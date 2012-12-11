---
layout: post
title: Statistical Simplification
tagline: example of multi-compilation
category : work 
tags : [SymPy, stats]
---
{% include JB/setup %}

[Lawrence Leemis](), a statistician at Williams and Mary, recently published a wonderful interactive visualization on the reduction relationships of statistical distributions. (found via [John Cook's blog](http://www.johndcook.com/blog/))

[![](http://www.johndcook.com/leemis.png)](http://www.math.wm.edu/~leemis/chart/UDR/UDR.html)

This excites me because it touches on one of my favorite topics

*How do we reusably encode expert knowledge into computational systems?*

Challenge
---------

Correct use of mathematical information can accelerate important computations by several orders of magnitude.  Unfortunately the people who know the mathematics are not always the ones doing the computation.  This results in substantial waste.

How do we integrate expert mathematical knowledge everywhere?  One solution is to collaborate more.  This is a good idea but does not scale well.  As problems become more complex it is more difficult to find all of the necessary experts.  Also, smaller projects may not be able to engage multiple experts.  Finally, collaboration rarely results in reusable infrastructure.  Statistical chemistry projects usually aren't helpful for statistical biology problems.

A Solution
----------

I prefer to write each expert's knowledge into a single project and then connect many such projects into a multi-stage compiler.  At each each stage we simplify the expression with the knowledge relevant at that stage.  For each connection between stages we create a transformation.  Ideally the conceptual distance between connected stages is small.

This isn't clearly the right solution.  It is difficult to chain many small projects together and end up with efficient code.  You need to find the right sequence of intermediate layers that are able to communicate mathematical information down to the lowest-level of computational code.

Relevance to SymPy.stats
------------------------

SymPy.stats endeavors to be a transformation in such a toolchain.  It converts stochastic expressions into integral expressions.

The surrounding infrastructure looks like this

![]({{ BASE_PATH }}/images/stats-simp.png)

Symbolic SymPy expressions are imbued with random variables causing stochastic expressions.  These are transformed into integral expressions which can then be transformed into baser expressions through a variety of methods, either numeric or again symbolic. 

Each stage within this pipeline presents us with an opportunity to simplify the expression.  For example at the input and output SymPy Expr layer we might make trigonometric and algebraic simplifications like the following

    sin(x)**2 + cos(x)**2 -> 1 
    X + X -> 2*X

Notice that there is no such simplification self-loop at the `Stochastic Expression` node.  This is where the information in Leemis' chart would fit in perfectly.

### A Problem

Currently sympy.stats does not simplify stochastic expressions with expert knowledge.  The information in the Loomis' chart is not in sympy.stats.  This causes some fairly embarassing failures 

    In [1]: from sympy.stats import *

    In [2]: X = Normal('X', 0, 1)

    In [3]: density(X**2)  
    Out[3]: 
    << failure: unevaluated integral >>

`sympy.stats` passed a difficult integral to the integration routines, hoping that they could work with it.  Unfortunately, due to a non-linear argument in a delta function, they failed.

However any statistician could tell you that the expression `X**2` has a Chi Squared distribution which has a clear and well understood form.  SymPy stats is obviously a poor statistician.  This relation is well known and occurs frequently.

### A Solution

Currently there are no simplifications based on expert statistical knowledge.  This is a missing piece.  The knowledge in Leemis's chart could be written down as a knowledgebase of known transformations.  Transformations like the following could solve our problem.

    Normal(0, 1) -> StandardNormal()
    StandardNormal()**2 -> ChiSquare(1)
    StandardNormal()**2 + ChiSquare(n) -> ChiSquare(n+1)

Leemis's chart is written declaratively, highlighting transformations possible under certain conditions.
