---
layout: post
title: High level performance of Pandas, Dask, Spark, and Arrow
category: work
draft: true
tags: [Programming, Python, scipy, dask]
theme: twitter
---

{% include JB/setup %}

*This work is supported by [Anaconda Inc](http://anaconda.com)*

## Question

> How does dask.dataframe performance compare to Pandas?  Also, what about
> Spark dataframes and Arrow?  How do they compare?

I get this question every few weeks, so I decided to write down my answer once
here in order to avoid repetition.

## Caveats

1.  This answer is likely to change over time.  I'm writing this in August 2018
2.  This question and answer are very high level.
    More technical answers are possible, but not contained here.

## Answers

### Pandas

If you're coming from Python and have smallish datasets then Pandas is the
right choice.  It's usable, widely understood by current and future employees,
efficient, and well maintained.


### Benefits of Parallelism

The performance benefit (or drawback) of using a parallel dataframe like Dask
dataframes or Spark dataframes over Pandas will differ based on the kinds of
computations you do:

1.  If you're doing small computations then Pandas is always the right choice.
    The administrative costs of parallelizing will outweigh any benefit.

2.  For simple operations like filtering, cleaning, and aggregating large data
    you should expect linear speedup by using a parallel dataframes.

    If you're on a 20-core computer you might expect a 20x speedup.  If you're
    on a 1000-core cluster you might expect a 1000x speedup, assuming that you
    have a problem big enough to spread across 1000 cores.  As you scale up
    administrative overhead will increase, so you should expect the speedup to
    decrease a bit.

2.  For complex operations like distributed joins it's more complicated.  You
    might get linear speedups like above, or you might even get slowdowns.
    Someone experienced in database-like computations and parallel computing
    can probably predict pretty well which computations will do well.


### There are other options to speed up Pandas

It's worth pointing out that many people looking to speed up Pandas don't need
parallelism.  There are often several other tricks like encoding text data,
using efficient file formats, avoiding groupby.apply, and so on that are more
effective at speeding up Pandas than switching to parallelism.


### Comparing Apache Spark and Dask

When it comes to dataframes Apache Spark and Dask are similar in some ways and
different in others.  At a high level ...

-  Spark dataframes will be much better when you have complex SQL-style queries
   (think 100+ line queries) where their query optimizer can kick in.
-  Dask dataframes will be much better when queries go outside of Spark's
   internal map-shuffle-reduce paradigm.  This happens most often in time
   series, random access, and other complex computations.
-  Spark will integrate better with JVM and data engineering technology. That
   is where it comes from.
-  Dask will integrate better with Python code.  A dask dataframe is just a
   bunch of Pandas dataframes, so if you're coming from Pandas it's usually
   pretty trivial to evolve to Dask.

Generally speaking though for most operations you'll be fine using either one.
But generally people often choose between Pandas/Dask and Spark based on
cultural preference.  Either they have people that really like the Python
ecosystem, or they have people that really like the Spark ecosystem.

Also dataframes are only a small part of each project.  Spark and Dask both do
many other things where the comparison is much more distinct.  Spark has a
graph analysis library, Dask doesn't.  Dask supports multi-dimensional arrays,
Spark doesn't.  Spark is generally higher level and all-in-one while Dask is
lower-level and focuses on integrating into other tools.


### Apache Arrow

> What about Arrow?  Is Arrow faster than Pandas?

This question doesn't make sense... yet.

Today, Arrow isn't a computational dataframe implementation; it's just a way to
move data around between different systems and file formats.  As a result, the
question of "is Arrow faster than Pandas" isn't actually a question that you
want answered today.  Arrow doesn't do any computation today.

However, this is likely to change in the future.  Arrow developers are planning
to write computational code around Arrow that we would expect to be faster than
the code in either Pandas or Spark.  This is probably a year or two away
though.  There will probably be some effort to make this semi-compatible with
Pandas, but it's much too early to tell.
