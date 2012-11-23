---
layout: post
title: Computing the Kalman Filter
tagline: connecting the pieces
category : work
draft: true
tags : [SymPy, Matrices, Uncertainty]
---
{% include JB/setup %}

The [Kalman Filter](http://en.wikipedia.org/wiki/Kalman_filter) is an algorithm to update probability distributions with new observations made under noisy conditions.  It is used in everything from smartphone GPS navigation systems to large scale climate simulations.  It is implemented in hardware ranging from embedded devices to super-computers.  It is important and widely used.

Two years ago I wrote two blogposts about the Kalman filter, one on [the univariate case](http://sympystats.wordpress.com/2011/07/02/a-lesson-in-data-assimilation-using-sympy/) and one on [the multivariate case](http://sympystats.wordpress.com/2011/07/19/multivariate-normal-random-variables/).  At the time I was working on `sympy.stats`, a module that enabled uncertainty modeling through the introduction of a random variables into the SymPy language.

SymPy stats was designed with atomicity in mind.  It tried to be as small and thin a layer as possible.  

*   It turned queries on continuous random expressions into integral expressions and then stopped.  
*   It turned queries on discrete random expressions into iterators and sums and then stopped.  
*   It also turned queries on multivariate normal random expressions into matrix expressions and then stopped.  

The goal was to turn a specialized problem (uncertainty quantification) into a general one (integrals, sums, matrix expressions) under the assumption that tools are much richer to solve the general problem than the specific one.  

The first blogpost on the univariate kalman filter produced integral expressions that were then solved by SymPy's integration routines.  The second blogpost on the multivariate Kalman filter generated the following matrix expressions

$$\mu' = \Sigma H^T H \Sigma H^T + R^{-1} \left(-1 data + H \mu\right) + \mu$$
$$\Sigma' = \left(-\Sigma H^T H \Sigma H^T + R^{-1} H + \mathbb{I}\right) \Sigma$$

That blogpost finished with this result, claiming that the job of `sympy.stats` was finished and that any of the popular numerical linear algebra packages could pick up from that point. 

Today, we pick up from where we left off. 

{% highlight python %}
# kalman.py
from sympy.matrices.expressions import MatrixSymbol, Identity
from sympy import Symbol, Q

n, k    = Symbol('n'), Symbol('k')
mu      = MatrixSymbol('mu', n, 1)
Sigma   = MatrixSymbol('Sigma', n, n)
H       = MatrixSymbol('H', k, n)
R       = MatrixSymbol('R', k, k)
data    = MatrixSymbol('data', k, 1)
I       = Identity(n)

newmu       = mu + Sigma*H.T * (R + H*Sigma*H.T).I * (H*mu - data)
newSigma    = (I - Sigma*H.T * (R + H*Sigma*H.T).I * H) * Sigma

assumptions = (Q.positive_definite(Sigma) & Q.symmetric(Sigma) &
               Q.positive_definite(R) & Q.symmetric(R))
{% endhighlight %}

We convert these matrix expressions into a computation

{% highlight python %}
# kalman_computation.py
from kalman import newmu, newSigma, assumptions
from sympy.computations.matrices.compile import make_rule, patterns
from sympy.computations.core import Identity

ident = Identity(newmu, newSigma)
rule = make_rule(patterns, assumptions)
mathcomp = next(rule(ident))
mathcomp.show()

{% endhighlight %}

![]({{ BASE_PATH }}/images/kalman-math-1.png)

By combining `sympy.stats`, `sympy.matrices.expressions` and `sympy.computations` we can seemlessly compile from the high level statistical expressions of `sympy.stats` to matrix expressions to the DAGs of `sympy.computations` and even down to Fortran code.  If we add a traditional Fortran compiler we can build working binaries directly from `sympy.stats`.

Features and Flaws in the Kalman graph
-------------------------

Lets investigate the Kalman computation.  It contains a few notable features.

First, unlike previous examples it has two outputs, `newmu` and `newSigma`.  These two have large common subexpressions like `H*Sigma*H' + R`.  You can see that these were computed once and shared.

Second, there is an unfortunately common motif.  This was taken from the upper right of the DAG.  This `GE/SYMM -> AXPY` motif occurs four times in the graph. 

![]({{ BASE_PATH }}/images/kalman-math-gemm-axpy-motif.png)

`GEMM/SYMM` are matrix multiplies and are used here to break down expressions like `alpha*A*B`.  `AXPY` is a matrix addition and is used to break down expressions like `alpha*A + B`.  They are both used properly here.

This motif is unforunate because `GEMM` is also capable of breaking down a larger expression like `alpha*A*B + beta*C`, doing a fused matrix multiply and add all in one pass.   Because of this the `AXPY`s would be unnecessary if our larger `GE/SYMM` patterns had matched correctly.  

Canonicalization
----------------

The `alpha*A*B + beta*C` patterns did not match here for a silly reason, there wasn't anything to match for the scalars `alpha` and `beta`.  Instead the patterns were like `A*B + C`.  One solution to this problem is to make more patterns with all possibilities.  Alternatively we could change how we canonicalize `MatMul` objects so that they always have a scalar coefficient, even if it defaults to 1.

We don't want to change `MatMul` to behave like this throughout all of SymPy though; the extra 1 is usually unwanted.  This is a case where there are multiple correct definitions of canonical.  Fortunately `MatMul` is written with this eventuality in mind.

Links
-----

1.  [A Lesson in Data Assimilation using SymPy](http://sympystats.wordpress.com/2011/07/02/a-lesson-in-data-assimilation-using-sympy/)
2.  [Multivariate Normal Random Variables](http://sympystats.wordpress.com/2011/07/19/multivariate-normal-random-variables/)
3.  Source for this post: [kalman.py]({{BASE_PATH}}/scripts/kalman.py), [kalman_comp.py]({{BASE_PATH}}/scripts/kalman_comp.py)
