---
layout: post
title: Dask Development Log
category: work
draft: true
tags: [Programming, Python, scipy, dask]
theme: twitter
---
{% include JB/setup %}

*This work is supported by TODO add Fabian's affiliation, [Anaconda
Inc](http://anaconda.com), and the [Berkeley Institute for Data
Science](https://bids.berkeley.edu/)*

At a recent Scikit-learn/Scikit-image/Dask sprint at BIDS, Fabian Pedregosa (a
machine learning researcher and Scikit-learn core developer) and Matthew
Rocklin (Dask core developer) sat down together to apply the SAGA optimizer to
parallel Dask datasets.

It as an interesting both to see how the algorithm performed and also to see
the ease and challenges to parallelizing a research algorithm with Dask.

### Start

We started with an intitial implementation that Fabian had written for Numpy
arrays using Numba.

TODO: Fabian should provide code example of original Numba/Numpy code

This implementation performs well in practice, and is already part of Fabian's
research.  We wanted to apply it across a parallel Dask array by applying it to
each chunk of the Dask array, a smaller Numpy array, one at a time, carrying
along a set of parameters along the way.


### Process

In order to better understand the challenges of writing Dask algorithms, Fabian
did most of the actual coding to start.  Fabian is good example of a researcher who
knows how to program well and how to design ML algorithms, but has no direct
exposure to the Dask library.  This was an educational opportunity both for
Fabian and for Matt.  Fabian learned how to use Dask, and Matt learned how to
introduce Dask to researchers like Fabian.

### Step 1: Build a sequential algorithm with pure functions

To start we actually didn't use Dask at all, instead, Matt asked Fabian to
modify his algorithm in a few ways:

1.  It should operate over a list of Numpy arrays (this is like a Dask array,
    but simpler)
2.  It should separate blocks of logic into separate functions, these will
    eventually become tasks, so they should be sizable chunks of work.
3.  These functions should not modify their inputs, nor should they depend on
    global state.  All information that those functions require (like
    the parameters that we're learning in our algorithm) should be
    explicitly provided as inputs.

These requested modifiations affect performance a bit, we end up making more
copies of the parameters and of some intermediate state.  In terms of
programming difficulty this took a bit of time (a couple hours?) but is a
straightforward task that Fabian didn't seem to find challenging or foreign.

TODO: example of list-of-numpy-arrays non-dask implementation


### Step 2: Apply dask.delayed

After things looked good, meaning that no functions either modified their
inputs nor relied on global state we went over a [dask.delayed
example](https://mybinder.org/v2/gh/dask/dask-examples/master?filepath=delayed.ipynb
) together, and then applied the `@dask.delayed` decorator to the functions
that Fabian had written.  Fabian did this at first in about five minutes and to
mutual surprise, things actually worked

TODO: Example diff when applying dask.delayed and image of dashboard after
running


### Step 3: Diagnose and add more dask.delayed calls

However, while things worked, they were also fairly slow.  If you notice the
dashboard plot above you'll see that there is plenty of white inbetween colored
rectangles.  This shows that there are long periods where none of the workers
is doing any work.

This is a common sign that we're mixing work between the workers (which shows
up on the dashbaord) and the client.  The solution to this is usually more
targetted use of dask.delayed.  Dask delayed is very useful to help parallelize
custom code and while it is trivial to start using, does require some
experience to use well.  It's important to keep track of which operations and
variables are delayed and which aren't.  There is some cost to mixing between
them.

At this point Matt stepped in and added delayed in a few more places and things
started looking cleaner.

TODO: show code diff with extra delayed calls and new image of dashboard


### Step 4: Profile

The dashboard image above gives confidence that our algorithm is operating as
it should.  The block-sequential nature of the algorithm comes out cleanly, and
there gaps between tasks are very short.

However, when we look at the profile plot of the computation across all of our
cores (Dask constantly runs a profiler on all threads on all workers to get
this information) we see that most of our time is spent compiling Numba code.

TODO: image of profile

We started a conversation for this on the [numba issue
tracker](https://github.com/numba/numba/issues/3026)


### Future Work

This was a useful experience to build an interesting algorithm.  Most of the
work above took place in an afternoon.  However to make this more valuable to
actual users we need to do a few things:

1.  Build a normal Scikit-Learn style estimator class for this algorithm
    so that people can use it without thinking too much about delayed objects,
    and can instead just use dask arrays or dataframes
2.  Integrate Fabian's other work that uses sparse arrays.  Hopefully on the
    SAGA side this just means doing a type check and then choosing between the
    two algorithms on a task-by-task basis
3.  Resolve the Numba re-deserialization issue, probably by caching functions
    within Dask
