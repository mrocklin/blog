---
layout: post
title:  SymPy -> Theano -- Matrix Expressions
tagline:  
draft: true
category : work 
tags : [SymPy, Theano]
---
{% include JB/setup %}

Introduction
------------

*This post uses some LaTeX.  You may want to read it on the original site.*

This is the last of a three part series connecting SymPy and Theano to transform mathematical expressions into efficient numeric code (see parts [1](http://matthewrocklin.com/blog/work/2013/03/19/SymPy-Theano-part-1/) and [2](http://localhost:4000/work/2013/03/28/SymPy-Theano-part-2/)).  We have seen that it is simple and computationally profitable to combine the best parts of both projects.

In this post we'll switch from computing scalar expressionss to computing matrix expressions.  We'll define the Kalman filter in SymPy and send it to Theano for code generation.  We'll then use SymPy to define a more performant blocked version of the same algorithm.


Kalman Filter
-------------

The [Kalman filter](http://en.wikipedia.org/wiki/Kalman_filter) is an algorithm to compute the Bayesian update of a normal random variable given a linear observation with normal noise.  It is commonly used when an uncertain quantity is updated with the results of noisy observations.  For example it is used in weather forecasting after weather stations report in with new measurements, aircraft control to automatically adjust for real-time turbulence, or even on your smartphone's GPS navigation.   It's everywhere, it's important, and it needs to be computed quickly and continuously.  It suits our needs today because it can be completely defined with a pair of matrix expressions.

{% highlight python %}
n       = 1000                          # Number of variables in our system/current state
k       = 500                           # Number of variables in the observation
mu      = MatrixSymbol('mu', n, 1)      # Mean of current state
Sigma   = MatrixSymbol('Sigma', n, n)   # Covariance of current state
H       = MatrixSymbol('H', k, n)       # A measurement operator on current state
R       = MatrixSymbol('R', k, k)       # Covariance of measurement noise
data    = MatrixSymbol('data', k, 1)    # Observed measurement data

newmu   = mu + Sigma*H.T * (R + H*Sigma*H.T).I * (H*mu - data)      # Updated mean
newSigma= Sigma - Sigma*H.T * (R + H*Sigma*H.T).I * H * Sigma       # Updated covariance

print latex(newmu)
print latex(newSigma)
{% endhighlight %}

$$ \Sigma H^T \left(H \Sigma H^T + R\right)^{-1} \left(-data + H \mu\right) + \mu $$
$$ - \Sigma H^T \left(H \Sigma H^T + R\right)^{-1} H \Sigma + \Sigma $$

Theano Execution
----------------

The objects above are for symbolic mathematics, not for numeric computation.  If we want a Python function to compute this expression we call on Theano

{% highlight python %}
inputs = [mu, Sigma, H, R, data]
outputs = [newmu, newSigma]

from sympy.printing.theanocode import theano_function

dtypes = {inp: 'float64' for inp in inputs}
f = theano_function(inputs, outputs, dtypes=dtypes)
{% endhighlight %}

Theano builds a Python function that calls down to a combination of low-level `C` code, `scipy` functions, and calls to the highly optimized `DGEMM` routine for matrix multiplication.  As input this function takes five numpy arrays corresponding to our five symbolic `inputs` and produces two numpy arrays corresponding to our two symbolic `outputs`.  [Recent work](https://github.com/sympy/sympy/pull/1965) allows *any* SymPy matrix expression to be translated to and run by Theano.

{% highlight python %}
import numpy
ninputs = [numpy.random.rand(*i.shape).astype('float64') for i in inputs]
noutputs = f(*inputs)
{% endhighlight %}

Blocked Execution
-----------------

These arrays are too large to fit comfortably in the fastest parts of the memory hierarchy.  As a result each sequential `C`, `scipy`, or `DGEMM` call needs to move big chunks of memory around while it computes.  After one operation completes the next operation moves around the same memory while it performs its task.  This repeated memory shuffling hurts performance.

A common approach to reduce memory shuffling is to cut the computation into smaller blocks.  We then perform as many computations as possible on a single block before moving on.  This is a standard technique in matrix multiplication.

{% highlight python %}
A, B, C, D, E, F, G, H = [MatrixSymbol(a, n, n) for a in 'ABCDEFGH']
X = BlockMatrix([[A, B],
                 [C, D]])
Y = BlockMatrix([[E, F],
                 [G, H]])
print latex(X*Y)
{% endhighlight %}

$$ \begin{bmatrix} A & B \\\\ C & D \end{bmatrix} 
   \begin{bmatrix} E & F \\\\ G & H \end{bmatrix}$$

{% highlight python %}
print latex(block_collapse(X*Y))
{% endhighlight %}

$$ \begin{bmatrix} A E + B G & A F + B H \\\\ 
                   C E + D G & C F + D H\end{bmatrix} $$

We are now able to focus on substantially smaller chunks of the array.  For example we can choose to keep `A` in local memory and perform all computations that involve `A`.  We will still need to shuffle some memory around (this is inevitable) but by organizing with blocks we're able to shuffle less.

This idea extends beyond matrix multiplication.  For example, SymPy knows how to block a matrix inverse

{% highlight python %}
print latex(block_collapse(X.I))
{% endhighlight %}

$$ \begin{bmatrix} 
\left(- B D^{-1} C + A\right)^{-1} & - A^{-1} B \left(- C A^{-1} B + D\right)^{-1} \\\\ 
- \left(- C A^{-1} B + D\right)^{-1} C A^{-1} & \left(- C A^{-1} B + D\right)^{-1}
\end{bmatrix} $$

High performance dense linear algebra libraries hard-code all of these tricks.  The call to the general matrix multiply routine `DGEMM` performs blocked matrix multiply within the call.  The call to the general matrix solve routine `DGESV` can perform blocked matrix solve.  Unfortunately these routines are unable to coordinate blocked computation *between* calls.

Fortunately, SymPy and Theano can.

SymPy can define and reduce the blocked matrix expressions using tricks like what are shown above.
{% highlight python %}
from sympy import blockcut, block_collapse
blocksizes = {
        Sigma: [(n/2, n/2), (n/2, n/2)],
        H:     [(k/2, k/2), (n/2, n/2)],
        R:     [(k/2, k/2), (k/2, k/2)],
        mu:    [(n/2, n/2), (1,)],
        data:  [(k/2, k/2), (1,)]
        }
blockinputs = [blockcut(i, *blocksizes[i]) for i in inputs]
blockoutputs = [o.subs(dict(zip(inputs, blockinputs))) for o in outputs]
collapsed_outputs = map(block_collapse, blockoutputs)

fblocked = theano_function(inputs, collapsed_outputs, dtypes=dtypes)
{% endhighlight %}

Theano is then able to coordinate this computation and compile it to low-level code.  At this stage the expresssions/computations are fairly complex and difficult to present.  Here is an image of the computation (click for zoomable PDF).

[![]({{ BASE_PATH }}/images/fblocked-small.png)]({{ BASE_PATH }}/images/fblocked.pdf)

Results
-------

Lets time the difference

{% highlight python %}
>>> timeit f(*ninputs)
1 loops, best of 3: 2.82 s per loop

>>> timeit fblocked(*ninputs)
1 loops, best of 3: 2.07 s per loop
{% endhighlight %}

That's a 25% performance increase from just a few lines of high-level code.

Blocked matrix multiply and blocked solve routines have long been established as *a good idea*.  High level mathematical and array programming libraries like SymPy and Theano allow us to extend this good idea to arbitrary array computations.


Analysis
--------

### Good Things

First, lets note that I'm not introducing a new library for dense linear algebra.  Instead I'm noting that existing general purpose high-level tools can be composed to that effect.

Second, lets acknoledge that we could take this further.  For example Theano seemlessly handles GPU interactions.  I could take this same code to a GPU accelerated machine and my code would just run faster without any action on my part. 

### Bad Things

However, there are some drawbacks.

Frequent readers of my blog might recall a [previous post about the Kalman filter](http://matthewrocklin.com/blog/work/2012/11/24/Kalman-Filter/).  In it I showed how we could use SymPy's inference engine to select appropriate BLAS/LAPACK calls.  For example we could infer that because $ H \Sigma H^T + R $ was symmetric positive definite we could use the substantially more efficient `POSV` routine for matrix solve rather than `GESV` (`POSV` uses Cholesky rather than straight LU).  Theano doesn't support the specialized BLAS/LAPACK routines though, so we are unable to take advantage of this benefit.  The lower-level interface (Theano) is not sufficiently rich to use all information captured in the higher-level (SymPy) representation.

Also, I've noticed that the blocked version of this computation experiences some significant roundoff errors (on the order of `1e-3`).  I'm in the process of tracking this down.  The problem must occur somewhere in the following tool-chain 

    SymPy -> Blocking -> Theano -> SciPy -> C routines -> BLAS

Debugging in this context can be wonderful if all elements are well unit-tested.  If they're not (they're not) then tracking down errors like this requires an unfortunate breadth of expertise.


References
----------

Scripts 

*   [Kalman example]({{ BASE_PATH }}/scripts/kalman.py)
*   [Block Matrix example]({{ BASE_PATH }}/scripts/blocks.py)
*   [Block Kalman]({{ BASE_PATH }}/scripts/kalman_blocked.py)
