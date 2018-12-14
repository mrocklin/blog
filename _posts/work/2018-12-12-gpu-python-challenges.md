---
layout: post
title: PyData, GPUs, First Impressions, and Future Work
category: work
draft: true
tags: [Programming, Python, scipy, dask]
theme: twitter
---
{% include JB/setup %}

For my first full week at NVIDIA I explored some of the challenges of working
with GPUs in the PyData ecosystem.
This post shares my first impressions
and plans for near-term work.
I'll mostly focus on technical details around Dask, GPUs, and PyData


GPU Performances Presents an Opportunity
----------------------------------------

Like many PyData developers, I'm loosely aware that GPUs can be quite fast, but
it's not really something that I think much about (until recently).  To get a
more visceral feel for the performance differences, I logged into a GPU
machine, opened up CuPy (a Numpy-like GPU library developed mostly by Chainer
in Japan) and cuDF (a Pandas-like library in development at NVIDIA) and did a
couple of small speed comparisons:

### Numpy/Cupy

TODO, speed comparisons

### Pandas/cuDF

TODO, speed comparisons

I intentionally tried things that weren't deep learning, and that might
instead be representative of normal scientific computing and data processing.

GPUs do offer an orders-of-magnitude performance difference over traditional
CPUs (at least in the naive cases presented above).  This represents an
opportunity that GPUs could offer to general computing.  This speed difference
's one of the reasons that made me curious about working for NVIDIA in the
first place.

Roadblocks
----------

But there are many reasons why people don't use GPUs for general purpose
computational programming today.
I thought I'd go through a few of them here.

This is just my personal experience which, let me be clear, is limited to a few
days.  I'm probably wrong about lots of things below.


Not everyone has a GPU
----------------------

GPUs can be expensive and hard to put into consumer laptops,
so there is a simple availability problem.  Most people can't just crack open a
laptop, start IPython or a Jupyter notebook, and try something out immediately.

However, most data scientists, actual scientists, and students that I run into
today do have some access to GPU resources through their institution.  Many
companies, labs, and universities today seem to have purchased some sort of GPU
cluster that, more often than not, sits idle.  These are often an `ssh` command
away, and generally available.

Two weeks ago I was visiting Joe Hamman, a scientific collaborator at NCAR and
UW eScience institute and he said "Oh yeah, we have a GPU cluster at work that
I never use".  About 20 minutes later he had a GPU stack installed and was
running an experiment very much like what we did above.


Installation and Drivers
------------------------

Before conda packages, wheels, Anaconda and conda forge, installing the PyData
software stack (Numpy, Pandas, Scikit-Learn, Matplotlib) was challenging.  This
was because users had to match a combination of system libraries, compiler
stacks, and Python packages.  "Oh, you're on Mac?  First brew install X, then
make sure you have `gfortran`, then `pip install scipy`"

The ecosystem solved this pain when we were able to bring the entire stack
under the one umbrella of conda, or alternatively was greatly diminished with
wheels.

Unfortunately, CUDA drivers have to be managed by the system side, so we're
back to matching system libraries with Python libraries, depending on what CUDA
version you're using.

Here are PyTorch's installation instructions as an example:

-  CUDA 8.0: `conda install pytorch torchvision cuda80 -c pytorch`
-  CUDA 9.2: `conda install pytorch torchvision -c pytorch`
-  CUDA 10.0: `conda install pytorch torchvision cuda100 -c pytorch`
-  No CUDA: `conda install pytorch-cpu torchvision-cpu -c pytorch`

Additionally, these conventions also differ from the conventions used by
Anaconda's packaging of TensorFlow and NVIDIA's packaging of RAPIDS.  It is
again unlikely that a novice user will get a working system if they don't do
some research ahead of time.

There is some work happening in Conda that can help with this in the future.
Regardless, we will need to develop better shared conventions between the
different Python GPU development groups.

