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

In my last two posts [1](http://matthewrocklin.com/blog/work/2013/03/19/SymPy-Theano-part-1/) [2]() I showed how SymPy and Theano can interoperate to generate efficient code.  Both examples transformed a set of complex scalar expressions into executable low-level code.  We saw that combining the best parts of both projects is both simple and computationally profitable.

In this post we'll switch from computing scalar expressionss to computing matrix expressions.  We'll build the Kalman filter in SymPy and send it to Theano for computation.  We'll then use SymPy to build a more performant blocked version of the same algorithm.

Kalman Filter
-------------

The [Kalman filter](http://en.wikipedia.org/wiki/Kalman_filter) is an algorithm to compute the Bayesian update of a normal random variable given a linear observation with normal noise.  It is commonly used anytime an uncertain quantity is updated with measurements.  For example it is used in weather forecasting after weather stations report in with new measurements, aircraft control to automatically adjust for turbulence, or even on your smartphone's GPS navigation.   It's everywhere, it's important, and it needs to be computed quickly and continuously.  I particularly like it because it can be represented purely as a matrix expression.

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

Theano builds a Python function calling on a combination of low-level `C` code, `scipy` functions, and calls to the optimized `DGEMM` routine.  As input this function takes five numpy arrays corresponding to our five symbolic `inputs` and produces two numpy arrays corresponding to our symbolic `outputs`.  Recent work allows *any* SymPy matrix expression to be translated to and run by Theano.

{% highlight python %}
import numpy
ninputs = [numpy.random.rand(*i.shape).astype('float64') for i in inputs]
noutputs = f(*inputs)
{% endhighlight %}

Blocked Execution
-----------------

These arrays are too large to fit comfortably in the fastest parts of the memory hierarchy.  As a result each sequential `C`, `scipy`, or `DGEMM` call needs to move big chunks of memory around while it computes.  After it completes the next operation moves around that same memory while it performs its task.  This repeated memory shuffling hurts performance.  

A common solution is to cut the computation into smaller blocks, that way we can perform multiple computations on the same memory before moving on.  This is a standard technique in matrix multiplication.

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

High performance dense linear algebra libraries have all of these tricks hardcoded in.  The call to the general matrix multiply routine `DGEMM` performs blocked matrix multiply within the call.  The call to the general matrix solve routine `DGESV` can perform blocked matrix solve.  Unfortunately they are unable to coordinate blocks *between* calls. 

Fortunately, SymPy can.

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

At this stage the expresssions/computations are fairly complex.  Here is an
image (click for vector graphic)

[![]({{ BASE_PATH }}/images/fblocked.png)]({{ BASE_PATH }}/images/fblocked.pdf)

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


Conclusion
----------

Blocked matrix multiply and blocked solve routines have long been established as *a good idea*.  High level mathematical and array programming libraries like SymPy and Theano allow us to extend this good idea to arbitrary array computations.


References
----------

*   [Kalman example]({{ BASE_PATH }}/scripts/kalman.py)
*   [Block Matrix example]({{ BASE_PATH }}/scripts/blocks.py)
*   [Block Kalman]({{ BASE_PATH }}/scripts/kalman_blocked.py)
