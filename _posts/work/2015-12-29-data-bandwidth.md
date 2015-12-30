---
layout: post
title: Data Bandwidth
category : work
tags : [scipy, Python, Programming, dask, blaze]
---
{% include JB/setup %}

*This work is supported by [Continuum Analytics](http://continuum.io)
and the [XDATA Program](http://www.darpa.mil/program/XDATA)
as part of the [Blaze Project](http://blaze.pydata.org)*

**tl;dr: We list and combine common bandwidths relevant in data science**

Understanding data bandwidths helps us to identify bottlenecks and write
efficient code.  Both hardware and software can be characterized by how
quickly they churn through data.  We present a rough list of relevant data
bandwidths and discuss how to use this list when optimizing a data pipeline.

<table>
  <thead>
    <tr> <th>Name</th> <th>Bandwidth MB/s</th> </tr>
  </thead>
<tbody>
  <tr> <td> Memory copy </td> <td> 3000 </td> </tr>
  <tr> <td> Basic filtering in C/NumPy/Pandas </td> <td> 3000 </td> </tr>
  <tr> <td> Fast decompression </td> <td> 1000 </td> </tr>
  <tr> <td> SSD Large Sequential Read</td> <td> 500 </td> </tr>
  <tr> <td> Interprocess communication (IPC) </td> <td> 300 </td> </tr>
  <tr> <td> msgpack deserialization </td> <td> 125 </td> </tr>
  <tr> <td> Gigabit Ethernet </td> <td> 100 </td> </tr>
  <tr> <td> Pandas read_csv </td> <td> 100 </td> </tr>
  <tr> <td> JSON Deserialization </td> <td> 50 </td> </tr>
  <tr> <td> Slow decompression (e.g. gzip/bz2) </td> <td> 50 </td> </tr>
  <tr> <td> SSD Small Random Read </td> <td> 20 </td> </tr>
  <tr> <td> Wireless network </td> <td> 1 </td> </tr>
</tbody>
</table>

*Disclaimer: all numbers in this post are rule-of-thumb and vary by situation*

Understanding these scales can help you to identify how to speed up your
program.  For example, there is no need to use a faster network or disk
if you store your data as JSON.


Combining bandwidths
--------------------

Complex data pipelines involve many stages.  The rule to combine bandwidths is
to add up the inverses of the bandwidths, then take the inverse again:

$$ \textrm{total bandwidth} = \left(\sum_i \frac{1}{x_i}\right)^{-1} $$

This is the same principle behind adding conductances in serial within
electrical circuits.   One quickly learns to optimize the slowest link in the
chain first.


### Example

When we read data from disk (500 MB/s) and then deserialize it from JSON (50 MB/s)
our full bandwidth is 45 MB/s:

$$\left(\frac{1}{500} + \frac{1}{50}\right)^{-1} = 45.4 $$

If we invest in a faster hard drive system that has 2GB of read
bandwidth then we get only marginal performance improvement:

$$\left(\frac{1}{2000} + \frac{1}{50}\right)^{-1} = 48.8 $$

However if we invest in a faster serialization technology, like msgpack (125
MB/s), then we double our effective bandwidth.

$$\left(\frac{1}{500} + \frac{1}{125}\right)^{-1} = 100 $$

This example demonstrates that we should focus on the weakest bandwidth first.
Cheap changes like switching from JSON to msgpack can be more effective than
expensive changes, like purchasing expensive hardware for fast storage.


### Overlapping Bandwidths

We can overlap certain classes of bandwidths.  In particular we can often
overlap communication bandwidths with computation bandwidths.  In our disk+JSON
example above we can probably hide the disk reading time completely.  The same
would go for network applications *if* we handle sockets correctly.


### Parallel Bandwidths

We can parallelize some computational bandwidths.  For example we can
parallelize JSON deserialization by our number of cores to quadruple the
effective bandwidth `50 MB/s * 4 = 200 MB/s`.  Typically communication
bandwidths are not parallelizable per core.
