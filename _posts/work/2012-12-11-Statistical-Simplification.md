---
layout: post
title: Statistical Simplification
tagline: an example of multi-compilation
category : work 
draft: true
tags : [SymPy, stats]
---
{% include JB/setup %}

[Lawrence Leemis](), a statistician at Williams and Mary, recently published a wonderful interactive visualization on the reduction relationships of statistical distributions. (found via [John Cook's blog](http://www.johndcook.com/blog/2012/12/10/extended-distribution-chart/))

[![](http://www.johndcook.com/leemis.png)](http://www.math.wm.edu/~leemis/chart/UDR/UDR.html)

This excites me because it touches on one of my favorite topics

*How do we reusably encode expert knowledge into computational systems?*

The Big Challenge
-----------------

Correct use of mathematical information can accelerate important computations by several orders of magnitude.  Unfortunately the people who know the mathematics are not always the ones doing the computation.  This results in substantial waste.

How do we integrate expert mathematical knowledge everywhere?  One solution is to collaborate more.  This is a good idea but does not scale well.  As problems become more complex it is more difficult to find all of the necessary experts.  Also, smaller projects may not be able to engage multiple experts.  Finally, collaboration rarely results in reusable infrastructure.  Statistical chemistry projects usually aren't helpful for statistical biology problems.

One Solution - Multi-Stage Compilation
--------------------------------------

We could write each expert's knowledge into a single project and then connect many such projects into a multi-stage compiler.  At each each stage we simplify the expression with the knowledge relevant at that stage.  We must create a transformation between each pair of connecting stages.  Ideally the conceptual distance between connected stages is small and so these transformations are easy.

This isn't clearly the right solution.  It is difficult to chain many small projects together and end up with efficient code.  You need to find the right sequence of intermediate layers that are able to communicate mathematical information down to the lowest-level of computational code.

Relevance to SymPy.stats
------------------------

SymPy.stats endeavors to be a transformation in such a toolchain.  It converts stochastic expressions into integral expressions.

The surrounding infrastructure looks like this

![]({{ BASE_PATH }}/images/stats-simp.png)

When SymPy expressions are imbued with random variables they form stochastic expressions.  Sympy.stats transforms these into integral expressions which are then transformed into baser expressions through a variety of methods, either numeric or again symbolic. 

Each stage within this pipeline presents us with the opportunity to simplify the expression with knowledge relevant to that stage.  For example at the input and output SymPy Expr layers we make trigonometric and algebraic simplifications like the following

    sin(x)**2 + cos(x)**2 -> 1 
    X + X -> 2*X

Notice that there is no such simplification self-loop at the `Stochastic Expr` node.  This is where the information in Leemis' chart would fit.

### A Failing of sympy.stats

Currently sympy.stats does not simplify stochastic expressions with expert knowledge.  The information in the Leemis' chart is not encoded.  This causes some fairly embarassing failures like the following

{% highlight python %}
In [1]: from sympy.stats import *

In [2]: X = Normal('X', 0, 1)  # A standard normal random variable

In [3]: density(X**2)  
Out[3]: 
<< failure: unevaluated integral >>
{% endhighlight %}

Any statistician could tell you that the expression `X**2` has a Chi Squared distribution which has a simple and well understood density.  This relation is commonly known and commonly occuring in practice.  SymPy stats is evidently a poor statistician.

Instead sympy.stats blindly takes the expression `density(X**2)` and converts it directly into an integral.  The resulting integral is difficult and stumps the integration routines.  In this case knowing basic statistics would have turned an impossible problem into a trivial one.

### Future work

We should encode relations on distributions into SymPy. The knowledge in Leemis's chart could be written down as a knowledgebase of known transformations.  Transformations like the following could solve our immediate problem.

{% highlight python %}
Normal(0, 1) -> StandardNormal()
StandardNormal()**2 -> ChiSquared(1)
StandardNormal()**2 + ChiSquared(n) -> ChiSquared(n+1)
{% endhighlight %}

Leemis's chart is written declaratively, highlighting logical transformations possible under certain conditions.  The new modules on 
[unification]({{ BASE_PATH }}/work/2012/11/01/Unification/)
and 
[strategies]({{ BASE_PATH }}/work/2012/11/07/Strategies/)
should provide all of the necessary infrastructure to translate Leemis' chart to functioning code.  Writing a minimal simpliication scheme might be as simple as 

{% highlight python %}
#    rewriterule(from-pattern, to-pattern, wilds)
p1 = rewriterule(Normal(name, 0, 1), StandardNormal(name), wilds=(name,))
p2 = rewriterule(StandardNormal(name)**2, ChiSquared(name, 1), wilds=(name,))
p3 = rewriterule(StandardNormal(name)**2 + ChiSquared(name, n), 
                 ChiSquared(name, n+1), wilds=(name, n))

statsimp = exhaust(bottom_up(multiplex(p1, p2, p3)))
{% endhighlight %}

But that's wishful thinking.  If anyone is interested in this I'd be happy to help out.  This is the sort of project that really excites me but that I can't currently justify time-wise.
