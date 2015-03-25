---
layout: post
title: Towards Out-of-core DataFrames
category : work
draft: true
tags : [scipy, Python, Programming, Blaze, dask]
---
{% include JB/setup %}

*This work is supported by [Continuum Analytics](http://continuum.io)
and the [XDATA Program](http://www.darpa.mil/our_work/i2o/programs/xdata.aspx)
as part of the [Blaze Project](http://blaze.pydata.org/docs/dev/index.html)*

*This post primarily targets developers.*

**tl;dr** We partition out-of-core dataframes efficiently.


Partition Data
--------------

Many efficient parallel algorithms require intelligently partitioned data.

For example data indexed by time might partition into month-long
blocks.  Data indexed by text might have all of the "A"s in one group and
all of the "B"s in another.  These divisions let us arrange work with
foresight.

To extend Pandas operations to larger-than-memory data efficient partition
algorithms are critical.  This is tricky when data doesn't fit in memory.


Partitioning is fundamentally hard
----------------------------------

*Data locality is the root of all performance

    -- A Good Programmer*

Partitioning/shuffling is inherently non-local.  For any subset
of our input data we will need to separate and send bits to all of our output
partitions.  If we have a thousand partitions then that's a million little
partition shards to communicate.  Ouch.

<img src="{{ BASE_PATH }}/images/partition-transfer.png"
     alt="Shuffling data between partitions"
     width="30%"
     align="right">

Consider the following setup

      100GB dataset
    / 100MB partitions
    = 1,000 input partitions

To partition we need shuffle data in the input partitions to a similar number of
output partitions

      1,000 input partitions
    * 1,000 output partitions
    = 1,000,000 partition shards

If our communication/storage of those shards has even a millisecond of latency
then we run into problems.

      1,000,000 partition shards
    x 1ms
    = 18 minutes

Previously I stored the partition-shards individually on the filesystem using
cPickle.  This was slow.  Now we collect and organize partition shards headed
for the same out-block and write out many at a time, bundling overhead.
We balance this practice against memory constraints.  This stresses both Python
latencies and memory use.


BColz, now for very small data
------------------------------

Fortuantely we have a nice on-disk chunked array container that
supports append in Cython.  [BColz](http://bcolz.blosc.org/) (formerly BLZ
(formerly CArray)) does this for us.  It wasn't originally designed for this
use case but performs admirably.

Briefly, BColz is...

*  A binary store (like HDF5)
*  With columnar access (useful for tabular computations)
*  That stores data in cache-friendly sized blocks
*  With a focus on compression
*  Written mostly by Francesc Alted (PyTables) and Valentin Haenel

It includes two main objects:

*  `carray`: An on-disk numpy array
*  `ctable`: A named collection of `carrays` to represent a table/dataframe

Partitioned Frame
-----------------

We use `carray` to make a new data structure `pframe` with the following
operations:

*  Append pandas DataFrame to collection, and partition it along the index on
   known block divisions `blockdivs`
*  Pull out the DataFrame corresponding to any particular partition

Internally we invent two new data structures:

*  `cframe`: Like `ctable` this stores column information in a collection of
   `carrays`.  Unlike `ctable` this maps perfectly onto the custom
   block structure used internally by Pandas.  For internal use only.
*  `pframe`: A collection of `cframes`, one for each partition.

<img src="{{ BASE_PATH }}/images/pframe-design.png"
     width="100%"
     alt="Partitioned Frame design">

CFrame and `bcolz.carray` manage efficient incremental storage of DataFrames on
disk as well as their eventual retrieval.

PFrame partitions incoming data and feeds it to the appropriate CFrame.


Example
-------

Create test dataset

{% highlight Python %}
In [1]: import pandas as pd
In [2]: df = pd.DataFrame({'a': [1, 2, 3, 4],
...                        'b': [1., 2., 3., 4.]},
...                       index=[1, 4, 10, 20])
{% endhighlight %}

Create `pframe` like our test dataset, partitioning on divisions 5, 15.  Append
the single test dataframe.

{% highlight Python %}
In [3]: from pframe import pframe
In [4]: pf = pframe(like=df, blockdivs=[5, 15])
In [5]: pf.append(df)
{% endhighlight %}

Pull out partitions

{% highlight Python %}
In [6]: pf.get_partition(0)
Out[6]:
   a  b
1  1  1
4  2  2

In [7]: pf.get_partition(1)
Out[7]:
    a  b
10  3  3

In [8]: pf.get_partition(2)
Out[8]:
    a  b
20  4  4
{% endhighlight %}

Continue to append data...

{% highlight Python %}
In [9]: df2 = pd.DataFrame({'a': [10, 20, 30, 40],
...                         'b': [10., 20., 30., 40.]},
...                        index=[1, 4, 10, 20])
In [10]: pf.append(df2)
{% endhighlight %}

... and partitions grow accordingly.

{% highlight Python %}
In [12]: pf.get_partition(0)
Out[12]:
    a   b
1   1   1
4   2   2
1  10  10
4  20  20
{% endhighlight %}

We can continue this until our disk fills up.  This runs near peak I/O speeds.


Performance
-----------

I've partitioned the NYCTaxi dataset a lot this week and posting my
results to the Continuum chat with messages like the following

    I think I've got it to work, though it took all night and my hard drive
    filled up.
    Down to six hours and it actually works.
    Three hours!
    By removing object dtypes we're down to 30 minutes
    20!  This is actually usable.
    OK, I've got this to six minutes.  Thank goodness for Pandas categoricals.
    Five.
    Down to about three and a half with multithreading, but only if we stop
    blosc from segfaulting.

And thats where I am now.  It's been a fun week.  Here is a tiny benchmark.

{% highlight Python %}
>>> import pandas as pd
>>> import numpy as np
>>> from pframe import pframe

>>> df = pd.DataFrame({'a': np.random.random(1000000),
                       'b': np.random.poisson(100, size=1000000),
                       'c': np.random.random(1000000),
                       'd': np.random.random(1000000).astype('f4')}).set_index('a')
{% endhighlight %}

Set up a pframe to match the structure of this DataFrame
Partition index into divisions of size 0.1

{% highlight Python %}
>>> pf = pframe(like=df,
...             blockdivs=[.1, .2, .3, .4, .5, .6, .7, .8, .9],
...             chunklen=2**15)
{% endhighlight %}

Dump the random data into the Partition Frame one hundred times and compute
effective bandwidths.

{% highlight Python %}
>>> for i in range(100):
...     pf.append(df)

CPU times: user 39.4 s, sys: 3.01 s, total: 42.4 s
Wall time: 40.6 s

>>> pf.nbytes
2800000000

>>> pf.nbytes / 40.6 / 1e6  # MB/s
68.9655172413793

>>> pf.cbytes / 40.6 / 1e6  # Actual compressed bytes on disk
41.5172952955665
{% endhighlight %}


We partition and store on disk random-ish data at 68MB/s (using
compression).  This is on my old small notebook computer with a weak processor
and hard drive I/O bandwidth at around 100 MB/s.


Theoretical Comparison to External Sort
---------------------------------------

There isn't much literature to back up my approach.  That concerns me.
There is a lot of literature however on external sorting and they often site
our partitioning problem as a use case.  Perhaps we should do an external sort?

I thought I'd quickly give some reasons why I think the current approach is
theoretically better than an out-of-core sort; hopefully someone smarter can
come by and tell me why I'm wrong.

We don't need a full sort, we need something far weaker.   External sort
requires at least two passes over the data while the method above requires one
full pass through the data as well as one additional pass through the index
column to determine good block divisions.  These divisions should be of
*approximately* equal size.  The *approximate size* can be pretty rough.  I
don't think we would notice a variation of a factor of five in block sizes.
Task scheduling lets us be pretty sloppy with load imbalance as long as we have
many tasks.

I haven't implemented a good external sort though so I'm only able to argue
theory here.  I'm likely missing important implementation details.
