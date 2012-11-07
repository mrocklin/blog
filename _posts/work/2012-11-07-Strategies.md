---
layout: post
title: Strategies
tagline: Programming control flow
category : work 
tags : [SymPy]
---
{% include JB/setup %}

In [my last post](matthewrocklin.com/blog/work/2012/11/01/Unification/) I showed how unification and rewrite rules allow us to express *what* we want without specifying *how* to compute it.  As an example we were able to turn the mathematical identity `sin(x)**2 + cos(x)**2 -> 1` into a function with relatively simple code

{% highlight python %}
    # Transformation : sin(x)**2 + cos(x)**2 -> 1
    >>> pattern = patternify(sin(x)**2 + cos(x)**2, x)
    >>> sincos_to_one = rewriterule(pattern, 1)

    >>> sincos_to_one(sin(a+b)**2 + cos(a+b)**2).next()
    1
{% endhighlight %}

However we found that this function did not work deep within an expression tree

{% highlight python %}
    >>> list(sincos_to_one(2 + c**(sin(a+b)**2 + cos(a+b)**2))) # no matches
    []
{% endhighlight %}

`sincos_to_one` does not know *how* to traverse a tree.  It is pure logic and has no knowledge of control.  We define traverals separately using strategies.

*Short version*: we give you a higher order function, `top_down` which turns a
expression-wise function into a tree-wise function.  We provide a set of similar functions which can be composed to various effects.

* * * * 

A Toy Example
-------------

How do we express control programmatically? 

Traditional control flow is represented with constructs like `if`, `for`, `while`, `def`, `return`, `try`, etc....  These terms direct the flow of what computation occurs when.  Traditionally we mix control and logic.  Consider the following toy problem that reduces a number until it reaches a multiple of ten

{% highlight python %}
    def reduce_to_ten(x):
        """ Reduce a number to the next lowest multiple of ten 

        >>> reduce_ten(26)
        20
        """
        old = None
        while(old != x):
            if (x % 10 != 0):
                x -= 1
        return x
{% endhighlight %}

While the logic in this function is somewhat trivial 

{% highlight python %}
    if (x % 10 != 0):
        x -= 1
{% endhighlight %}

the control pattern is quite common in serious code 

{% highlight python %}
    while(old != expr):
        old = expr 
        expr = f(expr)
    return expr
{% endhighlight %}

It is the "Exhaustively apply this function until there is no effect" control pattern. It occurs often in general programming and very often in the SymPy sourcecode.  We separate this control pattern into a higher order function named `exhaust`

{% highlight python %}
    def exhaust(rule):
        """ Apply a rule repeatedly until it has no effect """
        def exhaustive_rl(expr):
            old = None
            while(expr != old):
                expr, old = rule(expr), expr 
            return expr 
        return exhaustive_rl
{% endhighlight %}

We show how to use this function to achieve the previous result. 

{% highlight python %}
    def dec_10(x):                          # Close to pure logic
        if (x % 10 != 0):   return x - 1
        else:               return x

    reduce_to_ten = exhaust(dec_10)
{% endhighlight %}
        
By factoring out the control strategy we achieve several benefits

1.  Code reuse of the `while(old != new)` control pattern 
2.  Exposure of logic - we can use the `dec_10` function in other contexts more easily. This version is more extensible.
3.  Programmability of control - the control pattern is now first class.  We can manipulate and compose it as we would manipulate or compose a variable or function.

Example - Debug
---------------

When debugging code we often want to see the before and after effects of running a function.  We often do something like the following
    
{% highlight python %}
    new = f(old)
    if new != old:
        print "Before: ", old 
        print "After:  ", new 
{% endhighlight %}

This common structure is encapsulated in the debug strategy

{% highlight python %}
    def debug(rule):
        """ Print out before and after expressions each time rule is used """
        def debug_rl(expr):
            result = rule(expr)
            if result != expr:
                print "Rule: ", rule.func_name
                print "In:   ", expr
                print "Out:  ", result
            return result
        return debug_rl
{% endhighlight %}

