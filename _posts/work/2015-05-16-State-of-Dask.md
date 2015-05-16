---
layout: post
title: State of Dask
category : work
draft: true
tags : [scipy, Python, Programming, Blaze, dask]
---
{% include JB/setup %}

*This work is supported by [Continuum Analytics](http://continuum.io)
and the [XDATA Program](http://www.darpa.mil/our_work/i2o/programs/xdata.aspx)
as part of the [Blaze Project](http://blaze.pydata.org/docs/dev/index.html)*

**tl;dr** We lay out the pieces of Dask, a system for parallel computing

Introduction
------------

Dask began five months ago.  It started as a parallel on-disk array but has
since broadened out.  I've enjoyed [writing about its
development](http://matthewrocklin.com/blog/tags.html#dask-ref) tremendously.

With the [recent 0.5.0 release]() **TODO link** I decided to take a moment to
give an overview of dask's various pieces, their state, and current
development.


Collections, graphs, and schedulers
-----------------------------------

Dask modules can be separated as follows:

**Image of collections, graph, schedulers**

On the left there are collections like arrays, bags, and dataframes.  These
copy APIs for NumPy, PyToolz, and Pandas respectively and are aimed towards
data science users, allowing them to interact with larger datasets.  Operations
on these dask collections produce task graphs which are recipes to compute the
desired result using many smaller computations that each fit in memory.  For
example if we want to sum a trillion numbers then we might break the numbers
into million element chunks, sum those, and then sum the sums.  A previously
impossible task becomes a million and one easy ones.

On the right there are schedulers.  Schedulers execute task graphs in different
situations, usually in parallel.  Notably there are a few schedulers for a
single machine, and a new prototype for a [distributed
scheduler](http://dask.pydata.org/en/latest/distributed.html).

In the center is the directed acyclic graph.  This graph serves as glue between
collections and schedulers.  The dask graph format is simple and doesn't
include any dask classes; it's just [dicts and
tuples](http://dask.readthedocs.org/en/latest/spec.html) and so is easy to
build and low-tech enough to understand immediately.  This separation is very
useful to dask during development; improvements to one side immediately affect
the other.

This separation is useful to other projects too.  Directed acyclic graphs are
popular today in many domains.  By exposing dask's schedulers publicly, other
projects can bypass dask collections and go straight for the execution engine.

A flattering quote from [a github
issue](https://github.com/ContinuumIO/dask/issues/153#issuecomment-92520216):

*dask has been very helpful so far, as it allowed me to skip implementing
all of the usual graph operations. Especially doing the asynchronous
execution properly would have been a lot of work.


Who uses dask?
--------------

I work closely with a few groups that use dask.  Presumably there are others.

1.  [Stephan Hoyer](http://stephanhoyer.com/) at Climate Corp has integrated
`dask.array` into [`xray`](xray.readthedocs.org) a library to manage large
volumes of meteorlogical data (and other labeled arrays.)

2.  [Scikit image](http://scikit-image.org) now includes an
[`apply_parallel`](https://github.com/scikit-image/scikit-image/pull/1493)
operation that uses dask.array to parallelize a wide set of image processing
routines. (work by [Blake Griffiths](https://github.com/cowlicks))

3.  [Mariano Tepper](http://www.marianotepper.com.ar/) a postdoc at Duke, uses
dask in his research on matrix factorizations.  Mariano is also the sole
contributor to the `dask.array.linalg` module, which includes some very nice QR
and SVD algorithms.

4.  Finally I personally use dask daily on work related to the [XData
project](http://www.darpa.mil/our_work/i2o/programs/xdata.aspx).  This tends to
drive some of the newer features.


What works and what doesn't
---------------------------

Dask is modular.  Each of the collections and each of the schedulers are
effectively separate projects.  These subprojects exist at different states of
development.  Knowing how stable or unstable each is can help you to determine
how you depend on it.

**TODO**


*Notably, neither dask.dataframe nor dask.distributed are ready for public use.*


Current work
------------

There are some exciting things happening with dask today.

1.  Dask.bag and dask.dataframe are progressing nicely.  My personal work
    depends on these modules, so they see a lot of attention.
    *  At the moment I focus on grouping and join operations through fast
       shuffles; I hope to write about this problem soon.
    *  The Pandas API is large and complex.  Reimplementing a subset of it
       in a blocked way is straightforward but also detailed and time consuming.
       This would be a great place for community contributions.
2.  Dask.distributed is new.  It needs it tires kicked but it's an exciting
    development.
    *  For easy deployment we're planning to bootstrap off of
       [IPython parallel](http://ipython.org/ipython-doc/dev/parallel/) which
       already has decent coverage of many parallel job systems,
       see [#208](https://github.com/ContinuumIO/dask/pull/208)
    *  [MinRK](https://github.com/minrk), the main developer of IPython
       parallel, is looking into deploying with Yarn, which would give both
       IPython and dask access to existing Hadoop clusters.
3.  Dask.array development these days focuses on outreach.  We've found
    application domains where dask is very useful; we'd like to find more.


No Road Map
-----------

Someone asked on the mailing list for a road map.  Other than the above current
work we don't have a road map.  We've managed well so far only doing work that
was directly asked of us.  This focuses the project on meaningful features.  If
you'd like to see your domain better supported then please contribute.  If you
don't have the technical expertise or time to contribute with code then [please
contribute an issue](https://github.com/ContinuumIO/dask/issues/new), I'd love
to hear from you.

I've enjoyed the ZermMQ guide lately.  Here is their discussion on road maps:
[How ZeroMQ Lost its Road Map](http://zguide.zeromq.org/page:all#How-ZeroMQ-Lost-Its-Road-Map).
