---
layout: post
title: Building Computations 
tagline: Non-trivial results
category : work
draft : true
tags : [SymPy, Matrices]
---
{% include JB/setup %}

In my [last post]({{ BASE_PATH }}/work/2012/11/21/Computations/) I described a
base type that represented a computation as a directed acyclic graph.  In my
post on [preliminary results]({{ BASE_PATH }}/work/2012/11/10/GeneratingBLAS-PreliminaryResults/) I showed how we could write Fortran code for a simple expression.  In this post I want to show how unificaiton, rewrite rules, and manipulations on computations can compile computations from fairly complex matrix expressions.

Inputs
------

Lets begin with a complex expression and a set of assumptions

{% highlight python %}
    expr = (Y.I*Z*Y + b*Z*Y + c*W*W).I*Z*W
    assumptions = Q.symmetric(Y) & Q.positive_definite(Y) & Q.symmetric(X)
{% endhighlight %}

We also specify a list of conditional rewrite patterns.  A pattern has the
following form

{% highlight python %}
Source:     alpha*A*B
Target:     SYMM(alpha, A, B, S.Zero, B)
Wilds:      alpha, A, B
Condition:  Q.symmetric(A) | Q.symmetric(B))
{% endhighlight %}

This means that we convert the expression `alpha*A*B` into the computation `SYMM(alpha, A, B, S.Zero, B)` (a SYmmetric Matrix Multiply) for any `(alpha, A, B)` when either `A` is symmetric or `B` is symmetric.

Thanks to [unification]({{BASE_PATH}}/work/2012/11/01/Unification/) rewrite patterns are simple to make.  Someone who is familiar with BLAS/LAPACK but unfamiliar with compilers would be able to make many of these simply.

Expressions to Computations
---------------------------

Each pattern is turned into a function/rule that transforms an expression
into a computation.  We start with an identity computation

{% highlight python %}
    expr = (Y.I*Z*Y + b*Z*Y + c*W*W).I*Z*W
    assumptions = Q.symmetric(Y) & Q.positive_definite(Y) & Q.symmetric(X)
    identcomp = Identity(expr)
{% endhighlight %}

And we cycle our rules over the inputs.  Whenever we find a match we add a new atomic computation onto the composite one.  We use [branching strategies]({{BASE_PATH}}/work/2012/11/09/BranchingStrategies/) to orchestrate *how* these rules are applied.  This is in the last line of the `make_matrix_rule` function

{% highlight python %}
    def make_matrix_rule(patterns, assumptions):
        rules = [expr_to_comp_rule(src, target, wilds, cond, assumptions)
                 for src, target, wilds, cond in patterns]
        return exhaust(multiplex(*map(input_crunch, rules)))
{% endhighlight %}

We then apply this rule to our identity computation and pull off compiled results

{% highlight python %}
    rule = make_rule(patterns, assumptions)
    comp = next(rule(identcomp))
    comp.show()
{% endhighlight %}

Computations are able to print themselves in the [DOT Language](http://en.wikipedia.org/wiki/DOT_language) enabling simple visualization

![]({{ BASE_PATH }}/images/complex-matrix-computation.png)

Inplace Computations
--------------------

BLAS/LAPACK routines are *inplace*; they write their results to the memory locations of their inputs.  We have a separate system to deal with inplace computations. 

{% highlight python %}
    from sympy.computations.inplace import inplace_compile
    icomp = inplace_compile(comp)
    icomp.show()
{% endhighlight %}

![]({{ BASE_PATH }}/images/complex-matrix-computation-inplace.png)
