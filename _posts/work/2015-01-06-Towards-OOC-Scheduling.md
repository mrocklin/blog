---
layout: post
title: Towards Out-of-core ND-Arrays -- Multi-core Scheduling
category : work
tags : [scipy, Python, Programming, Blaze]
---
{% include JB/setup %}

**tl;dr** We show off the ideas and performance behind a multi-threaded
shared-memory task scheduler.  We end with pretty GIFs.

*Disclaimer: This post is on experimental buggy code.  This is not ready for public use.*

*Disclaimer 2: This post is technical and intended for people who care about
task scheduling, not for traditional users.*

Setup
-----

My last two posts
([post 1](http://matthewrocklin.com/blog/work/2014/12/27/Towards-OOC/),
[post 2](http://matthewrocklin.com/blog/work/2014/12/30/Towards-OOC-Frontend/))
construct an ND-Array library out of a task scheduler, NumPy, and Blaze.

In these posts we used a simple twenty-line scheduler to execute array
computations out-of-core.  This scheduler, while simple, is inefficient for
complex computations (it suffers the same drawbacks as the naive recursive
solution to Fibonacci).

In this post we outline a less elegent but more effective scheduler that uses
multiple threads and caching to achieve performance on an interesting class of
array operations.


Example
-------

First, we establish value by doing a hard thing well.  Given two large
arrays stored in HDF5.

{% highlight Python %}
import h5py
f = h5py.File('myfile.hdf5')
A = f.create_dataset(name='A', shape=(4000, 2000000), dtype='f8',
                     chunks=(250, 250), fillvalue=1.0)
B = f.create_dataset(name='B', shape=(4000, 4000), dtype='f8',
                     chunks=(250, 250), fillvalue=1.0)
f.close()
{% endhighlight %}

We do a transpose and dot product.  We use all of our cores.

{% highlight Python %}
from blaze import Data, into
from dask.obj import Array

f = h5py.File('myfile.hdf5')

a = into(Array, f['A'], blockshape=(1000, 1000), name='A')
b = into(Array, f['B'], blockshape=(1000, 1000), name='B')

A = Data(a)
B = Data(b)

expr = A.T.dot(B)

result = into('myfile.hdf5::/C', expr)
{% endhighlight %}

Among the inputs, the intermediate results, and the output, none fit in memory
and yet we're still able to compute comfortably.  Even better we leveraged all
of our cores.

In principle we could have computed this with only 100MB or so of RAM.  We
failed to actually achieve this (see note at bottom) but still, *in theory*,
we're great!


Avoid Intermediates
-------------------

To keep a small memory footprint we avoid holding on to unnecessary
intermediate data.  The full computation graph of a smaller problem
looks like the following:

<img src="{{ BASE_PATH }}/images/dask/uninlined.png"
     alt="Un-inlined dask">

Boxes are data, circles are functions, arrows specify which functions
produce/consume which data.

The top row of circles is the actual dot products (note the many data
dependence arrows coming out of them).  The bottom row of circles is getting
out blocks from the the `A` dataset from the HDF5 file.  The second row is
transposing the blocks from the first row and adding another smaller set of
blocks from `B`.

This is bad; we replicate our data four times here, once in each of the rows.
We pull out all of the chunks, transpose each of them, and then finally do a
dot product.  If we couldn't fit the original data in memory then there is no
way that this will work.


Function Inlining
-----------------

So we don't explicitly run each of these circles and store the results, instead
we merge quick computations, like `np.transpose`, with long computations, like
`np.dot`.  We may end up running the same quick function twice, but at least we
won't have to store the result.  We trade computation for memory.

The result looks like the following:

<img src="{{ BASE_PATH }}/images/dask/inlined.png"
     alt="inlined dask">

Now our keys hold nested tasks.  All of these operations are run by a worker
thread at once. (non-LISP-ers avert your eyes):

{% highlight Python %}
('x_6', 6, 0): (dotmany, [(np.transpose, (ndslice, 'A', (1000, 1000), 0, 6)),
                          (np.transpose, (ndslice, 'A', (1000, 1000), 1, 6))],
                          [(ndslice, 'B', (1000, 1000), 0, 0),
                           (ndslice, 'B', (1000, 1000), 1, 0)]),
{% endhighlight %}

Where we used to have a simple tuple of `(func, *args)` we now have tuples of
tuples `(func, (func2, *args), (func3, *args))`, inlined functions.

This effectively shoves all of the storage back down the HDF5 store.  We'll
end up pulling the same blocks out multiple times, but repeated disk access is
inevitable on large complex problems.

This is all automatic.  Dask now includes an `inline` function that does this
for you.  You just give it a set of "fast" functions to ignore, e.g.

    dsk2 = inline(dsk, [np.transpose, ndslice, add, mul, ...])


Scheduler
---------

Now that we have a nice dask to crunch on, lets go about actually running all
of those tasks efficiently.  Given a dask and a thread pool we want to compute
the outputs using all of our cores in limited space.  This is the job of a
*scheduler*.

<img src="{{ BASE_PATH }}/images/threads.jpg"
      align="right"
      alt="Thread pool, courtesy of sewingmantra.com"
      width="20%">

Our new multi-threaded cached scheduler is complex but effective.  It replaces
the elegant, 20 line reference solution with a 400 line blob of ugly code
filled with locks and mutable state.  Still, it manages the computation sanely,
performs some critical optimizations, and uses many cores.

If you weren't already aware, many NumPy operations release the GIL.  This is
possible because they aren't running Python code most of the time.  As a result
NumPy programs do not suffer the single-active-core-per-process limitations
of most Python code.  We get to use all of our hardware, and keep benefiting
from Moore's law.


Approach
--------

We follow a fairly standard model.  We create a `ThreadPool` with a fixed
number of workers.  We analyze the dask to determine "ready to run" tasks.
We send a task to each of our worker threads.  As they finish they update the
run-state, marking jobs as finished, inserting their results into a shared
cache, and then marking new jobs as ready based on the newly available data.
This update process is fully indexed and handled by the worker threads
themselves (with appropriate locks) making the overhead negligible and
hopefully scalable to complex workloads.

Newly available worker threads select a new ready task.  Often there are
several tasks to choose from.  This choice is both cheap and can strongly
affect performance.  A variety of policies are open to us.  Currently we select
tasks that release data resources in an effort to keep the shared cache as
small as possible.


Optimizations
-------------

As just mentioned, we choose tasks that, when completed, will free up
resources.  This detail drastically reduces the amount of intermediates.


Example: Embarrassingly parallel computation
-------------------------------------------

<img src="{{ BASE_PATH }}/images/dask/embarrassing.gif"
      align="right"
      width="50%"
      alt="Embarassingly parallel dask">

On the right is an animated GIF showing the progress of the following
embarrassingly parallel computation:

    expr = (((A + 1) * 2) ** 3)

Circles are computations, boxes are data.  Red colored things are actively
taking up resources; red circles are currently executing functions (occupying
one of our workers) and red boxes are data currently residing in the cache
(occupying precious memory).  Blue nodes are finished computations or data
released from memory because it is no longer necessary.  Once all functions
that rely on a data resource terminate, that resource can be freed.

In short, we want to turn all nodes blue while minimizing the number of red
boxes we have at any given time.

This policy to execute tasks that free resources causes "vertical" execution
when possible.  In this example our approach is optimal because the number of
red boxes is kept small throughout the computation.

Conversely one could imagine a horizontal progression in which we first do all
of the bottom tasks, then all of the middle tasks, then all of the final tasks.
This horizontal progression would have to hold on to much more data at once
which would bog down our system.


Example: More complex computation with Reductions
-------------------------------------------------

<img src="{{ BASE_PATH }}/images/dask/normalized-b.gif"
      align="right"
      width="35%"
      alt="More complex dask">

We now show a more complex expression

    expr = (B - B.mean(axis=0)) + (B.T / B.std())

This extends the class of expressions that we've seen so far to reductions and
reductions along an axis.  The per-chunk reductions start at the bottom and
depend only on the chunk from which they originated.  These per-chunk results
are then concatenated together and re-reduced with the large circles (zoom in
to see the text `concatenate` in there.)  The next level takes these (small)
results and the original data again (note the long edges back down the bottom
data resources) which result in per-chunk subtractions and divisions.

From there on out the work is embarrassing, resembling the computation above.
In this case we have relatively little parallelism, so the frontier of red
boxes covers the entire image; fortunately the dataset is small.


Example: Fail Case
------------------

<img src="{{ BASE_PATH }}/images/dask/fail-case.gif"
      align="right"
      width="50%"
      alt="A case where our scheduling algorithm fails to avoid intermediates">

We now show a case where our greedy solution fails miserably

    expr = (A.T.dot(B) - B.mean(axis=0))

The two large functions on the second level from the bottom are the computation
of the Mean.  These are relatively cheap computations that, once completed,
allow each of the blocks of the result of the dot product to terminate quickly.

Tragically these mean computations don't execute until the last possible
moment.  Once they finally complete the computation floods upwards releasing
quickly.  Sadly we had almost a full row of red boxes before this occurs.

In this case our greedy solution was short sighted; a slightly more global
solution would quickly select these large circles to run quickly.

Perhaps betweenness centrality would be a good measure here.


On-disk caching
---------------

We'll never build a good enough scheduler; we'll eventually run into a case
where we need on-disk caching.  This isn't actually that terrible.  High
performance SSDs get close to 1 GB/second throughput and, in the complex cases
where data-aware scheduling fails, we probably compute slower than that anyway.

I have a little project, [`chest`](https://github.com/mrocklin/chest/) for this
but it's pretty immature.  In general I'd like to see more projects implement
the `dict` interface.


Trouble with binary data stores
-------------------------------

I have a confession, the first computation, the very large dot product,
sometimes crashes my machine.  While then scheduler manages memory well I have
a memory leak somewhere.  I suspect that I use HDF5 improperly.

I also tried doing this with `bcolz`.  Sadly nd-chunking is not well
supported.  [email thread
here](https://groups.google.com/forum/#!topic/bcolz/6pddtrKMqQc) [and
here](https://groups.google.com/forum/#!topic/bcolz/330-llmA3ps).


Expression Scope
----------------

Blaze currently generates dasks for the following:

1.  Elementwise operations (like `+`, `*`, `exp`, `log`, ...)
2.  Dimension shuffling like `np.transpose`
3.  Tensor contraction like `np.tensordot`
4.  Reductions like `np.mean(..., axis=...)`
5.  All combinations of the above

We also comply with the NumPy API on these operations..  At the time of writing
notable missing elements include the following:

1.  Slicing (though this should be easy to add)
2.  Solve, SVD, or any more complex linear algebra.  There are good solutions
to this implemented in other linear algebra software (Plasma,
Flame, Elemental, ...) but I'm not planning to go down that path until
lots of people start asking for it.
3.  Anything that NumPy can't do.


Bigger ideas
------------

My experience building dynamic schedulers is limited and my approach is likely
suboptimal.  It would be great to see other approaches.  None of the logic in
this post is specific to Blaze or even to NumPy.  To build a scheduler you only
need to understand the model of a graph of computations with data dependencies.

If we were ambitious we might consider a distributed scheduler to execute these
task graphs across many nodes in a distributed-memory situation (like a
cluster).  This is a hard problem but it would open up a different class of
computational solutions.  The Blaze code to generate the dasks would not change
; the graphs that we generate are orthogonal to our choice of scheduler.


Help
----

I could use help with all of this, either as open source work (links below) or
for money.  Continuum has grant funding and ample interesting problems.

**Links:**

* [Dask spec](http://dask.readthedocs.org/en/latest/)
* [Scheduler implementation (with decent narrative documentation)](https://github.com/ContinuumIO/dask/blob/master/dask/threaded.py)
