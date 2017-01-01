---
layout: post
title: Distributed NumPy on a Cluster with Dask Arrays
category: work
draft: true
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

We analyze a stack of images in parallel with NumPy arrays distributed across a
cluster of machines on Amazon's EC2 with Dask array.  This is a model
application shared among many image analysis groups ranging from satelite
imagery to bio-medical applications.  We go through a series of common
operations:

1.  Inspect a sample of images locally with Scikit Image
2.  Construct a distributed Dask.array around all of our images
3.  Process and re-center images with Numba
4.  Transpose data to get a time-series for every pixel, compute FFTs

This last step is quite fun.  Even if you skim through the rest of this article
I recommend checkout out the last section.


Inspect Dataset
---------------

I asked a colleague at the US National Institutes for Health (NIH) for a
biggish imaging dataset.  He came back with the following message:

*Electron microscopy is probably generating the biggest ndarray datasets in the field - terabytes regularly. Neuroscience need EM to see connections between neurons because the critical features of neural synapses (connections) are below the diffraction limit of light microscopes. The hard part is machine vision on the data to follow small neuron parts from one slice to the next.  This type of research has been called "connectomics".*

This data is from drosophila: [http://emdata.janelia.org/](http://emdata.janelia.org/). Here is an example 2d slice of the data [http://emdata.janelia.org/api/node/bf1/grayscale/raw/xy/2000_2000/1800_2300_5000](http://emdata.janelia.org/api/node/bf1/grayscale/raw/xy/2000_2000/1800_2300_5000).

```python
import skimage.io
import matplotlib.pyplot as plt

sample = skimage.io.imread('http://emdata.janelia.org/api/node/bf1/grayscale/raw/xy/2000_2000/1800_2300_5000'
skimage.io.imshow(sample)
```

<a href="{{ BASE_PATH }}/images/dask-imaging-sample.png">
  <img src="{{ BASE_PATH }}/images/dask-imaging-sample.png"
         alt="Sample electron microscopy image from stack"
                width="60%"></a>

The last number in the URL is an index into a large stack of about 10000 images.  We can change that number to get different slices through our 3D dataset.

```python
samples = [skimage.io.imread('http://emdata.janelia.org/api/node/bf1/grayscale/raw/xy/2000_2000/1800_2300_%d'
% i) for i in [1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000]]

fig, axarr = plt.subplots(1, 9, sharex=True, sharey=True, figsize=(24, 2.5))
for i, sample in enumerate(samples):
    axarr[i].imshow(sample, cmap='gray')
```

<a href="{{ BASE_PATH }}/images/dask-imaging-row.png">
  <img src="{{ BASE_PATH }}/images/dask-imaging-row.png"
         alt="Sample electron microscopy images over time"
                width="100%"></a>

We see that our field of interest moves a bit over time.


Create a Distributed Array
--------------------------

Even though our data is spread across many files, we still want to think of it
as a single logical 3D array.  We know how to get any particular 2D slice of
that array using Scikit-image.  Now we're going to use Dask.array to stitch
all of those scikit-image calls into a single distributed array.

```python
import dask.array as da
from dask import delayed

imread = delayed(skimage.io.imread, pure=True)  # Lazy version of imread

urls = ['http://emdata.janelia.org/api/node/bf1/grayscale/raw/xy/2000_2000/1800_2300_%d' % i
        for i in range(10000)]  # A list of our URLs

lazy_values = [imread(url) for url in urls]     # Lazily evaluate imread

arrays = [da.from_delayed(lazy_value,           # Construct a small Dask array
                          dtype=sample.dtype,   # for every lazy value
                          shape=sample.shape)
          for lazy_value in lazy_values]

stack = da.stack(arrays, axis=0)                # Stack all small Dask arrays into one

>>> stack
dask.array<shape=(10000, 2000, 2000), dtype=uint8, chunksize=(1, 2000, 2000)>

>>> stack = stack.rechunk((20, 2000, 2000))  # to reduce overhead
>>> stack
dask.array<shape=(10000, 2000, 2000), dtype=uint8, chunksize=(20, 2000, 2000)>
```

So here we've constructed a lazy Dask.array from many delayed calls to
`skimage.io.imread`.  We haven't done any actual work yet, we've just
constructed a parallel array that knows how to get any particular slice of data
if necessary.  This gives us a full NumPy-like abstaction on top of all of
these remote images.  For example we can now download a particular image
just by slicing our Dask array.

```python
>>> stack[5000, :, :].compute()
array([[0, 0, 0, ..., 0, 0, 0],
       [0, 0, 0, ..., 0, 0, 0],
       [0, 0, 0, ..., 0, 0, 0],
       ...,
       [0, 0, 0, ..., 0, 0, 0],
       [0, 0, 0, ..., 0, 0, 0],
       [0, 0, 0, ..., 0, 0, 0]], dtype=uint8)

>>> stack[5000, :, :].mean().compute()
11.49902425
```

However we probably don't want to operate too much further without connecting
to a cluster.  That way we can just download all of the images once into
distributed RAM and start doing some real computations.

```python
from dask.distributed import Client, progress
client = Client('localhost:8786')

>>> client
<Client: scheduler="localhost:8786" processes=10 cores=80>
```

And lets go ahead and bring in all of our images, persisting the array into
concrete data in memory.

```python
stack = client.persist(stack)
```

This the downloads across our 10 processes.  When this completes we have 10 000
NumPy arrays spread around on our cluster, coordinated by our single Dask
array.  This takes a while, about five minutes.  We're mostly network bound
here (Janelia's servers are not co-located with our compute nodes).  Here is a
parallel profile of the computation.  You can see every Python function that
ran over time on every worker (y-axis).  You can hover over each rectangle
(task) for more information on what kind of task it was, how long it took,
etc..

<iframe src="https://cdn.rawgit.com/mrocklin/e09cad939ff7a85a06f3b387f65dc2fc/raw/fa5e20ca674cf5554aa4cab5141019465ef02ce9/task-stream-image-load.html"
        width="800" height="400"></iframe>

Now our Dask array is based on hundreds of concrete in-memory NumPy arrays
across the cluster, rather than based on hundreds of lazy scikit-image calls.
Now we can do all sorts of fun distributed array computations quickly.

For example we can easily see our field of interest move across the frame by
averaging across time:

```python
skimage.io.imshow(stack.mean(axis=0))
```

<a href="{{ BASE_PATH }}/images/dask-imaging-time-mean.png">
  <img src="{{ BASE_PATH }}/images/dask-imaging-time-mean.png"
         alt="Avergage image over time"
                width="100%"></a>

<iframe src="https://cdn.rawgit.com/mrocklin/e09cad939ff7a85a06f3b387f65dc2fc/raw/fa5e20ca674cf5554aa4cab5141019465ef02ce9/task-stream-image-mean-time.html"
        width="800" height="400"></iframe>

Or we can see when the field of interest is actually present within the frame
by averaging across x and y

```python
plt.plot(stack.mean(axis=[1, 2]))
```

<a href="{{ BASE_PATH }}/images/dask-imaging-spatial-mean.png">
  <img src="{{ BASE_PATH }}/images/dask-imaging-spatial-mean.png"
         alt="Image brightness over time"
                width="100%"></a>

<iframe src="https://cdn.rawgit.com/mrocklin/e09cad939ff7a85a06f3b387f65dc2fc/raw/fa5e20ca674cf5554aa4cab5141019465ef02ce9/task-stream-image-mean-spatial.html"
        width="800" height="400"></iframe>

By looking at the profile plots for each case we can see that averaging over
time involves much more inter-node communication, which can be quite expensive
in this case.


Recenter Images with Numba
--------------------------

In order to remove the spatial offset across time we're going to compute a
centroid for each slice and then crop the image around that center.  I looked
up centroids in the Scikit-Image docs but came across a function that did *way*
more than what I was looking for, so I just quickly coded up a solution in Pure
Python and then JIT-ed it with [Numba](http://numba.pydata.org/) (which makes
this run at C-speeds).

```python
from numba import jit

@jit(nogil=True)
def centroid(im):
    n, m = im.shape
    total_x = 0
    total_y = 0
    total = 0
    for i in range(n):
        for j in range(m):
            total += im[i, j]
            total_x += i * im[i, j]
            total_y += j * im[i, j]

    if total > 0:
        total_x /= total
        total_y /= total
    return total_x, total_y

>>> centroid(sample)  # this takes around 9ms
(748.7325324581344, 802.4893005160851)
```

```python
def recenter(im):
    x, y = centroid(im.squeeze())
    x, y = int(x), int(y)
    if x < 500:
        x = 500
    if y < 500:
        y = 500
    if x > 1500:
        x = 1500
    if y > 1500:
        y = 1500

    return im[..., x-500:x+500, y-500:y+500]

plt.figure(figsize=(8, 8))
skimage.io.imshow(recenter(sample))
```

<a href="{{ BASE_PATH }}/images/dask-imaging-recentered-sample.png">
  <img src="{{ BASE_PATH }}/images/dask-imaging-recentered-sample.png"
       alt="Recentered image"
       width="40%"></a>


Now we map this function across our distributed array.

```python
import numpy as np
def recenter_block(block):
    """ Recenter a short stack of images """
    return np.stack([recenter(block[i]) for i in range(block.shape[0])])

recentered = stack.map_blocks(recenter, chunks=(1, 1000, 1000),
                              dtype=a.dtype)
recentered = client.persist(recentered)
```

<iframe src="https://cdn.rawgit.com/mrocklin/e09cad939ff7a85a06f3b387f65dc2fc/raw/fa5e20ca674cf5554aa4cab5141019465ef02ce9/task-stream-image-recentering.html"
        width="800" height="400"></iframe>

This profile provides a good opportunity to talk about a scheduling *failure*;
things went a bit wrong here.  Towards the beginning we quickly recenter
several images (Numba is fast) however then as some workers finish all of their
work the scheduler erroneously starts to load balance, moving images from busy
workers to idle workers.  Unfortunately the network at this time appeared to be
much slower than expected and so the move + compute elsewhere strategy ended up
being much slower than just letting the busy workers finish their work.  The
scheduler keeps track of expected compute times and transfer times precisely to
avoid mistakes like this one.  These sorts of issues are rare, but do occur on
occasion.

We check our work and see that, indeed, our images are better centered with
each other.

```python
skimage.io.imshow(recentered.mean(axis=0))
```

<a href="{{ BASE_PATH }}/images/dask-imaging-recentered-time-mean.png">
  <img src="{{ BASE_PATH }}/images/dask-imaging-recentered-time-mean.png"
       alt="Recentered time average"
       width="40%"></a>

This shows how easy it is to create fast in-memory code with Numba and then
scale it out with Dask.array.  The two projects complement each other nicely,
giving us near-optimal performance with intuitive code across a cluster.

<iframe src="https://cdn.rawgit.com/mrocklin/e09cad939ff7a85a06f3b387f65dc2fc/raw/fa5e20ca674cf5554aa4cab5141019465ef02ce9/task-stream-image-recenter-mean-time.html"
        width="800" height="400"></iframe>

Rechunk to Time Series
----------------------

We're now going to rearrange our data from being partitioned by time slice, to
being partitioned by pixel.  This will allow us to run computations like Fast
Fourier Transforms (FFTs) on each time series efficiently.  Switching the chunk
pattern back and forth like this is generally a very difficult operation for
distributed arrays because every slice of the array contributes to every
time-series.  We have N-squared communication.

This analysis may not be appropriate for this data, but it's a very frequent
request, so I wanted to include it.

Currently our Dask array has chunkshape (20, 1000, 1000), meaning that our data
is collected into 500 NumPy arrays across the cluster, each of size `(20, 1000,
1000)`.

```python
>>> recentered
dask.array<shape=(10000, 1000, 1000), dtype=uint8, chunksize=(20, 1000, 1000)>
```

But we want to change this shape so that the chunks cover the entire first
axis.  We could do something like the following:

```python
>>> rechunked = recentered.rechunk((10000, 1, 1))
```

However this would result in one million chunks (there are one million pixels)
which will result in a bit of overhead.  Instead we'll collect our time-series
into `10 x 10` groups of one hundred pixels.  This will help us to reduce
overhead.

```python
>>> rechunked = recentered.rechunk((10000, 10, 10))
```

Now we'll compute the FFT of each pixel, take the absolute value and square to
get the power spectrum.  Finally to conserve space we'll down-grade the dtype
to float32 (our original data is only 8-bit anyway.

```python
x = da.fft.fft(rechunked, axis=0)
power = abs(x ** 2).astype('float32')

power = client.persist(power, optimize_graph=False)
```

This is a fun profile to inspect.  We've included a real-time trace during
execution, the full profile, as well as some diagnostics plots from a single
worker.  These plots total up to around 20MB.  I sincerely apologize to those
without broadband access.

<a href="{{ BASE_PATH }}/images/task-stream-fft.gif">
  <img src="{{ BASE_PATH }}/images/task-stream-fft.gif"
         alt="Dask task stream of rechunk + fft"
                width="100%"></a>

<iframe src="https://cdn.rawgit.com/mrocklin/e09cad939ff7a85a06f3b387f65dc2fc/raw/fa5e20ca674cf5554aa4cab5141019465ef02ce9/task-stream-image-fft.html"
        width="800" height="400"></iframe>

<a href="{{ BASE_PATH }}/images/worker-state-fft.png">
  <img src="{{ BASE_PATH }}/images/worker-state-fft.png"
         alt="Worker communications during FFT"
                width="45%"></a>
<a href="{{ BASE_PATH }}/images/worker-communications-fft.png">
  <img src="{{ BASE_PATH }}/images/worker-communications-fft.png"
         alt="Worker communications during FFT"
                width="45%"></a>

This computation starts with a lot of communication while we rechunk and
realign our data (recent optimizations here by [Antoine
Pitrou](https://github.com/pitrou) in [dask #417](https://github.com/dask/dask/pull/1737).
Then we transition into doing thousands of small FFTs and other arithmetic
operations.  During all of this inter-worker communication was around
100-300 MB/s (typical for Amazon's EC2) and CPU load remained high.  We're
using our hardware.

Finally we can inspect the results.  We see that the power spectrum is very
boring the corner, and has typical activity towards the center of the image

<a href="{{ BASE_PATH }}/images/dask-imaging-fft-0.png">
  <img src="{{ BASE_PATH }}/images/dask-imaging-fft-0.png"
         alt="Power spectrum near edge"
                width="70%"></a>

<a href="{{ BASE_PATH }}/images/dask-imaging-fft-center.png">
  <img src="{{ BASE_PATH }}/images/dask-imaging-fft-center.png"
         alt="Power spectrum at center"
                width="70%"></a>

Final Thoughts
--------------

This blogpost showed a non-trivial image processing workflow, emphasizing the
following points:

1.  Constructing a Dask array from a stack of Python function calls.  In this
    case using SKImage, but we could have use anything.
2.  Using the NumPy syntax with Dask.array to do standard array manipulations
    on data spread across a cluster of machines
3.  Building an efficient centroid function with Numba, showing how Numba and
    Dask.array complement each other well
4.  Rechunking an array that was distributed by time slice into an array that
    was distributed as time-series by pixel, a common and challenging operation

Hopefully this example has components that look similar to what you want to do
with your data on your hardware.  We would love to see more applications like
this out there in the wild.