Because control is separated we can inject this easily into our function

{% highlight python %}
    >>> reduce_to_ten = exhaust(debug(dec_10))
    
    >>> reduce_to_ten(23)
    Rule:  dec_10
    In:    23
    Out:   22
    Rule:  dec_10
    In:    22
    Out:   21
    Rule:  dec_10
    In:    21
    Out:   20
    20
{% endhighlight %}

Traversals
----------

Finally we show off the use of a tree traversal strategy which applies a function at each node in an expression tree.  Here we use the `Basic` type to denote a tree of generic nodes.

{% highlight python %}
    def top_down(rule):
        """ Apply a rule down a tree running it on the top nodes first """
        def top_down_rl(expr):
            newexpr = rule(expr)
            if is_leaf(newexpr):
                return newexpr
            return new(type(newexpr), *map(top_down_rl, newexpr.args))
        return top_down_rl

    >>> reduce_to_ten_tree = top_down(exhaust(tryit(dec_10)))

    >>> expr = Basic(23, 35, Basic(10, 13), Basic(Basic(5)))
    >>> reduce_to_ten_tree(expr)
    Basic(20, 30, Basic(10, 10), Basic(Basic(0)))
{% endhighlight %}

Use in Practice
---------------

We have rewritten the canonicalization code in the Matrix Expression module to use these strategies.  There are a number of small functions to represent atomic logical transformations of expressions.  We call these rules.  Rules are functions from expressions to expressions

    rule :: expr -> expr

And there are a number of strategies like `exhaust` and `top_down` which transform rules and parameters into larger rules

    strategy :: parameters, rule -> rule

For example there are general rules like `flatten` that simplify nested expressions like 

`Add(1, 2, Add(3, 4)) -> Add(1, 2, 3, 4)`

{% highlight python %}
    def flatten(expr):
        """ Flatten T(a, b, T(c, d), T2(e)) to T(a, b, c, d, T2(e)) """
        cls = expr.__class__
        args = []
        for arg in expr.args:
            if arg.__class__ == cls:
                args.extend(arg.args)
            else:
                args.append(arg)
        return new(expr.__class__, *args)
{% endhighlight %}

We compose these general rules (e.g. 'flatten', 'unpack', 'sort', 'glom') with strategies to create large canonicalization functions 

{% highlight python %}
    rules = (rm_identity(lambda x: x == 0 or isinstance(x, ZeroMatrix)),
             unpack,
             flatten,
             glom(matrix_of, factor_of, combine),
             sort(str))

    canonicalize = exhaust(top_down(typed({MatAdd: do_one(*rules)})))
{% endhighlight %}

Going Farther
-------------

We use strategies to build large rules out of small rules.  Can we build large strategies out of small strategies? The `canonicalize` function above follows a common pattern "Apply a set of rules down a tree, repeat until they have no effect." This is built into the `canon` strategy.

{% highlight python %}
    def canon(*rules):
        """ Strategy for canonicalization """
        return exhaust(top_down(do_one(*rules)))
{% endhighlight %}

Previous Work
-------------

This implementation of strategies was inspired by the work in the language StrategoXT. Stratego is a language for control that takes these ideas much farther and implements them more cleanly.  It is a language where control structure are the primitives that can be built up, composed, and compiled down.  It is possible to express ideas like "dynamic programming" in this language.

References
----------

1.  Ralf Lämmel , Eelco Visser , Joost Visser, [*The Essence of Strategic Programming*](http://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=1&cad=rja&ved=0CDMQFjAA&url=http%3A%2F%2Fhomepages.cwi.nl%2F~ralf%2Feosp%2Fpaper.pdf&ei=bJuaUNWwNuOc2AWQtICYCA&usg=AFQjCNHG1lJTjP05tO1aElYQkXMYSmgNuw&sig2=EwanltC52lXaC4gU4OtVvA), 2002
2.  Eelco Visser, [*Program Transformation with Stratego/XT*](http://www.springerlink.com/content/my9we5tj86u2f59n/)
