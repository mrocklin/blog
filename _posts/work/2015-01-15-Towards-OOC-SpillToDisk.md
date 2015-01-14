---
layout: post
title: Towards Out-of-core ND-Arrays -- Spilling to Disk
category : work
draft : true
tags : [scipy, Python, Programming, Blaze]
---
{% include JB/setup %}

**tl;dr** We implement a dictionary that spills to disk when we run out of
memory.  We connect this to our scheduler.

Introduction
------------

This is the fifth in a sequence of posts constructing an on-disk (out-of-core)
n-dimensional array using NumPy for in-memory computations, Blaze for
high-level control, and dask for task scheduling.  You can view
these posts here:

1. [Simple task scheduling](http://matthewrocklin.com/blog/work/2014/12/27/Towards-OOC/),
2. [Frontend usability](http://matthewrocklin.com/blog/work/2014/12/30/Towards-OOC-Frontend/)
3. [A multi-threaded scheduler](http://matthewrocklin.com/blog/work/2015/01/06/Towards-OOC-Scheduling/)
4. [Matrix Multiply Benchmark](http://matthewrocklin.com/blog/work/2015/01/15/Towards-OOC-MatMul/)

In this post we discuss `chest` a `dict` type that spills to disk and how it helps
large computations from flooding memory.


Intermediate Data
-----------------

<img src="{{ BASE_PATH }}/images/dask/fail-case.gif"
      align="right"
      width="50%"
      alt="A case where our scheduling algorithm fails to avoid intermediates">

If you read the
[post on scheduling](http://matthewrocklin.com/blog/work/2015/01/06/Towards-OOC-Scheduling/)
you may recall that our goal was to minimize intermediates during a
multi-worker computation.  Images like the one on the right show traces of our
scheduler as it traverses the task dependency graph.  Our goal was to compute
the entire graph quickly while keeping only a small amount of data in memory.

Sometimes we fail at this goal, our scheduler inadvertently needs to store
many large intermediate results, and we risk crashing our machine.  In these
cases we want to spill excess intermediate data to disk.


Chest
-----

Chest is a dict-like object that writes data to disk once it runs out of
memory.

{% highlight Python %}
>>> from chest import Chest
>>> d = Chest(available_memory=1e9)  # Only use a GigaByte
{% endhighlight %}

It satisfies the `MutableMapping` interface so it looks and feels exactly like
a `dict`

{% highlight Python %}
>>> d = Chest(available_memory=24)  # enough space for one Python integer

>>> d['one'] = 1
>>> d['two'] = 2
>>> d['three'] = 3
>>> d['three']
3
>>> d.keys()
['one', 'two', 'three']
{% endhighlight %}

But it only keeps some of its data in memory

{% highlight Python %}
>>> d.inmem
{'three': 3}
{% endhighlight %}

While the rest lives somewhere on disk

{% highlight Python %}
>>> d.path
'/tmp/tmpb5ouAb.chest'
>>> os.listdir(d.path)
['one', 'two']
{% endhighlight %}

This data is stored using pickle by default but `chest` supports any protocol
with the `dump/load` interface.  The data is loaded on demand.

A quick point about `pickle`.  Frequent readers of my blog may know of my
sadness at how this library
[serializes functions](http://matthewrocklin.com/blog/work/2013/12/05/Parallelism-and-Serialization/)
and the effect on multiprocessing.
That sadness does not extend to normal data.  Pickle is fine for data if you
use the `protocol=` keyword to `pickle.dump` correctly .  Pickle isn't a good
cross-language solution, but that doesn't matter in our application of
temporarily storing numpy arrays on disk.


Recent tweaks
-------------

In using `chest` alongside `dask` with any reasonable success I had to make the
following improvements to the original implementation:

1.  A basic LRU mechanism to write only infrequently used data
2.  A policy to avoid writing the same data to disk twice if it hasn't changed
3.  Thread safety

Now we can execute more dask workflows without risk of flooding memory

{% highlight Python %}
A = ...
B = ...
expr = A.T.dot(B) - B.mean(axis=0)

cache = Chest(available_memory=1e9)

into('myfile.hdf5::/result', expr, cache=cache)
{% endhighlight %}

Now we incur only moderate slowdown when we schedule poorly and run into large
quantities of intermediate data.


Conclusion
----------

Chest is only useful when we fail to schedule well.  I'm still thinking about
cheap algorithms to schedule tasks well and avoid keeping data in memory but
it's nice to have `chest` as a backup for when these algorithms fail.
Resilience is reassuring.
