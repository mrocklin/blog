---
layout: post
title: Scientific Data in the Cloud
category: work
draft: True
tags: [Programming, Python, scipy, Pangeo]
theme: twitter
---
{% include JB/setup %}

Multi-dimensional data, such as is commonly stored in HDF and NetCDF formats, is difficult to access on traditional cloud storage platforms.
This post outlines the situation, current approaches, and their strengths and weaknesses.

Not Tabular Data
----------------

If your data fits into a tabular format,
such that you can use tools like SQL, Pandas, or Spark,
then this post is not relevant to you.
You should consider Parquet, ORC,
or any of a hundred other excellent formats that are well designed for use on cloud storage technologies.


Multi-Dimensional Data
----------------------

We're talking about data that is multi-dimensional and regularly strided.
This data often occurs in simulation output (like weather),
biomedical imaging (like an MRI scan),
or needs to be efficiently accessed across a number of different dimensions (like many complex time series).
Here is an image from XArray to put you in the right frame of mind:

<img src="{{BASE_PATH}}/images/xarray-boxes-2.png" width="100%">

This data is often stored in blocks such that, say,
each 100x100x100 chunk of data is stored together,
and can be accessed without reading through the rest of the file.

A few file formats allow this layout, the most popular of which is the HDF format, which has been the standard for decades.
HDF is a powerful and efficient format capable of handling both complex hierarchical data systems (filesystem-in-a-file)
and efficiently blocked numeric arrays.


The Opportunity and Challenge of Cloud Storage
----------------------------------------------

The scientific community generates several petabytes of HDF data annually.
Supercomputer simulations (like a large climate model) produce a few petabytes.
Planned NASA satellite missions will produce hundreds of petabytes a year.
All of these tend to be stored in HDF.

To increase access,
institutions now place this data on the cloud.
Hopefully this generates more social value from existing simulations and observations.

