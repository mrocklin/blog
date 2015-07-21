---
layout: post
title: Custom Parallel Workflows
tagline: dask graphs <3 for loops
category : work
draft: true
tags : [scipy, Python, Programming, dask, blaze]
---
{% include JB/setup %}

*This work is supported by [Continuum Analytics](http://continuum.io)
and the [XDATA Program](http://www.darpa.mil/our_work/i2o/programs/xdata.aspx)
as part of the [Blaze Project](http://blaze.pydata.org/docs/dev/index.html)*

**tl;dr: We motivate the expansion of parallel programming beyond big
collections.  We discuss programmability of dask graph.**


Recent Parallel Work Focuses on Big Collections
-----------------------------------------------

Parallel databases, Spark, and the Dask collections all provide some large
distributed collection and handle parallelism for you.  You put your data into
this collection, restrict yourself to a small set of operations like `map` or
`groupby` and they handle the parallel processing.  There are now a dozen
projects promising big and friendly Pandas clones.

This is good.  These collections provide usable, high-level interfaces for a
large class of problems.


Custom Workloads
----------------

However, many workloads are too complex for these collections.  Workloads might
be complex either because they come from sophisticated algorithms
(as we saw in a [recent post on SVD]({{ BASE_PATH }}/work/2015/06/26/Complex-Graphs/)) or because they come from the real world,
where problems tend to be messy.

In these cases I tend to see people do two things

1.  Fall back to `multiprocessing` or some other more explicit form of
parallelism
2.  Perform mental gymnastics trying to fit their problem into spark using
clever choice of key values but often failing to acheive much speedup (if not a
significant slowdown)


Direct Dask Graphs
------------------

Historically I've constructed dask graphs directly for these use cases.  Manual
creation of dask graphs lets you specify fairly arbitrary workloads which can
then use the dask schedulers to execute in parallel.
The [dask docs](dask.pydata.org/en/latest/custom-graphs.html) hold the
following example of a simple data processing pipeline:

<img src="{{ BASE_PATH }}/images/pipeline.png" align="right">

{% highlight Python %}
def load(filename):
    ...
def clean(data):
    ...
def analyze(sequence_of_data):
    ...
def store(result):
    ...

dsk = {'load-1': (load, 'myfile.a.data'),
       'load-2': (load, 'myfile.b.data'),
       'load-3': (load, 'myfile.c.data'),
       'clean-1': (clean, 'load-1'),
       'clean-2': (clean, 'load-2'),
       'clean-3': (clean, 'load-3'),
       'analyze': (analyze, ['clean-%d' % i for i in [1, 2, 3]]),
       'store': (store, 'analyze')}

>>> from dask.multiprocessing import get
>>> get(dsk, 'store')  # executes in parallel
{% endhighlight %}

Feedback from users is that this is interesting and powerful but that
programming directly in dictionaries is not inutitive, doesn't integrate well
with IDEs, and is prone to error.


Introducing dask.do
-------------------

We want the same ability to write custom parallel workloads but using
normal-ish Python code rather than raw dictionaries.  We solve this with the
`dask.do` function which turns any normal Python function into a delayed
version that adds to a dask graph.  The `do` function lets us rewrite the
computation above as follows:

{% highlight Python %}
from dask import do

loads = [do(load)('myfile.a.data'),
         do(load)('myfile.b.data'),
         do(load)('myfile.c.data')]

cleaned = [do(clean)(x) for x in loads]

analysis = do(analyze)(cleaned)
result = do(store)(analysis)
{% endhighlight %}

The explicit function calls here don't perform work directly; instead they
build up a dask graph lazily which we can then execute in parallel

{% highlight Python %}
from dask.multiprocessing import get
result.compute(get=get)
{% endhighlight %}

This interface was suggested by [Gael Varoquaux](http://gael-varoquaux.info/)
based on his experience with [joblib](https://pythonhosted.org/joblib/).  It
was implemented by [Jim Crist](http://jcrist.github.io/)
[here](https://github.com/ContinuumIO/dask/pull/408).


Example: Nested Cross Validation
--------------------------------

I sat down with a Machine learning student, [Gabriel
Krummenacher](http://people.inf.ethz.ch/kgabriel/) and worked to parallelize a
small code to do nested cross validation.  Below is a comparison of a
sequential implementation that has been parallelized using `dask.do`:

You can safely skip reading this code in depth.  The take-away is that it's
somewhat involved but that the addition of parallelism is light.

<img src="{{BASE_PATH}}/images/do.gif">

The parallel version runs about four times faster on a personal laptop.  This
example is artificially similar.  The sequential version is just a downgraded
version of the parallel code.  The original sequential prototype was lost.  The
parallel version is available
[on github](http://github.com/mrocklin/dask-crossval).

So the result of our imperative-style for-loop code is a fully parallelizable
dask graph.  We visualize that graph below.

    test_score.visualize()

<a href="{{BASE_PATH}}/images/crossval.png">
  <img src="{{BASE_PATH}}/images/crossval.png"
       alt="Cross validation dask graph">
</a>


Help!
-----

Is this a useful interface?  It would be great if people could try this out
and generate feedback on `dask.do`.
