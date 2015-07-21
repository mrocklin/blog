---
layout: post
title: Profiling Data Throughput
category : work
tags : [scipy, Python, Programming, Blaze, dask]
---
{% include JB/setup %}

*This work is supported by [Continuum Analytics](http://continuum.io)
and the [XDATA Program](http://www.darpa.mil/program/XDATA)
as part of the [Blaze Project](http://blaze.pydata.org)*

*Disclaimer: This post is on experimental/buggy code.*

**tl;dr** We measure the costs of processing semi-structured data like JSON
blobs.


Semi-structured Data
--------------------

Semi-structured data is ubiquitous and computationally painful.  Consider
the following JSON blobs:

    {'name': 'Alice',   'payments': [1, 2, 3]}
    {'name': 'Bob',     'payments': [4, 5]}
    {'name': 'Charlie', 'payments': None}

This data doesn't fit nicely into NumPy or Pandas and so we fall back to
dynamic pure-Python data structures like dicts and lists.  Python's core data
structures are surprisingly good, about as good as compiled languages like
Java, but dynamic data structures present some challenges for efficient
parallel computation.


Volume
------

Semi-structured data is often at the beginning of our data pipeline and so
often has the greatest size.  We may start with 100GB of raw data, reduce to
10GB to load into a database, and finally aggregate down to 1GB for analysis,
machine learning, etc., 1kB of which becomes a plot or table.

<table align="right">
  <thead>
  <tr>
    <th></th>
    <th>Data Bandwidth (MB/s)</th>
    <th>In Parallel (MB/s)</th>
  </tr>
  </thead>
  <tbody>
    <tr><th>Disk I/O</th><td>500</td><td>500</td></tr>
    <tr><th>Decompression</th><td>100</td><td>500</td></tr>
    <tr><th>Deserialization</th><td>50</td><td>250</td></tr>
    <tr><th>In-memory computation</th><td>2000</td><td>oo</td></tr>
    <tr><th>Shuffle</th><td>9</td><td>30</td></tr>
  </tbody>
</table>

Common solutions for large semi-structured data include Python iterators,
multiprocessing, Hadoop, and Spark as well as proper databases like MongoDB and
ElasticSearch.  [Two months
ago](http://matthewrocklin.com/blog/work/2015/02/17/Towards-OOC-Bag/) we built
`dask.bag`, a toy dask experiment for semi-structured data.  Today we'll
strengthen the `dask.bag` project and look more deeply at performance in this
space.

We measure performance with data bandwidth, usually in megabytes per
second (MB/s).  We'll build intuition for why dealing with this data is costly.


Dataset
-------

As a test dataset we play with a dump of GitHub data from
[https://www.githubarchive.org/](https://www.githubarchive.org/).  This data
records every public github event (commit, comment, pull request, etc.) in the
form of a JSON blob.  This data is representative fairly representative of a
broader class of problems.  Often people want to do fairly simple analytics,
like find the top ten committers to a particular repository, or clean the
data before they load it into a database.

We'll play around with this data using `dask.bag`.  This is both to get a feel
for what is expensive and to provide a cohesive set of examples.  In truth we
won't do any real analytics on the github dataset, we'll find that the
expensive parts come well before analytic computation.

Items in our data look like this:

{% highlight Python %}
>>> import json
>>> import dask.bag as db
>>> path = '/home/mrocklin/data/github/2013-05-0*.json.gz'
>>> db.from_filenames(path).map(json.loads).take(1)
({u'actor': u'mjcramer',
  u'actor_attributes': {u'gravatar_id': u'603762b7a39807503a2ee7fe4966acd1',
   u'login': u'mjcramer',
   u'type': u'User'},
  u'created_at': u'2013-05-01T00:01:28-07:00',
  u'payload': {u'description': u'',
   u'master_branch': u'master',
   u'ref': None,
   u'ref_type': u'repository'},
  u'public': True,
  u'repository': {u'created_at': u'2013-05-01T00:01:28-07:00',
   u'description': u'',
   u'fork': False,
   u'forks': 0,
   u'has_downloads': True,
   u'has_issues': True,
   u'has_wiki': True,
   u'id': 9787210,
   u'master_branch': u'master',
   u'name': u'settings',
   u'open_issues': 0,
   u'owner': u'mjcramer',
   u'private': False,
   u'pushed_at': u'2013-05-01T00:01:28-07:00',
   u'size': 0,
   u'stargazers': 0,
   u'url': u'https://github.com/mjcramer/settings',
   u'watchers': 0},
  u'type': u'CreateEvent',
  u'url': u'https://github.com/mjcramer/settings'},)
{% endhighlight %}


Disk I/O and Decompression -- 100-500 MB/s
-------------------------------------------

<table align="right">
  <thead>
  <tr>
    <th></th>
    <th>Data Bandwidth (MB/s)</th>
  </tr>
  </thead>
  <tbody>
    <tr><th>Read from disk with open</th><td>500</td></tr>
    <tr><th>Read from disk with gzip.open</th><td>100</td></tr>
    <tr><th>Parallel Read from disk with gzip.open</th><td>500</td></tr>
  </tbody>
</table>

A modern laptop hard drive can theoretically read data from disk to memory at
800 MB/s.  So we could burn through a 10GB dataset in fifteen seconds on our
laptop.  Workstations with RAID arrays can do a couple GB/s.  In practice I
get around 500 MB/s on my personal laptop.

{% highlight Python %}
In [1]: import json
In [2]: import dask.bag as db
In [3]: from glob import glob
In [4]: path = '/home/mrocklin/data/github/2013-05-0*.json.gz'

In [5]: %time compressed = '\n'.join(open(fn).read() for fn in glob(path))
CPU times: user 75.1 ms, sys: 1.07 s, total: 1.14 s
Wall time: 1.14 s

In [6]: len(compressed) / 0.194 / 1e6  # MB/s
508.5912175438597
{% endhighlight %}

To reduce storage and transfer costs we often compress data.  This requires CPU
effort whenever we want to operate on the stored values.  This can limit
data bandwidth.

{% highlight Python %}
In [7]: import gzip
In [8]: %time total = '\n'.join(gzip.open(fn).read() for fn in glob(path))
CPU times: user 12.2 s, sys: 18.7 s, total: 30.9 s
Wall time: 30.9 s

In [9]: len(total) / 30.9 / 1e6         # MB/s  total bandwidth
Out[9]: 102.16563844660195

In [10]: len(compressed) / 30.9 / 1e6   # MB/s  compressed bandwidth
Out[10]: 18.763559482200648
{% endhighlight %}

So we lose some data bandwidth through compression.  Where we could previously
process 500 MB/s we're now down to only 100 MB/s.  If we count bytes in terms
of the amount stored on disk then we're only hitting 18 MB/s.  We'll get around
this with multiprocessing.


Decompression and Parallel processing -- 500 MB/s
-------------------------------------------------

Fortunately we often have more cores than we know what to do with.
Parallelizing reads can hide much of the decompression cost.

{% highlight Python %}
In [12]: import dask.bag as db

In [13]: %time nbytes = db.from_filenames(path).map(len).sum().compute()
CPU times: user 130 ms, sys: 402 ms, total: 532 ms
Wall time: 5.5 s

In [14]: nbytes / 5.5 / 1e6
Out[14]: 573.9850932727272
{% endhighlight %}

Dask.bag infers that we need to use gzip from the filename.  Dask.bag currently
uses `multiprocessing` to distribute work, allowing us to reclaim our 500 MB/s
throughput on compressed data.  We also could have done this with
multiprocessing, straight Python, and a little elbow-grease.


Deserialization -- 30 MB/s
--------------------------

<table align="right">
  <thead>
  <tr>
    <th></th>
    <th>Data Bandwidth (MB/s)</th>
  </tr>
  </thead>
  <tbody>
    <tr><th>json.loads</th><td>30</td></tr>
    <tr><th>ujson.loads</th><td>50</td></tr>
    <tr><th>Parallel ujson.loads</th><td>150</td></tr>
  </tbody>
</table>

Once we decompress our data we still need to turn bytes into meaningful data
structures (dicts, lists, etc..)  Our GitHub data comes to us as JSON.  This
JSON contains various encodings and bad characters so, just for today, we're
going to punt on bad lines.  Converting JSON text to Python objects
explodes out in memory a bit, so we'll consider a smaller subset for this part,
a single day.

{% highlight Python %}
In [20]: def loads(line):
...          try: return json.loads(line)
...          except: return None

In [21]: path = '/home/mrocklin/data/github/2013-05-01-*.json.gz'
In [22]: lines = list(db.from_filenames(path))

In [23]: %time blobs = list(map(loads, lines))
CPU times: user 10.7 s, sys: 760 ms, total: 11.5 s
Wall time: 11.3 s

In [24]: len(total) / 11.3 / 1e6
Out[24]: 33.9486321238938

In [25]: len(compressed) / 11.3 / 1e6
Out[25]: 6.2989179646017694
{% endhighlight %}

So in terms of actual bytes of JSON we can only convert about 30MB per second.
If we count in terms of the compressed data we store on disk then this looks
more bleak at only 6 MB/s.

### This can be improved by using faster libraries -- 50 MB/s

The [ultrajson](https://github.com/esnme/ultrajson) library, `ujson`, is pretty
slick and can improve our performance a bit.  This is what Pandas uses under
the hood.

{% highlight Python %}
In [28]: import ujson
In [29]: def loads(line):
...          try: return ujson.loads(line)
...          except: return None

In [30]: %time blobs = list(map(loads, lines))
CPU times: user 6.37 s, sys: 1.17 s, total: 7.53 s
Wall time: 7.37 s

In [31]: len(total) / 7.37 / 1e6
Out[31]: 52.05149837177748

In [32]: len(compressed) / 7.37 / 1e6
Out[32]: 9.657771099050203
{% endhighlight %}


### Or through Parallelism  -- 150 MB/s

This can also be accelerated through parallelism, just like decompression.
It's a bit cumbersome to show parallel deserializaiton in isolation.
Instead we'll show all of them together.  This will under-estimate
performance but is much easier to code up.

{% highlight Python %}
In [33]: %time db.from_filenames(path).map(loads).count().compute()
CPU times: user 32.3 ms, sys: 822 ms, total: 854 ms
Wall time: 2.8 s

In [38]: len(total) / 2.8 / 1e6
Out[38]: 137.00697964285717

In [39]: len(compressed) / 2.8 / 1e6
Out[39]: 25.420633214285715
{% endhighlight %}


Mapping and Grouping - 2000 MB/s
--------------------------------

<table align="right">
  <thead>
  <tr>
    <th></th>
    <th>Data Bandwidth (MB/s)</th>
  </tr>
  </thead>
  <tbody>
    <tr><th>Simple Python operations</th><td>1400</td></tr>
    <tr><th>Complex CyToolz operations</th><td>2600</td></tr>
  </tbody>
</table>

Once we have data in memory, Pure Python is relatively fast.  Cytoolz moreso.

{% highlight Python %}
In [55]: %time set(d['type'] for d in blobs)
CPU times: user 162 ms, sys: 123 ms, total: 285 ms
Wall time: 268 ms
Out[55]:
{u'CommitCommentEvent',
 u'CreateEvent',
 u'DeleteEvent',
 u'DownloadEvent',
 u'FollowEvent',
 u'ForkEvent',
 u'GistEvent',
 u'GollumEvent',
 u'IssueCommentEvent',
 u'IssuesEvent',
 u'MemberEvent',
 u'PublicEvent',
 u'PullRequestEvent',
 u'PullRequestReviewCommentEvent',
 u'PushEvent',
 u'WatchEvent'}

In [56]: len(total) / 0.268 / 1e6
Out[56]: 1431.4162052238805

In [57]: import cytoolz
In [58]: %time _ = cytoolz.groupby('type', blobs)  # CyToolz FTW
CPU times: user 144 ms, sys: 0 ns, total: 144 ms
Wall time: 144 ms

In [59]: len(total) / 0.144 / 1e6
Out[59]: 2664.024604166667
{% endhighlight %}

So slicing and logic are essentially free.  The cost of compression and
deserialization dominates actual computation time.  Don't bother optimizing
fast per-record code, especially if CyToolz has already done so for you.  Of
course, you might be doing something expensive per record.  If so then most of
this post isn't relevant for you.


Shuffling - 5-50 MB/s
---------------------

<table align="right">
  <thead>
  <tr>
    <th></th>
    <th>Data Bandwidth (MB/s)</th>
  </tr>
  </thead>
  <tbody>
    <tr><th>Naive groupby with on-disk Shuffle</th><td>25</td></tr>
    <tr><th>Clever foldby without Shuffle</th><td>250</td></tr>
  </tbody>
</table>


For complex logic, like full groupbys and joins, we need to communicate large
amounts of data between workers.  This communication forces us to go through
another full serialization/write/deserialization/read cycle.  This hurts.  And
so, the single most important message from this post:

**Avoid communication-heavy operations on semi-structured data.  Structure your
data and load into a database instead.**

That being said, people will inevitably ignore this advice so we need to have a
not-terrible fallback.

{% highlight Python %}
In [62]: %time dict(db.from_filenames(path)
...                   .map(loads)
...                   .groupby('type')
...                   .map(lambda (k, v): (k, len(v))))
CPU times: user 46.3 s, sys: 6.57 s, total: 52.8 s
Wall time: 2min 14s
Out[62]:
{'CommitCommentEvent': 17889,
 'CreateEvent': 210516,
 'DeleteEvent': 14534,
 'DownloadEvent': 440,
 'FollowEvent': 35910,
 'ForkEvent': 67939,
 'GistEvent': 7344,
 'GollumEvent': 31688,
 'IssueCommentEvent': 163798,
 'IssuesEvent': 102680,
 'MemberEvent': 11664,
 'PublicEvent': 1867,
 'PullRequestEvent': 69080,
 'PullRequestReviewCommentEvent': 17056,
 'PushEvent': 960137,
 'WatchEvent': 173631}

In [63]: len(total) / 134 / 1e6  # MB/s
Out[63]: 23.559091
{% endhighlight %}

This groupby operation goes through the following steps:

1.  Read from disk
2.  Decompress GZip
3.  Deserialize with `ujson`
4.  Do in-memory groupbys on chunks of the data
5.  Reserialize with `msgpack` (a bit faster)
6.  Append group parts to disk
7.  Read in new full groups from disk
8.  Deserialize `msgpack` back to Python objects
9.  Apply length function per group

Some of these steps have great data bandwidths, some less-so.
When we compound many steps together our bandwidth suffers.
We get about 25 MB/s total.  This is about what pyspark gets (although today
`pyspark` can parallelize across multiple machines while `dask.bag` can not.)

Disclaimer, the numbers above are for `dask.bag` and could very easily be
due to implementation flaws, rather than due to inherent challenges.

{% highlight Python %}
>>> import pyspark
>>> sc = pyspark.SparkContext('local[8]')
>>> rdd = sc.textFile(path)
>>> dict(rdd.map(loads)
...         .keyBy(lambda d: d['type'])
...         .groupByKey()
...         .map(lambda (k, v): (k, len(v)))
...         .collect())
{% endhighlight %}

I would be interested in hearing from people who use full groupby on BigData.
I'm quite curious to hear how this is used in practice and how it performs.


Creative Groupbys - 250 MB/s
----------------------------

Don't use groupby.  You can often work around it with cleverness.  Our example
above can be handled with streaming grouping reductions (see [toolz
docs.](http://toolz.readthedocs.org/en/latest/streaming-analytics.html#split-apply-combine-with-groupby-and-reduceby))
This requires more thinking from the programmer but avoids the costly shuffle
process.

{% highlight Python %}
In [66]: %time dict(db.from_filenames(path)
...                   .map(loads)
...                   .foldby('type', lambda total, d: total + 1, 0, lambda a, b: a + b))
Out[66]:
{'CommitCommentEvent': 17889,
 'CreateEvent': 210516,
 'DeleteEvent': 14534,
 'DownloadEvent': 440,
 'FollowEvent': 35910,
 'ForkEvent': 67939,
 'GistEvent': 7344,
 'GollumEvent': 31688,
 'IssueCommentEvent': 163798,
 'IssuesEvent': 102680,
 'MemberEvent': 11664,
 'PublicEvent': 1867,
 'PullRequestEvent': 69080,
 'PullRequestReviewCommentEvent': 17056,
 'PushEvent': 960137,
 'WatchEvent': 173631}
CPU times: user 322 ms, sys: 604 ms, total: 926 ms
Wall time: 13.2 s

In [67]: len(total) / 13.2 / 1e6  # MB/s
Out[67]: 239.16047181818183
{% endhighlight %}

We can also spell this with PySpark which performs about the same.

{% highlight Python %}
>>> dict(rdd.map(loads)  # PySpark equivalent
...         .keyBy(lambda d: d['type'])
...         .combineByKey(lambda d: 1, lambda total, d: total + 1, lambda a, b: a + b)
...         .collect())
{% endhighlight %}


Use a Database
--------------

By the time you're grouping or joining datasets you probably have structured
data that could fit into a dataframe or database.  You should transition from
dynamic data structures (dicts/lists) to dataframes or databases as early as
possible.  DataFrames and databases compactly represent data in formats that
don't require serialization; this improves performance.  Databases are also
very clever about reducing communication.

Tools like `pyspark`, `toolz`, and `dask.bag` are great for initial cleanings
of semi-structured data into a structured format but they're relatively
inefficient at complex analytics.  For inconveniently large data you should
consider a database as soon as possible.  That could be some big-data-solution
or often just Postgres.


Better data structures for semi-structured data?
------------------------------------------------

Dynamic data structures (dicts, lists) are overkill for semi-structured data.
We don't need or use their full power but we inherit all of their limitations
(e.g.  serialization costs.)  Could we build something NumPy/Pandas-like that
could handle the blob-of-JSON use-case?  Probably.

DyND is one such project.  DyND is a C++ project with Python bindings written
by Mark Wiebe and Irwin Zaid and historically funded largely by Continuum and
XData under the same banner as Blaze/Dask.  It could probably handle the
semi-structured data problem case if given a bit of love.  It handles variable
length arrays, text data, and missing values all with numpy-like semantics:

{% highlight Python %}
>>> from dynd import nd
>>> data = [{'name': 'Alice',                       # Semi-structured data
...          'location': {'city': 'LA', 'state': 'CA'},
...          'credits': [1, 2, 3]},
...         {'name': 'Bob',
...          'credits': [4, 5],
...          'location': {'city': 'NYC', 'state': 'NY'}}]

>>> dtype = '''var * {name: string,
...                   location: {city: string,
...                              state: string[2]},
...                   credits: var * int}'''        # Shape of our data

>>> x = nd.array(data, type=dtype)                  # Create DyND array

>>> x                                               # Store compactly in memory
nd.array([["Alice", ["LA", "CA"], [1, 2, 3]],
          ["Bob", ["NYC", "NY"], [4, 5]]])

>>> x.location.city                                 # Nested indexing
nd.array([ "LA", "NYC"],
         type="strided * string")

>>> x.credits                                       # Variable length data
nd.array([[1, 2, 3],    [4, 5]],
         type="strided * var * int32")

>>> x.credits * 10                                  # And computation
nd.array([[10, 20, 30],     [40, 50]],
         type="strided * var * int32")
{% endhighlight %}

Sadly DyND has functionality gaps which limit usability.

{% highlight Python %}
>>> -x.credits                                      # Sadly incomplete :(
TypeError: bad operand type for unary -
{% endhighlight %}

I would like to see DyND mature to the point where it could robustly handle
semi-structured data.  I think that this would be a big win for productivity
that would make projects like `dask.bag` and `pyspark` obsolete for a large
class of use-cases.  If you know Python, C++, and would like to help DyND grow
I'm sure that Mark and Irwin would love the help

*  [DyND Mailing list](https://groups.google.com/forum/#!forum/libdynd-dev)
*  [DyND GitHub repository](https://github.com/libdynd/dynd-python)


Comparison with PySpark
-----------------------

Dask.bag pros:

1.  Doesn't engage the JVM, no heap errors or fiddly flags to set
2.  Conda/pip installable.  You could have it in less than twenty seconds from now.
3.  Slightly faster in-memory implementations thanks to `cytoolz`; this isn't
    important though
4.  Good handling of lazy results per-partition
5.  Faster / lighter weight start-up times
6.  (Subjective) I find the API marginally cleaner

PySpark pros:

1.  Supports distributed computation (this is obviously huge)
2.  More mature, more filled out API
3.  HDFS integration

Dask.bag reinvents a wheel; why bother?

1.  Given the machinery inherited from `dask.array` and `toolz`, `dask.bag` is
very cheap to build and maintain.  It's around 500 significant lines of code.
2.  PySpark throws Python processes inside a JVM ecosystem which can cause some
confusion among users and a performance hit.  A task scheduling
system in the native code ecosystem would be valuable.
3.  Comparison and competition is healthy
4.  I've been asked to make a distributed array.  I suspect that distributed
    bag is a good first step.
