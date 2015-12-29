---
layout: post
title: Disk Bandwidth
category : work
tags : [scipy, Python, Programming, dask, blaze]
---
{% include JB/setup %}

*This work is supported by [Continuum Analytics](http://continuum.io)
and the [XDATA Program](http://www.darpa.mil/program/XDATA)
as part of the [Blaze Project](http://blaze.pydata.org)*

**tl;dr: Disk read and write bandwidths depend strongly on block size.**

Disk read/write bandwidths on commodity hardware vary between 10 MB/s (or
slower) to 500 MB/s (or faster on fancy hardware).  This variance can be
characterized by the following rules:

1.  Reading/writing large blocks of data is faster than
    reading/writing small blocks of data
2.  Reading is faster than writing
3.  Solid state drives are faster than spinning disk *especially for
    many small reads/writes*

In [this notebook](https://gist.github.com/07bb67d99dc5d15341f9) we experiment
with the dependence of disk bandwidth on file size.  The result of this
experiment is the following image, which depicts the read and write bandwidths
of a commercial laptop SSD as we vary block size:

![]({{ BASE_PATH }}/images/disk-bandwidth.png)


Analysis
--------

We see that this particular hard drive wants to read/write data in chunksizes
of 1-100 MB.  If we can arrange our data so that we consistently pull off
larger blocks of data at a time then we can read through data quite quickly
at 500 MB/s.  We can churn through a 30 GB dataset in one minute.
Sophisticated file formats take advantage of this by storing similar data
consecutively.  For example column stores store all data within a single column
in single large blocks.


Difficulties when measuring disk I/O
------------------------------------

Your file system is sophisticated.  It will buffer both reads and writes in RAM
as you think you're writing to disk.  In particular, this guards your disk
somewhat against the "many small writes" regime of terrible performance.  This
is great, your file system does a fantastic job (bringing write numbers up from
0.1 MB/s to 20 MB/s or so) but it makes it a bit tricky to benchmark properly.
In the experiment above we `fsync` each file after write to flush write buffers
and explicitly clear all buffers before entering the read section.

Anecdotally I also learned that my operating system caps write speeds at 30
MB/s when operating off of battery power.  This anecdote demonstrates how
particular your hard drive may be when controlled by a file system.  It is worth
remembering that your hard drive is a physical machine and not just a
convenient abstraction.
