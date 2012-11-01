---
layout: post
title: Unification in SymPy
tagline: Enabling logical programming in Python
category : work 
tags : [SymPy, Matrices]
---
{% include JB/setup %}

Unification is a way to ask questions by matching against patterns. It is a powerful form of pattern matching found in logical programming languages like Prolog, Maude, and Datalog. It is the computational backbone behind the logical programming paradigm and is now in SymPy (in a pull request).

Here is a simple example. Imagine that you want to find the name of the MatrixSymbol within the Transpose in the following expression (i.e. we're looking for the string `'X'`)

{% highlight python %}


    >>> X = MatrixSymbol('X', 3, 3)
    >>> Y = MatrixSymbol('Y', 3, 3)
    >>> expr = Transpose(X) + Y

{% endhighlight %}

Traditionally we could solve this toy problem with a simple function

{% highlight python %}

    def name_of_symbol_in_transpose_in_add(expr):
        assert isinstance(expr, MatAdd)
        for arg in expr.args:
            if isinstance(arg, Transpose) and isinstance(arg.arg, MatrixSymbol):
                return arg.arg.name
        raise ValueError("No Transpose Found")

{% endhighlight %}

We solve this task with unification by setting up a pattern and then unifying that pattern against a target expression

{% highlight python %}

    >>> A = MatrixSymbol('name', n, m)
    >>> B = MatrixSymbol('B', m, n)
    # Look for an expression tree like A.T + B
    # Treat the leaves 'name', n, m, B as Wilds
    >>> pattern = patternify(Transpose(A) + B, 'name', n, m, B)

    >>> unify(pattern, expr).next()
    {name: X, m: 3, n: 3, B: Y}

{% endhighlight %}

We get back a dictionary with the mapping and see that `'name'` gets mapped to the string `'X'`. Is this better or worse than the straight Python solution? Given the relative number of users between Python and Prolog it's a safe bet that the style of Python programs have some significant advantages over the logical programming paradigm. Still, this idea has some value in some applications.

Unification allows a clean separation between *what we're looking for* and *how we find it*. In the python solution the mathematical definition of what we want is spread among a few lines and is buried inside of control flow. 

    assert isinstance(expr, MatAdd)
    for arg in expr.args:
        if isinstance(arg, Transpose) and isinstance(arg.arg, MatrixSymbol):
            return arg.arg.name

In the unification solution the line 

    pattern = patternify(Transpose(A) + B, 'name', n, m, B)

expresses exactly *what* we're looking for and gives no information on *how* it should be found. The how is wrapped up in the call to `unify`

    unify(pattern, expr).next()

This separation of the *what* and *how* is what excites me about declarative programming. I think that this separation is useful when mathematical and algorithmic programmers need to work together to solve a large problem. This is often the case in scientific computing. Mathematical programmers think about *what* should be done while algorithmic programmers think about *how* it can be efficiently computed. Declarative techniques like unification enables these two groups to work independently.


References
----------