Unfortunately, the layout of HDF files makes it difficult to query them efficiently on cloud storage systems
(like Amazon's S3, Google's GCS, Microsoft's ADL).
The HDF format is complex and metadata is strewn throughout the file a complex sequence of reads within a binary blob of data.
The only pragmatic way to read a chunk of data from an HDF file today is to use the existing HDF C library,
which expects to receive a C `FILE` object, pointing to a normal file system
(not a cloud object store) (this is not entirely true, as we'll see below).

So organizations like NASA are dumping large amounts of HDF onto Amazon's S3,
that no one can actually read, except by downloading the entire file down to their hard drive,
and then pulling out the particular bits that they need.
This is inefficient.
It misses out on the potential that cloud-hosted public data can offer our to society.

The rest of this post discusses a few of the options to solve this problem,
including their advantages and disadvantages.

1.  **Cloud Optimized GeoTIFF:** We can use modern and efficient formats from other domains, like Cloud Optimized GeoTIFF

    **Good**: Fast, well established

    **Bad**: Not actually sophisticated enough to handle some scientific use cases

2.  **HDF + FUSE:** Continue using HDF, but mount cloud object stores as a file system with [Filesystem in Userspace, aka FUSE](https://en.wikipedia.org/wiki/Filesystem_in_Userspace)

    **Good:** Works with existing files, no changes to the HDF library necessary

    **Bad:** It's complex, probably not as fast as possible, and has historically been brittle

2.  **HDF + Custom Reader:** Continue using HDF, but teach it how to read from S3, GCS, ADL, ...

    **Good:** Works with existing files, no complex FUSE tricks

    **Bad:** Requires changes to the HDF library and all downstream libraries (like Python wrappers).  Probably not performance optimal

3.  **HDF + Web Service:** Continue using HDF, but buffer it with a distributed service

    **Good:** Works with existing files, probably decently fast, probably also works for efficient writes

    **Bad:** Complex to write and to deploy.  Probably not free.  It hides our data behind someone who owns and runs a service, introducing an intermediary.

4.  **New Formats for Scientific Data:** Design a new format, optimized for science use on the cloud

    **Good:** Fast, intuitive, and modern

    **Bad:** Not a community standard

Now we go into each option in more depth


Use Other Formats, like Cloud Optimized GeoTIFF
-----------------------------------------------

We could use formats other than HDF and NetCDF that are already well established.
The two that I hear most often proposed are Cloud Optimized GeoTIFF and Apache Parquet.
Both are efficient, well designed for cloud storage, and well established as community standards.
If you haven't already, I strongly recommend reading Chris Holmes' (Planet) blog series on [Cloud Native Geospatial](https://medium.com/tag/cloud-native-geospatial/latest).

These formats are well designed for cloud storage because they support random access well with relatively few communications and with relatively simple code.
If you needed to you could open up the Cloud Optimized GeoTIFF spec,
and with about an hour of reading,
get an image that you wanted using nothing but a couple of `curl` commands.
Metadata is in a clear centralized place.
That metadata provides enough information to issue further commands to get the relevant bytes from the object store.
Those bytes are stored in a format that is easily interpreted by a variety of common tools on all platforms.

However, neither of these formats are sufficiently expressive to handle some of the use cases of HDF and NetCDF.
Recall our image earlier about atmospheric data:

<img src="{{BASE_PATH}}/images/xarray-boxes-2.png" width="100%">

Our data isn't a parquet table, nor is it a stack of geo-images.
While it's true that you could store any data in these formats,
for example by saving each horizontal slice as a GeoTIFF,
or each spatial point in a Parquet table,
these storage layouts would be *inefficient* for regular access patterns.
Some parts of the scientific community *need* blocked layouts for multi-dimensional array data.


HDF and Filesystems in Userspace (FUSE)
---------------------------------------

We could access HDF data on the cloud *now* if we were able to convince our operating system that S3 or GCS or ADL were a normal file system.
This is a reasonable goal; cloud object stores look and operate much like normal file systems.
They have directories that you can list and navigate.
They have files/objects that you can copy, move, rename,
and from which you can read or write small sections.

We can achieve this using an operating systems trick, [FUSE, or Filesystem in Userspace](https://en.wikipedia.org/wiki/Filesystem_in_Userspace).
This allows us to make a program that the operating system treats as a normal file system.
Several groups have already done this for a variety of cloud providers.
Here is an example with the [gcsfs](https://gcsfs.readthedocs.org) Python library

```
$ pip install gcsfs --upgrade
$ mkdir /gcs
$ gcsfuse pangeo-data /gcs --background
Mounting bucket pangeo-data to directory gcs

$ ls /gcs
...
```

Now we point our HDF library to a NetCDF file in that directory
(which actually points to an object on Google Cloud Storage),
and it happily uses C File objects to read and write data.
The operating system passes the read/write requests to `gcsfs`,
which goes out to the cloud to get data, and then hands it back to the operating system, which hands it to HDF.
All normal HDF operations *just work*,
although they may now be significantly slower.
The cloud is further away than local disk.

This slowdown is significant because the HDF library makes many small 4kB reads
in order to gather the metadata necessary to pull out a chunk of data.
Each of those tiny reads made sense when the data was local,
but now that we're sending out a web request each time.
This means that users can sit for minutes just to open a file.

Fortunately, we can be clever.
By buffering and caching data, we can reduce the number of web requests.
For example, when asked to download 4kB we actually download 100kB or 1MB.
If some of the future 4kB reads are within this 1MB then we can return them immediately.,
Looking at HDF traces it looks like we can probably reduce "dozens" of web requests to "a few".

FUSE also requires elevated operating system permissions,
which can introduce challenges if working from Docker containers
(which is likely on the cloud).
Docker containers running FUSE need to be running in privileged mode.
There are some tricks around this, with Kubernetes, notably FlexVolumes,
but generally FUSE brings some excess baggage.


HDF and a Custom Reader
-----------------------

The HDF library doesn't *need* to use C File pointers,
we can extend it to use other storage backends as well.

This has already been done to support Amazon's S3 twice,

1.  Once by the [HDF group](https://www.hdfgroup.org/) (currently private private),
2.  Once by Joe Jevnik and Scott Sanderson (Quantopian) at [https://h5s3.github.io/h5s3/](https://h5s3.github.io/h5s3/) (highly [experimental](https://h5s3.github.io/h5s3/warnings.html))

This provides an alternative to FUSE.
This is better because it doesn't require privileged access,
but is worse because it only solves this problem for HDF and not all file access.

In either case we'll need to do look-ahead buffering and caching to get reasonable performance.


Centralize Metadata
-------------------

Alternatively, we might centralize metadata in one place so that we can avoid many hops through the file.
This could be within the HDF format itself, or in a separate side-file.

This would remove the need to perform clever file-system caching and buffering tricks,
but requires some work on the HDF library itself.


HDF + Web Service
-----------------

We could offload this problem to a for-profit entity,
like the [HDF group](https://www.hdfgroup.org/) or a cloud provider (Google, Amazon, Microsoft).
They would solve this problem however they like,
and expose a web API that we can hit for our data.

This would be distributed service of several computers on the cloud near our data
that will take our requests for what data we want,
perform whatever tricks they deem appropriate to get that data,
and then deliver it to us.
This fleet of machines will still have to address the problems listed above,
but we can let them figure it out, and presumably they'll learn as they go.

However, this is somewhat complex, and creates an intermediary between us and our data.

The HDF group is working on such a service, HSDS that works on Amazon's S3 (or anything that looks like S3).
They have created a [h5pyd](https://github.com/HDFGroup/h5pyd) library that is a drop-in replacement for the popular [h5py](https://github.com/HDFGroup/h5pyd) Python library.

Presumably a cloud provider, like Amazon, Google, or Microsoft could do this as well.
By providing open standards like [OpenDAP](https://www.opendap.org/) they might attract more science users onto their platform
to more efficiently query their cloud-hosted datasets.


New Formats for Scientific Data
-------------------------------

Alternatively, we can move on from the HDF file format,
and invent a new data storage specification that fits cloud storage
(or other storage)
more cleanly without worrying about supporting the legacy layout of existing HDF files.

This has already been going on, informally, for years.
Most often we see people break large arrays into blocks,
store each block as a separate object in the cloud object store with a suggestive name,
and store a metadata file describing how the blocks relate to each other.
This looks something like the following:

```
/metadata.json
/0.0.0.dat
/0.0.1.dat
/0.0.2.dat
 ...
/10.10.8.dat
/10.10.9.dat
/10.10.10.dat
```

There are many variants:

- They might extend this to have groups or sub-arrays in sub-directories.
- They might choose to compress the individual blocks in the `.dat` files or not.
- They might choose different encoding schemes for the metadata and the binary blobs.

But generally most array people on the cloud do something like this with their research data,
and they've been doing it for years.
It works efficiently,
is easy to understand and manage,
and transfers well to any cloud platform,
onto a local file system,
or even into a standalone zip file or small database.

There are two groups that have done this in a more mature way,
defining both modular standalone libraries to manage their data,
as well as proper specification documents that inform others how to interpret this data in a long-term stable way.

-  [Zarr](http://zarr.readthedocs.io/en/stable/)
-  [N5](https://github.com/saalfeldlab/n5)

These are both well maintained and well designed libraries (by my judgment),
in Python and Java respectively.
They offer layouts like the layout above, although with more sophistication.
Entertainingly [their](https://github.com/saalfeldlab/n5#filesystem-specification-version-100) [specs](http://zarr.readthedocs.io/en/stable/spec/v2.html) are similar enough that another library,
[Z5](https://github.com/constantinpape/z5),
built a cross-compatible parser for each in C++.
This unintended uniformity is a good sign.
It means that both developer groups were avoiding creativity,
and have converged on a sensible common solution.
I encourage you to read the [Zarr Spec](http://zarr.readthedocs.io/en/stable/spec/v2.html) in particular.

However, technical merits are not alone sufficient to justify a shift in data format,
especially for archival datasets of record that we're discussing.
The institutions in charge of this data and have multi-decade horizons and so move slowly.
For them, moving off of the historically community standard would be major shift.

And so we need to answer a couple of difficult questions:

1.  How hard is it to make HDF efficient in the cloud?
2.  How hard is it to shift the community to a new standard?