After speaking about this with [John Kirkham](https://github.com/jakirkham)
(Conda Forge maintainer), he suggested that the situation is also a bit like
the conda ecosystem before conda-forge, where everyone built their own packages
however they liked and uploaded them to anaconda.org without agreeing on a
common build environment.  As much of the scientific community knows, this
inconsistency can lead to a fragmented stack, where certain families of
packages work well only with certain packages within their family.


Community fragmentation
-----------------------

Many of the large GPU-enabled packages are being developed by large teams
within private institutions.  There isn't a strong culture of cross team
collaboration.

After working with the RAPIDS team at NVIDIA for a week my sense is that this
is only due to being unaware of how to act, and not any nefarious purpose (or
they were very good at hiding that purpose).  I suspect that the broader
community will be able to bring these groups more into the open.


Technical issues around RAPIDS, Dask, and RAPIDS + Dask
-------------------------------------------------------

I'm going to switch now and talk about a few technical issues in the RAPIDS
stack, and Dask's engagement with GPUs and this space generally.  This will be
lower-level, but shows the kinds of things that I hope to work on technically
over the coming months.

Generally the goal of RAPIDS is to build a data science stack around
conventional numeric computation that mimics the PyData/SciPy stack.  They
seem to be targeting libraries like:

-   Pandas by building a new library, [cuDF](https://cudf.readthedocs.io/en/latest/)
-   Scikit-Learn / traditional non-deep machine learning by building a new
    library [cuML](https://github.com/rapidsai/cuml)
-   Numpy by leveraging existing libraries like CuPy, PyTorch, TensorFlow (Jax?)
    and focusing on improving interoperation within the ecosystem

Driven by the standard slew of scientific/data centric applications like
imaging, earth science, ETL, finance, and so on.

Now lets talk about the current challenges for those systems.  In general, none
of this stack is yet mature (except for array computing in the deep-learning
case).


Pandas/cuDF
-----------

I showed cuDF at the top of this post when talking about speed.  I ran the
following computations, which worked well.

```python
df = cudf.read_csv(...)
df.x.mean()
df[df.x > 100]
df.groupby('id').x.mean()
```

What I failed to show was that many operations erred.
The library can do some things, but is far from complete.

```python
# There are many holes in the cuDF API
cudf.read_csv(...)      # works
cudf.read_parquet(...)  # fails if compression is present

df.x.mean()  # works
df.mean()    # fails

df.groupby('id').x.mean()   # works
df.x.groupby(df.id).mean()  # fails
df = cudf.read_parquet(...)  # with compression
```

Additionally, there are areas where the cudf semantics don't match Pandas
semantics.  In general this is fine (not everyone loves Pandas semantics) but
it makes it difficult as we try to wrap Dask Dataframe around cudf.  We would
like to grow Dask Dataframe so that it can accept Pandas-*like* dataframes and
so then get out-of-core GPU dataframes on a single node, and distributed GPU
dataframes on multi-GPU or multi-node, and we would like to grow cudf so that
it can fit into this expectation.

This work has to happen both at the low-level C++/CUDA code, and also at the
Python level.  The sense I get is that NVIDIA has a ton of people available at
the CUDA level, but only a few (very good) people at the Python level who are
working to keep up (come help!).


Numpy/cupy/PyTorch/Tensorflow
-----------------------------

The Numpy story is generally smoother, mostly because of the excitement around
deep learning over the last few years.  It seems like most large tech companies
have made their own deep learning framework, each of which contains a partial
clone of the Numpy API.

This is great, because there is a ton of good functionality to choose from, but
somewhat painful, because the ecosystem here is fragmented.  There are some
things that would be good to see going forward to heal this rift:

-   A standard way to communicate low-level information about arrays between
    frameworks like device memory pointer, datatype, shape, and so on.  This
    would allow people to allocate an array with one framework, but then use
    computational operations defined in another framework.

    The Numba team prototyped something a few months ago, and the CuPy team
    seemed happy with it.  See [cupy/cupy #1144](https://github.com/cupy/cupy/pull/1144)

    ```python
    @property
    def __cuda_array_interface__(self):
        desc = {
            'shape': self.shape,
            'typestr': self.dtype.str,
            'descr': self.dtype.descr,
            'data': (self.data.mem.ptr, False),
            'version': 0,
        }
        if not self._c_contiguous:
            desc['strides'] = self._strides
         return desc
    ```

-   A standard way for developers to write backend-agnostic array code.
    Currently my favorit approach to this is to use Numpy functions as a lingua
    franca, but allow the frameworks to hijack those functions and interpret
    them as they will.

    This has been proposed and accepted within Numpy itself in
    [NEP-0018](https://www.numpy.org/neps/nep-0018-array-function-protocol.html)
    and has been pushed forward by people like Stephan Hoyer, Hameer Abbasi,
    Marten van Kerkwijk, and Eric Wieser.

    This is also useful for other array libraries, like pydata/sparse and dask
    array, and would go a long way towards unifying operations with libraries
    like XArray.


Scikti-Learn / cuML
-------------------

Scikit Learn fortunately established a pretty simple API early on, so building
new estimators in external libraries that connect to the ecosystem well is
pretty straightforward.

```python
# This code is aspirational
from sklearn.model_selection import RandomSearchCV
from sklearn.pipeline import make_pipeline
from sklearn.feature_extraction.text import TfidfTransformer

# from sklearn.feature_extraction.text import HashingVectorizer
from cuml.feature_extraction.text import HashingVectorizer  # swap out for GPU versions

# from sklearn.linear_model import LogisticRegression, RandomForest
from cuml.linear_model import LogisticRegression, RandomForest

pipeline = make_pipeline([HashingVectorizer(),  # use Scikit-Learn infrastructure
                          TfidfTransformer(),
                          LogisticRegression()])

RandomSearchCV(pipeline).fit(data, labels)
```

*Note, the example above is aspirational (that cuml code doesn't exist yet) and
probably naive (I don't know ML well).*

However, aside from the straightforward task of building these GPU-enabled
estimators (which seems to be routine for the CUDA developers at NVIDIA) there
are still challenges around cleanly passing non-Numpy arrays around, coercing
only when necessary, and so on that we'll need to work out within Scikit-Learn.

Fortunately this work has already started because of Dask Array, which has the
same problem.  The Dask and Scikit-Learn communities have been collaborating to
better enable pluggability over the last year.  Hopefully this additional use
case proceeds along these existing efforts, but now with more support.


The Deep Learning Frameworks
----------------------------

There are many small issues around integrating pieces of the deep learning
frameworks into a more general purpose ecosystem.

We went through a similar experience with Dask early on, when the Python
ecosystem wasn't ready for parallel computing.  As Dask expanded we ran into
many small issues around parallel computing that hadn't been addressed before
because, for the most part, few people used Python for parallelism at the time.

-  Various libraries didn't release the GIL (thanks for the work Pandas, Scikit-Image, and others!)
-  Various libraries weren't threadsafe in some cases (like h5py, and even Scikit-Learn in one case)
-  Function serialization still needed work (thanks `cloudpickle` developers!)
-  Compression libraries were unmaintained (like LZ4)
-  Networking libraries weren't used to high bandwidth workloads (thanks Tornado devs!)

These things were all fixed by some combination of Dask developers and
the broader community (it's amazing what people will do if you provide a
well-scoped and well-described problem on GitHub).  These libraries were
designed to be used with other libraries, and so they were well incentivized to
make themselves easy to work with.

The deep learning frameworks have these same sorts of problems.
They often don't serialize well, don't operate well when called in multiple
threads, and so on.  This is to be expected, most people to date using a tool
like TensorFlow or PyTorch are just using TensorFlow or PyTorch.  They're not
using it in concert with the rest of the ecossytem.
Taking tools that were designed for fairly narrow workflows and encouraging
them towards general purpose collaboration in an ecosystem of tools takes some
time and effort, both technically and socially.

The non-deep-learning OSS community hasn't really made a strong effort to
engage the deep-learning developer communities yet.  I think that this will be
an interesting experiment in interactions between two different kinds of dev
groups.  I suspect that they have different styles, and can likely learn from
each other.

*Note: Chainer/CuPy is an interesting exception here.  The Chainer library
(another deep learning framework common in Japan) explicitly separated out its
array library CuPy, which makes it much easier to deal with.  This, combined
with a strict adherence to the Numpy API, is probably why they've been the
early target for most ongoing Python OSS interactions.*


Deploying Dask around GPUs
--------------------------

On high-end systems it is common to have several GPUs on a single machine.
Programming across these GPUs is challenging because you need to think about
data locality, load balancing, and so on.

Dask is well-positioned to handle this for users (a multi-GPU node looks a bit
like a small multi-node CPU cluster) and indeed this is why many Dask+GPU users
use Dask today.  However, most people doing this today have some arcane script
to set things up that includes a combination of environment variables,
`dask-worker` calls, additional calls to CUDA profiling utilities and so on.
We should probably make a simple `LocalGPUCluster` Python object that people
can call easily within a local script, similar to how they do today for
`LocalCluster`.

This problem also carries over to the multi-gpu multi-node case, and will
probably require us to get a bit creative with the existing distributed
deployment solutions (like dask-kubernetes, dask-yarn, and dask-jobqueue).  Of
course, adding complexity like this without significantly impacting the non-GPU
case or adding to community maintenance costs will be an interesting challenge,
and will likely require some creativity.


Communication
-------------

High-end GPU systems often use high-end networking.  This becomes especially
important if our compute times drop significantly (the relative time spent
communicating may increase sharply if we can reduce computation time with GPUs).

Last year Antoine spent a bit of time improving Tornado's handling of
high-bandwidth connections to get something like 1GB/s per process on
Infiniband networks.  We may need to go well above this, both for Infiniband and
for more exotic networking solutions.  In particular NVIDIA has systems that
support efficient transfer directly between GPU devices without going through
host memory.

There is already some work here that we can leverage.  The
[OpenUCX](http://www.openucx.org/) project offloads exotic networking solutions
(like Infiniband) to a uniform API.  They're now working to provide a Python
accessible API, that we'll then connect through to Dask.  This is good also for
Dask-CPU users because Infiniband connections will become more efficient (HPC
users rejoice) and also for the general Python HPC community, which will
finally get a reasonable Python API to high performance networking.  This is
currently targeting the Asyncio event loop.

As an aside, this is exactly the kind of work I'd like to see more of coming
out of NVIDIA in the future.  It helps connect Python users to their hardware
yes, but also helps lots of other systems and provides general infrastructure
at the same time.


Come help
---------

To me, NVIDIA's plan here to build a GPU-compatible data science stack seems
ambitious.  However, they also seem to be treating the problem seriously, and
seem willing to put resources and company focus behind the problem.

If any of the work above sounds interesting to you please engage either as an
...

-  **Individual**: either as an open source contributor (RAPIDS is Apache 2.0
   licensed and seems to be operating as a normal OSS project, while Dask is
   BSD) or as an employee (see active [job
   postings](https://www.google.com/search?q=nvidia+rapids&ibp=htl;jobs#fpstate=tldetail&htidocid=PEj50HJ9NiABW4nJAAAAAA%3D%3D&htivrt=jobs)).

   There is lots of exciting work to do here.

   .. or as an ...

-  **Institution**: You may already have both a cluster of GPUs going unused
   within your institution, and large teams of data scientists familiar with
   the Python but unfamiliar with CUDA.  NVIDIA seems eager to find partners
   who are interested in cost-sharing arrangements to build out functionality
   for specific domains.  Please reach out if this sounds familiar.
