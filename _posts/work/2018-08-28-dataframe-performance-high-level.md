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

### Pandas and Dask Dataframe

Dask dataframes are parallel Pandas dataframes.  They use the exact same code
underneath, just called many times.  The performance benefit (or drawback) of
using Dask dataframes over Pandas dataframes will differ based on the kinds of
computations you're doing:

1.  If you're doing small computations then Pandas is always the right choice.
    The administrative costs of parallelizing will outweigh any benefit.

2.  For simple operations like filtering, cleaning, and aggregating large data
    you should expect linear speedup by using Dask dataframes.

    If you're on a 20-core computer you might expect a 20x speedup.  If you're
    on a 1000-core cluster you might expect a 1000x speedup, assuming that you
    have a problem big enough to spread across 1000 cores.  As you scale up you
    should expect the speedup to decrease a bit, but generally this is an easy
    problem to parallelize.

2.  For complex operations like distributed joins it's more complicated.  You
    might get linear speedups like above, or you might even get slowdowns.
    Someone experienced in database-like computations and parallel computing
    can probably predict pretty well which computations will do well.
    Dask.dataframe looks like any parallel database-like system here.

It's worth pointing out that many people looking to speed up Pandas don't need
Dask.  There are often several other tricks like using categorical data,
efficient file formats, avoiding groupby.apply, and so on that are more
effective at speeding up Pandas than switching to parallelism with Dask.


### Apache Spark

It used to be that Apache Spark's dataframe implementation was very very slow.
This is no longer the case; Spark is pretty well optimized these days.  There
are situations where performance is better or worse than Pandas/Dask.

-  Spark works about as well as Pandas for simple operations
-  Spark will perform better when you get into complex SQL style queries due to
   better query optimization (think 100+ line queries with many joins and
   filters)
-  Spark will perform worse when you get outside of what is easy to do in the
   simple map-shuffle-reduce paradigm.  This is painful when you get to things
   like time series, random access, and so on.

But generally people often choose between Pandas/Dask and Spark based on
cultural preference.  Either they have people that really like the Python
ecosystem, or they have people that really like the Spark ecosystem.


### Apache Arrow

Today, Arrow isn't a computational dataframe implementation, it's just a way to
move data around between different systems and file formats.  As a result, the
question of "is Arrow faster than Pandas" isn't actually a question that you
want answered today.  Arrow does do any computation today.

However, this is likely to change in the future.  Arrow developers are planning
to write computational code around Arrow that we would expect to be faster than
the code in either Pandas or Spark.  This is probably a year or two away
though.
