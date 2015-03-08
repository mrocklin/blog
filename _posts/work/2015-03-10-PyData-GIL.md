---
layout: post
title: PyData and the GIL
category : work
draft: true
tags : [scipy, Python, Programming]
---
{% include JB/setup %}

*This work is supported by [Continuum Analytics](http://continuum.io)
and the [XDATA Program](http://www.darpa.mil/our_work/i2o/programs/xdata.aspx)
as part of the [Blaze Project](http://blaze.pydata.org/docs/dev/index.html)*

**tl;dr** Many PyData projects release the GIL.  Multi-core parallelism is
alive and well.

Introduction
------------

*Machines grow more cores every year. Can the PyData ecosystem leverage this
power? is the GIL a problem?*

The Global Interpreter Lock (GIL) stops threads from manipulating
Python objects in parallel.  This cripples Pure Python shared-memory
parallelism.  This sounds like a big deal but it doesn't really affect the
PyData stack (NumPy/Pandas/SciKit *)

Q: *Given the growth of shared-memory parallelism, should the PyData ecosystem
    be concerned about the GIL?*

A: *No, we should be very excited about this growth*

Many PyData projects don't spend much time in Python code.  They spend
99% of their time in C/Fortran/Cython code.  This code can release the GIL.

The following projects release the GIL:

*  NumPy
*  SciPy
*  Numba in `nopython` mode
*  SciKit Learn
*  *if you add more in the comments then I will post them here*

Additionally any project that depends on these gains the same benefit.


Quick Example with dask.array
-----------------------------

As a quick example, we compute a large random dot product with `dask.array`.

{% highlight Python %}
In [1]: import dask.array as da

In [2]: x = da.random.random((10000, 10000), blockshape=(1000, 1000))

In [3]: float(x.dot(x.T).sum())
Out[3]: 250026827523.19141
{% endhighlight %}

<img src="{{ BASE_PATH }}/images/350percent-cpu-usage-alpha.png"
     alt="Full resource utilization with Python">

*Technical note, my BLAS is set to use on thread only, the parallelism in the
above example is strictly due to multiple Python worker threads, and not any
parallelism in the underlying native code.*

Note the 361.0% CPU utilization in the `ipython` process.

Because the PyData stack is fundamentally based on native compiled code
multiple Python threads can crunch data in parallel without worrying about the
GIL.  The GIL does not have to affect us in a significant way.


That's not true, the GIL hurts Python in the following cases
------------------------------------------------------------

### Text

We don't have a good C/Fortran/Cython solution for text. When given a
pile-of-text-files we often switch from threads to processes and use the
`multiprocessing` module.  This limits inter-worker communication but this is
rarely an issue for this kind of embarrassingly parallel work.

The multiprocessing workflow is fairly simple.  I've written about this in the
[toolz docs](http://toolz.readthedocs.org/en/latest/parallelism.html) and in a
blogpost about
[dask.bag](http://matthewrocklin.com/blog/work/2015/02/17/Towards-OOC-Bag/).

### Pandas

Pandas does not yet release the GIL in computationally intensive code.
It probably could though.  This requires momentum from the community and some
grunt-work by some of the Pandas devs.  I have a small issue
[here](https://github.com/pydata/pandas/issues/8882).


PyData <3 Shared Memory Parallelism
-----------------------------------

If you're looking for more speed in compute-bound applications then consider
threading or heavy workstation machines.  I personally find this approach to be
more convenient than spinning up a cluster.
