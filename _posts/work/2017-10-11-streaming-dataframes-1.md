---
layout: post
title: Streaming Dataframes
category: work
draft: true
tags: [Programming, Python, scipy, dask]
theme: twitter
---

{% include JB/setup %}

*This work is supported by [Anaconda Inc](http://anaconda.com) and the Data
Driven Discovery Initiative from the [Moore Foundation](https://www.moore.org/)*

<a href="{{BASE_PATH}}/images/streaming-dataframes-plot.gif">
  <img src="{{BASE_PATH}}/images/streaming-dataframes-plot.gif"
     align="right"
     width="40%"></a>

Summary
-------

This post describes a prototype project to handle continuous data sources of
tabular data using Pandas, and Streamz.


Introduction
------------

Some data never stops.  It arrives continuously in a constant, never-ending
stream.  Algorithms to handle this data are slightly different from what you
find in libraries like NumPy and Pandas, which assume that they know all of the
data up-front.  It's still possible to use these libraries, but you need to be
clever and keep enough intermediate data around to compute marginal updates
when new data comes in.


Example: Streaming Mean
-----------------------

For example, lets say that we have a continuous stream of CSV files coming at
us and we want to print out the mean over time.  We get a new CSV file every
once in a while, so we never stop.

We can accomplish this by keeping running totals and running counts as follows:

```python
total = 0
count = 0

for filename in filenames:  # filenames is an infinite iterator
    df = pd.read_csv(filename)
    total = total + df.sum()
    count = count + df.count()
    mean = total / count
    print(mean)
```

Now as we add new files to our `filenames` iterator our code prints out new
means that are updated over time.  We don't have a single result, we have
continuous stream of results.  Our output data is an infinite stream, just like our
input data.

When our computations are linear and straghtforward like this a for loop
suffices.  However when our computations branch out and have several streams
branching out or converging, possibly with rate limiting or buffering between
them this for-loop approach can grow complex.

Streamz
-------

A few months ago I pushed a small library called
[streamz](http://streamz.readthedocs.io/en/latest/), which handled control flow
for pipelines, including linear map operations, operations that accumulated
state, branching, joining, as well as back pressure, flow control, feedback,
and so on.  Streamz was designed to handle all of the movement of data and
signaling of computation at the right time.  This library was quietly used by a
couple of groups and now feels fairly clean and useful.

Streamz was designed to handle the *control flow* of such a system, but did
nothing to help you with streaming algorithms.  Over the past week I've been
building a dataframe abstraction on top of streamz to help with streaming
tabular data.  This module uses Pandas, and implements a subset of the Pandas
API, so hopefully it will be easy to use for programmers with existing Python
knowledge.

Example: Streaming Mean
-----------------------

Our example above could be written as follows with streamz

```python
source = Stream.filenames('path/to/dir/*.csv')  # stream of filenames
sdf = (source.map(pd.read_csv)                  # stream of Pandas dataframes
             .to_dataframe(example=...))        # logical streaming dataframe

sdf.mean().stream.sink(print)                   # printed stream of mean values
```

This example is no more clear than the for-loop version.  On its own this is
probably a *worse* solution than what we had before, just because it involves
new technology.  Where this starts becoming useful is when you start wanting to
do multiple things with your data at once, and the administrative cost of
updating all of the relevant data structures becomes challenging.

For example if you wanted to compute both the sum, and a groupby-aggregation at
the same time, and then use that aggregation to trigger other events when it
got too high, then this might become problematic for basic for loops.

Jupyter Integration
-------------------

Using [ipywidgets](https://ipywidgets.readthedocs.io/en/stable/) and [Bokeh
plots](https://bokeh.pydata.org/en/latest/) we're able to build nicely
responsive feedback whenever things change.

<a href="{{BASE_PATH}}/images/streaming-dataframes-files.gif">
  <img src="{{BASE_PATH}}/images/streaming-dataframes-files.gif"
     width="100%"></a>

What is supported?
------------------

This project is young and there are plenty of holes in the API.  That being
said, the following works fine:

Elementwise operations:

```python
sdf['z'] = sdf.x + sdf.y
sdf = sdf[sdf.z > 2]
```

Simple reductions:

```python
sdf.sum()
sdf.x.mean()
```

Groupby reductions:

```python
sdf.groupby(sdf.x).y.mean()
```

Rolling reductions by number of rows or time window

```python
sdf.rolling(20).x.mean()
sdf.rolling('100ms').x.quantile(0.9)
```

Real time plotting with Bokeh (one of my favorite features)

```python
sdf.plot()
```

<a href="{{BASE_PATH}}/images/streaming-dataframes-plot.gif">
  <img src="{{BASE_PATH}}/images/streaming-dataframes-plot.gif"
     align="right"
     width="40%"></a>

What's missing?
---------------

1.  Streamz has an optional Dask backend for parallel computing.  I haven't
    made any attempt to attach these two
2.  Data ingestion from common streaming sources like Kafka.  I'm in the
    process now of building asynchronous aware wrappers around Kafka Python
    client libraries, so this is likely to come soon.
3.  Computation currently happens on the event loop, which is a bit of an
    anti-pattern.  This will be resolved if we connect Dask.
4.  Performance.  Some of the operations above (particularly rolling
    operations) do involve some non-trivial copying, especially with larger
    windows.
5.  Filled out API.  We still many common operations (like variance).
6.  ...
