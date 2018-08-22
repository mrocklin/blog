---
layout: post
title: Unification in SymPy
tagline: Enabling logical programming in Python
category : work
tags : [SymPy, Matrices]
theme: twitter
---
{% include JB/setup %}

Unification is a way to ask questions by matching expressions against patterns. It is a powerful form of pattern matching found in logical programming languages like Prolog, Maude, and Datalog. It is the computational backbone behind the logical programming paradigm and is now a part of SymPy (in a pull request).

Consider the following example. Imagine that you want to find the name of the MatrixSymbol within the Transpose in the following expression (i.e. we're looking for the string `'X'`)

{% highlight python %}

>>> X = MatrixSymbol('X', 3, 3)
>>> Y = MatrixSymbol('Y', 3, 3)
>>> expr = Transpose(X) + Y

{% endhighlight %}

Traditionally we could solve this toy problem with a simple function

{% highlight python %}

def name_of_symbol_in_transpose_in_add(matadd):
    for arg in matadd.args:
        if isinstance(arg, Transpose) and isinstance(arg.arg, MatrixSymbol):
            return arg.arg.name

{% endhighlight %}

We solve this task with unification by setting up a pattern and then unifying that pattern against a target expression

{% highlight python %}

>>> A = MatrixSymbol('name', n, m)
>>> B = MatrixSymbol('B', m, n)
# Look for an expression tree like A.T + B
# Treat the leaves 'name', n, m, B as Wilds
>>> pattern = Transpose(A) + B
>>> wilds = 'name', n, m, B

>>> unify(pattern, expr, wilds=wilds).next()
{'name': 'X', m: 3, n: 3, B: Y}

{% endhighlight %}

We get back a matching for each of the wildcards (name, n, m, B) and see that `'name'` was matched to the string `'X'`. Is this better or worse than the straight Python solution? Given the relative number of users between Python and Prolog it's a safe bet that the style of Python programs have some significant advantages over the logical programming paradigm. Why would we program in this strange way?

Unification allows a clean separation between *what we're looking for* and *how we find it*. In the Python solution the mathematical definition of what we want is spread among a few lines and is buried inside of control flow.

{% highlight python %}
for arg in matadd.args:
    if isinstance(arg, Transpose) and isinstance(arg.arg, MatrixSymbol):
        return arg.arg.name
{% endhighlight %}

In the unification solution the lines

{% highlight python %}
pattern = Transpose(A) + B
wilds = 'name', n, m, B
{% endhighlight %}

expresse exactly *what* we're looking for and gives no information on *how* it should be found. The how is wrapped up in the call to `unify`

{% highlight python %}
unify(pattern, expr, wilds=wilds).next()
{% endhighlight %}

This separation of the *what* and *how* is what excites me about declarative programming. I think that this separation is useful when mathematical and algorithmic programmers need to work together to solve a large problem. This is often the case in scientific computing. Mathematical programmers think about *what* should be done while algorithmic programmers think about *how* it can be efficiently computed. Declarative techniques like unification enables these two groups to work independently.

Multiple Matches
----------------

Lets see how unify works on a slightly more interesting expression

{% highlight python %}
>>> expr = Transpose(X) + Transpose(Y)
>>> unify(pattern, expr)
<generator object unify at 0x548cb90>
{% endhighlight %}

In this situation because both matrices `X` and `Y` are inside transposes our pattern to match "the name of a symbol in a transpose" could equally well return the strings `'X'` or `'Y'`. The unification algorithm will give us both of these options

{% highlight python %}
>>> for match in unify(pattern, expr):
...    print match
{'name': 'Y', m: 3, n: 3, B: 'X'}
{'name': 'X', m: 3, n: 3, B: 'Y'}
{% endhighlight %}

Because expr is commutative we can match `{A: Transpose(X), B: Transpose(Y)}` or `{A: Transpose(Y), B: Transpose(X)}` with equal validity. Instead of choosing one `unify`, returns an iterable of all possible matches.

Combinatorial Blowup
--------------------

In how many ways can we match the following pattern

    w + x + y + z

to the following expression?

    a + b + c + d + e + f

This is a variant on the standard "N balls in K bins" problem often given in a discrete math course. The answer is "quite a few." How can we avoid this combinatorial blowup?

`unify` produces matches lazily. It returns a Python generator which yields results only as you ask for them. You can ask for just one match (a common case) very quickly.

The bigger answer is that if you aren't satisfied with this and want a better/stronger/faster way to find your desired match you could always *rewrite unify*. The `unify` function is all about the *how* and is disconnected from the *what*. Algorithmic programmers can tweak unify without disrupting the mathematical code.

Rewrites
--------

Unification is commonly used in term rewriting systems. Here is an example

{% highlight python %}
>>> sincos_to_one = rewriterule(sin(x)**2 + cos(x)**2, 1, wilds=[x])
>>> sincos_to_one(sin(a+b)**2 + cos(a+b)**2).next()
1
{% endhighlight %}

We were able to turn a mathematical identity `sin(x)**2 + cos(x)**2 => 1` into a function very simply using unification. However unification only does exact pattern matching so we can only find the `sin(x)**2 + cos(x)**2` pattern if that pattern is at the top node in the tree. As a result we're not able to apply this simplification within a larger expression tree


{% highlight python %}
>>> list(sincos_to_one(2 + c**(sin(a+b)**2 + cos(a+b)**2))) # no matches
[]
{% endhighlight %}

I will leave the solution of this problem to a future post. Instead, I want to describe why I'm working on all of this.

Matrix Computations
-------------------

[My last post](http://matthewrocklin.com/blog/work/2012/10/29/Matrix-Computations/) was about translating Matrix Expressions into high-performance Fortran Code. I ended this post with the following problem:


* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *

*So how can we transform a matrix expression like*

{% highlight python %}
(alpha*A*B).I * x
{% endhighlight %}

...

*Into a graph of `BLAS` calls like one of the following?*

{% highlight python %}
DGEMM(alpha, A, B, 0, B) -> DTRSV(alpha*A*B, x)
DTRMM(alpha, A, B)       -> DTRSV(alpha*A*B, x)
{% endhighlight %}

* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *

This problem can be partially solved by unification and rewrite rules. Each `BLAS` operation is described by a class

{% highlight python %}
class MM(BLAS):
    """ Matrix Multiply """
    _inputs   = (alpha, A, B, beta, C)
    _outputs  = (alpha*A*B + beta*C,)
{% endhighlight %}

The `_outputs` and `_inputs` fields mathematically define when `MM` is appropriate. This is all we need to make a transformation

{% highlight python %}
source = MM._outputs[0]
target = MM(*MM._inputs)
wilds  = MM._inputs
rewriterule(source, target, wilds)
{% endhighlight %}

Unification allows us to describe `BLAS` mathematically without thinking about
how each individual operation will be detected in an expression. The control
flow and the math are completely separated allowing us to think hard about each
problem in isolation.

References
----------

I learned a great deal from the following sources

*   [Artificial Intelligence: A Modern Approach](http://aima.cs.berkeley.edu/) by Stuart Russel and Peter Norvig (Particularly section 9.2 in the second edition)
*   [StackOverflow - Algorithms for Unification of list-based trees](http://stackoverflow.com/questions/13092092/algorithms-for-unification-of-list-based-trees)
*   [StackOverflow - Partition N items into K bins in Python lazily](http://stackoverflow.com/questions/13131491/partition-n-items-into-k-bins-in-python-lazily) (Special thanks to [Chris Smith](https://github.com/smichr) who provided the best answer)
*   [Logic Programming](http://en.wikipedia.org/wiki/Logic_programming)
*   [Term Rewriting](http://en.wikipedia.org/wiki/Term_rewriting)
*   [My favorite Prolog tutorial](http://www.learnprolognow.org/)
*   [SymPy E-mail thread on this topic](http://goo.gl/ZqVHJ)
*   [Pull Request](https://github.com/sympy/sympy/pull/1633)
