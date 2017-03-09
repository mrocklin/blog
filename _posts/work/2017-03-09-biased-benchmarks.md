---
layout: post
title: Biased Benchmarks
tagline: honesty is hard
category: work
tags: [Programming, Python, scipy]
theme: twitter
---
{% include JB/setup %}

*This work is supported by [Continuum Analytics](http://continuum.io)
the [XDATA Program](http://www.darpa.mil/program/XDATA)
and the Data Driven Discovery Initiative from the [Moore
Foundation](https://www.moore.org/)*

Summary
-------

Performing benchmarks to compare software is surprisingly difficult to do
fairly, even assuming the best intentions of the author.  Technical developers
can fall victim to a few natural human failings:

1.  We judge other projects by our own objectives rather than the objectives under which that project was developed
2.  We fail to use other projects with the same expertise that we have for our own
3.  We naturally gravitate towards cases at which our project excels
4.  We improve our software during the benchmarking process
5.  We don't release negative results

We discuss each of these failings in the context of current benchmarks I'm
working on comparing Dask and Spark Dataframes.


Introduction
------------

Last week I started comparing performance between Dask Dataframes (a project
that I maintain) and Spark Dataframes (the current standard).  My initial
results showed that Dask.dataframes were overall *much* faster, somewhere like
5x.

These results were wrong.  They're weren't wrong in a factual sense, the
experiments that I ran were clear and reproducible, but there was so much bias
in how I selected, set up, and ran those experiments that the end result was
misleading.  After checking results myself and then having other experts come
in and check my results I now see much more sensible numbers.  At the moment
both projects are within a factor of two most of the time, with some
interesting exceptions either way.

This blogpost outlines the ways in which library authors can fool themselves
when performing benchmarks, using my recent experience as an anecdote.  I hope
that this encourages authors to check themselves, and encourages readers to be
more critical of numbers that they see in the future.

This problem exists as well in academic research.  For a pop-science rendition
I recommend ["The Experiment Experiment" on the Planet Money
Podcast](http://www.npr.org/sections/money/2016/01/15/463237871/episode-677-the-experiment-experiment).


Skewed Objectives
-----------------

*Feature X is so important.  I wonder how the competition fares?*

Every project is developed with different applications in mind and so has
different strengths and weaknesses.  If we approach a benchmark caring only
about our original objectives and dismissing the objectives of the other
projects then we'll very likely trick ourselves.

For example consider reading CSV files.  Dask's CSV reader is based off of
Pandas' CSV reader, which was the target of great effort and love; this is
because CSV was so important to the finance community where Pandas grew up.
Spark's CSV solution is less awesome, but that's less about the quality of
Spark and more a statement about how Spark users tend not to use CSV.  When
they use text-based formats they're much more likely to use line-delimited
JSON, which is typical in Spark's common use cases (web diagnostics, click
logs, etc..)  Pandas/Dask came from the scientific and finance worlds where CSV
is king while Spark came from the web world where JSON reigns.

Conversely, Dask.dataframe hasn't bothered to hook up the `pandas.read_json`
function to Dask.dataframe yet.  Surprisingly it rarely comes up.  Both
projects can correctly say that the other project's solution to what they
consider the standard text-based file format is less-than-awesome.  Comparing
performance here either way will likely lead to misguided conclusions.

So when benchmarking data ingestion maybe we look around a bit, see that both
claim to support Parquet well, and use that as the basis for comparison.


Skewed Experience
-----------------

*Whoa, this other project has a lot of configuration parameters!  Lets just use
the defaults*

Software is often easy to set up, but often requires experience set up
optimally.  Authors are naturally more adept at setting up their own software
than the software of their competition.

My original (and flawed) solution to this was to "just use the defaults" on
both projects.  Given my inability to tune Spark (there are several dozen
parameters) I decided to also not tune Dask and run under default settings.  I
figured that this would be a good benchmark not only of the software, but also
on choices for sane defaults, which is a good design principle in itself.

This failed spectacularly because I was making unconscious decisions like the
size of machines that I was using for the experiment, CPU/memory ratios, etc..
It turns out that Spark's defaults are optimized for *very small machines* (or
more likely, small YARN containers) and use only 1GB of memory per executor by
default while Dask is typically run on larger boxes or has the full use of a
single machine in a single shared-memory process.  My standard cluster
configurations were biased towards Dask before I even considered running a
benchmark.

Similarly the APIs of software projects are complex and for any given problem
there is often both a fast way and a general-but-slow way.  Authors naturally
choose the fast way on their own system but inadvertently choose the general
way that comes up first when reading documentation for the other project.  It
often takes months of hands-on experience to understand a project well enough
to definitely say that you're not doing things in a dumb way.

In both cases I think the only solution is to collaborate with someone that
primarily uses the other system.


Preference towards strengths
----------------------------

*Oh hey, we're doing **really** well here.  This is great!  Lets dive into this a
bit more.*

It feels great to see your project doing well.  This emotional pleasure
response is powerful.  It's only natural that we pursue that feeling more,
exploring different aspects of it.  This can skew our writing as well.  We'll
find that we've decided to devote 80% of the text to what originally seemed
like a small set of features, but which now seems like *the main point*.

It's important that we define a set of things we're going to study ahead of
time and then stick to those things.  When we run into cases where our project
fails we should take that as an opportunity to raise an issue for future
(though not current) development.


Tuning during experimentation
-----------------------------

*Oh, I know why this is slow.  One sec, let me change something in the code.*

I'm doing this right now.  Dask dataframe shuffles are generally slower than
Spark dataframe shuffles.  On numeric data this used to be around a 2x
difference, now it's more like a 1.2x difference (at least on my current
problem and machine).  Overall this is great, seeing that another project was
beating Dask motivated me to dive in [(see dask/distributed
#932)](https://github.com/dask/distributed/issues/932) and this will result in
a better experience for users in the future.  As a developer this is also how I
operate.  I define a benchmark, profile my code, identify bottlenecks, and
optimize.  Business as usual.

However as an author of a comparative benchmark this also somewhat dishonest;
I'm not giving the Spark developers the same opportunity to find and fix
similar performance issues in their software before I publish my results.  I'm
also giving a biased picture to my readers.  I've made all of the pieces that
I'm going to show off fast while neglecting the others.  Picking benchmarks,
optimizing the project to make them fast, and then publishing those results
gives the incorrect impression that the entire project has been optimized to
that level.


Omission
--------

*So, this didn't go as planned.  Lets wait a few months until the next release.*

There is no motivation to publish negative results.  Unless of course you've
just written a blogpost announcing that you plan to release benchmarks in the
near future.  Then you're really forced to release numbers, even if they're
mixed.

That's ok, mixed numbers can be informative.  They build trust and
community.  And we all talk about open source community driven software, so
these should be welcome.


Straight up bias
----------------

*Look, we're not in grad-school any more.  We've got to convince companies to
actually use this stuff.*

Everything we've discussed so far assumes best intentions, that the author is
acting in good faith, but falling victim to basic human failings.

However many developers today (including myself) are paid and work for
for-profit companies that need to make money.  To an increasing extent making
this money depends on community mindshare, which means publishing
benchmarks that sway users to our software.  Authors have bosses that
they're trying to impress or the content and tone of an article may be
influenced by other people within the company other than the stated author.

I've been pretty lucky working with Continuum Analytics (my employer) in that
they've been pretty hands-off with technical writing.  For other
employers that may be reading, we've actually had an easier time getting
business because of the honest tone in these blogposts in some cases.
Potential clients generally have the sense that we're trustworthy.

Technical honesty goes a surprisingly long way towards implying technical
proficiency.
