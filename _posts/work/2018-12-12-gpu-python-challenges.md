---
layout: post
title: First Impressions of GPUs and PyData
tagline: Opportunities and challenges to integrating GPUs into traditional data science workloads
category: work
tags: [Programming, Python, scipy, dask]
theme: twitter
---
{% include JB/setup %}

I recently [moved from Anaconda to NVIDIA](../../../2018/11/26/joining-nvidia)
within the RAPIDS team, which is building a PyData-friendly GPU-enabled data
science stack.  For my first week I explored some of the current challenges of
working with GPUs in the PyData ecosystem.  This post shares my first
impressions and also outlines plans for near-term work.

First, lets start with the value proposition of GPUs, significant speed
increases over traditional CPUs.


GPU Performance
---------------

Like many PyData developers, I'm loosely aware that GPUs are sometimes fast, but
don't deal with them often enough to have strong feeling about them.

To get a more visceral feel for the performance differences, I logged into a
GPU machine, opened up [CuPy](http://docs-cupy.chainer.org/en/stable/) (a
Numpy-like GPU library developed mostly by Chainer in Japan) and
[cuDF](https://cudf.readthedocs.io/en/latest/) (a Pandas-like library in
development at NVIDIA) and did a couple of small speed comparisons:

### Compare Numpy and Cupy

```python
>>> import numpy, cupy

>>> x = numpy.random.random((10000, 10000))
>>> y = cupy.random.random((10000, 10000))

>>> %timeit (np.sin(x) ** 2 + np.cos(x) ** 2 == 1).all()
402 ms ± 8.59 ms per loop (mean ± std. dev. of 7 runs, 1 loop each)

>>> %timeit (cupy.sin(y) ** 2 + cupy.cos(y) ** 2 == 1).all()
746 µs ± 1.26 ms per loop (mean ± std. dev. of 7 runs, 1 loop each)
```

On this mundane example, the GPU computation is a full 500x faster.


### Compare Pandas and cuDF

```python
>>> import pandas as pd, numpy as np, cudf

>>> pdf = pd.DataFrame({'x': np.random.random(10000000),
                        'y': np.random.randint(0, 10000000, size=10000000)})
>>> gdf = cudf.DataFrame.from_pandas(pdf)

>>> %timeit pdf.x.mean()  # 30x faster
50.2 ms ± 970 µs per loop (mean ± std. dev. of 7 runs, 10 loops each)
>>> %timeit gdf.x.mean()
1.42 ms ± 5.84 µs per loop (mean ± std. dev. of 7 runs, 1000 loops each)

>>> %timeit pdf.groupby('y').mean()  # 40x faster
1.15 s ± 46.5 ms per loop (mean ± std. dev. of 7 runs, 1 loop each)
>>> %timeit gdf.groupby('y').mean()
54 ms ± 182 µs per loop (mean ± std. dev. of 7 runs, 10 loops each)

>>> %timeit pdf.merge(pdf, on='y')  # 30x faster
10.3 s ± 38.2 ms per loop (mean ± std. dev. of 7 runs, 1 loop each)
>>> %timeit gdf.merge(gdf, on='y')
280 ms ± 856 µs per loop (mean ± std. dev. of 7 runs, 1 loop each)
```

This is a 30-40x speedup for normal dataframe computing.
Operations that previously took ten seconds
now process in near-interactive speeds.

*These were done naively on one GPU on a DGX machine.
The dataframe examples were cherry-picked to find supported operations
(see dataframe issues below).*


### Analysis

This speed difference is *potentially* transformative to a number of scientific
disciplines.  I intentionally tried examples that were more generic than
typical  deep learning workloads today, examples that might represent more
traditional scientific computing and data processing tasks.

GPUs seem to offer orders-of-magnitude performance increases over traditional
CPUs (at least in the naive cases presented above).  This speed difference is
an interesting lever for us to push on, and is what made me curious about
working for NVIDIA in the first place.


Roadblocks
----------

However, there are many reasons why people don't use GPUs for general purpose
computational programming today.
I thought I'd go through a few of them in this blogpost so we can see the sorts
of things that we would need to resolve.

-  Not everyone has a GPU.  They can be large and expensive
-  Installing CUDA-enabled libraries can be tricky, even with conda
-  Current CUDA-enabled libraries don't yet form a coherent ecosystem with
   established conventions
-  Many of the libraries around RAPIDS need specific help:
    -  cuDF is immature, and needs many simple API and feature improvements
    -  Array computing libraries need protocols to share data and functionality
    -  Deep learning libraries have functionality, but don't share functionality easily
    -  Deploying Dask on multi-GPU systems can be improved
    -  Python needs better access to high performance communication libraries

This is just my personal experience which, let me be clear, is only limited to
a few days.  I'm probably wrong about many topics I discuss below.


Not everyone has a GPU
----------------------

GPUs can be expensive and hard to put into consumer laptops,
so there is a simple availability problem.  Most people can't just crack open a
laptop, start IPython or a Jupyter notebook, and try something out immediately.

However, most data scientists, actual scientists, and students that I run into
today do have some access to GPU resources through their institution.  Many
companies, labs, and universities today have purchased a GPU cluster that, more
often than not, sits under-utilized.  These are often an `ssh` command away,
and generally available.

Two weeks ago I visited with Joe Hamman, a scientific collaborator at NCAR and
UW eScience institute and he said "Oh yeah, we have a GPU cluster at work that
I never use".  About 20 minutes later he had a GPU stack installed and was
running an experiment very much like what we did above.


Installing CUDA-enabled libraries is complicated by drivers
-----------------------------------------------------------

Before conda packages, wheels, Anaconda, and conda forge, installing the PyData
software stack (Numpy, Pandas, Scikit-Learn, Matplotlib) was challenging.  This
was because users had to match a combination of system libraries, compiler
stacks, and Python packages.  "Oh, you're on Mac?  First brew install X, then
make sure you have `gfortran`, then `pip install scipy`"

The ecosystem solved this pain by bringing the entire stack under the single
umbrella of conda where everything could be managed consistently, or
alternatively was greatly diminished with pip wheels.

Unfortunately, CUDA drivers have to be managed on the system side, so we're
back to matching system libraries with Python libraries, depending on what CUDA
version you're using.

Here are PyTorch's installation instructions as an example:

-  **CUDA 8.0:** `conda install pytorch torchvision cuda80 -c pytorch`
-  **CUDA 9.2:** `conda install pytorch torchvision -c pytorch`
-  **CUDA 10.0:** `conda install pytorch torchvision cuda100 -c pytorch`
-  **No CUDA:** `conda install pytorch-cpu torchvision-cpu -c pytorch`

Additionally, these conventions differ from the conventions used by
Anaconda's packaging of TensorFlow and NVIDIA's packaging of RAPIDS.  This
inconsistency in convention makes it unlikely that a novice user will get a
working system if they don't do some research ahead of time.  PyData survives
by courting non-expert computer users (they're often experts in some other
field) so this is a challenge.

There is some work happening in Conda that can help with this in the future.
Regardless, we will need to develop better shared conventions between the
different Python GPU development groups.


No community standard build infrastructure exists
-------------------------------------------------

After speaking about this with [John Kirkham](https://github.com/jakirkham)
(Conda Forge maintainer), he suggested that the situation is also a bit like
the conda ecosystem before conda-forge, where everyone built their own packages
however they liked and uploaded them to anaconda.org without agreeing on a
common build environment.  As much of the scientific community knows, this
inconsistency can lead to a fragmented stack, where certain families of
packages work well only with certain packages within their family.


Development teams are fragmented across companies
-------------------------------------------------

Many of the large GPU-enabled packages are being developed by large teams
within private institutions.  There isn't a strong culture of cross-team
collaboration.

After working with the RAPIDS team at NVIDIA for a week my sense is that this
is only due to being unaware of how to act, and not any nefarious purpose (or
they were very good at hiding that nefarious purpose).  I suspect that the
broader community will be able to bring these groups more into the open quickly
if they engage.


RAPIDS and Dask need specific attention
---------------------------------------

Now we switch and discuss technical issues in the RAPIDS stack,
and Dask's engagement with GPUs generally.
This will be lower-level,
but shows the kinds of things that I hope to work on technically over the coming months.

Generally the goal of RAPIDS is to build a data science stack around
conventional numeric computation that mimics the PyData/SciPy stack.  They
seem to be targeting libraries like:

-   Pandas by building a new library, [cuDF](https://cudf.readthedocs.io/en/latest/)
-   Scikit-Learn / traditional non-deep machine learning by building a new
    library [cuML](https://github.com/rapidsai/cuml)
-   Numpy by leveraging existing libraries like CuPy, PyTorch, TensorFlow,
    and focusing on improving interoperation within the ecosystem

Driven by the standard collection  of scientific/data centric applications like
imaging, earth science, ETL, finance, and so on.

Now lets talk about the current challenges for those systems.  In general, none
of this stack is yet mature (except for the array-computing-in-deep-learning
case).


cuDF is missing Pandas functionality
------------------------------------

When I showed cuDF at the top of this post,
I ran the following computations, which ran 30-40x as fast as Pandas..

```python
gdf.x.mean()
gdf.groupby('y').mean()
gdf.merge(gdf, on='y')
```

What I *failed* to show was that many operations erred.
The cuDF library has great promise, but still needs work filling out the Pandas
API.

```python
# There are many holes in the cuDF API
cudf.read_csv(...)      # works
cudf.read_parquet(...)  # fails if compression is present

df.x.mean()  # works
df.mean()    # fails

df.groupby('id').mean()     # works
df.groupby('id').x.mean()   # fails
df.x.groupby(df.id).mean()  # fails
```

Fortunately, this work is happening quickly
([GitHub issues](https://github.com/rapidsai/cudf/issues) seem to turn quickly into PRs)
and is mostly straightforward on the Python side.
This is a good opportunity for community members who are looking to have a quick impact.
There are lots of low-hanging fruit.

Additionally, there are areas where the cudf semantics don't match Pandas
semantics.  In general this is fine (not everyone loves Pandas semantics) but
it makes it difficult as we try to wrap Dask Dataframe around cuDF.  We would
like to grow Dask Dataframe so that it can accept Pandas-*like* dataframes and
so then get out-of-core GPU dataframes on a single node, and distributed GPU
dataframes on multi-GPU or multi-node, and we would like to grow cudf so that
it can fit into this expectation.

This work has to happen both at the low-level C++/CUDA code, and also at the
Python level.  The sense I get is that NVIDIA has a ton of people available at
the CUDA level, but only a few (very good) people at the Python level who are
working to keep up (come help!).


Array computing is robust, but fragmented
-----------------------------------------

The Numpy experience is much smoother, mostly because of the excitement
around deep learning over the last few years.  Many large tech companies have
made their own deep learning framework, each of which contains a partial clone
of the Numpy API.  These include libraries like TensorFlow, PyTorch,
Chainer/CuPy, and others.

This is great because these libraries provide high quality functionality to
choose from, but is also painful because the ecosystem is heavily fragmented.
Data allocated with TensorFlow can't be computed on with Numba or CuPy
operations.

We can help to heal this rift with a few technical approaches:

-   A standard to communicate low-level information about GPU arrays
    between frameworks.  This would include information about an array like a
    device memory pointer, datatype, shape, strides, and so on, similar to what
    is in the Python buffer protocol today.

    This would allow people to allocate an array with one framework, but then
    use computational operations defined in another framework.

    The Numba team prototyped something like this a few months ago, and the
    CuPy team seemed happy enough with it.
    See [cupy/cupy #1144](https://github.com/cupy/cupy/pull/1144)

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

    This was also, I believe, accepted into PyTorch.

-   A standard way for developers to write backend-agnostic array code.
    Currently my favorite approach is to use Numpy functions as a lingua
    franca, and to allow the frameworks to hijack those functions and interpret
    them as they will.

    This was proposed and accepted within Numpy itself in
    [NEP-0018](https://www.numpy.org/neps/nep-0018-array-function-protocol.html)
    and has been pushed forward by people like Stephan Hoyer, Hameer Abbasi,
    Marten van Kerkwijk, and Eric Wieser.

    This is also useful for other array libraries, like pydata/sparse and dask
    array, and would go a long way towards unifying operations with libraries
    like XArray.


cuML needs features, Scikit-Learn needs datastructure agnosticism
-----------------------------------------------------------------

While deep learning on the GPU is commonplace today, more traditional
algorithms like GLMs, random forests, preprocessing and so on haven't received
the same thorough treatment.

Fortunately the ecosystem is well prepared to accept work in this space,
largely because Scikit Learn established a simple pluggable API early on.
Building new estimators in external libraries that connect to the ecosystem
well is straightforward.

We should be able to build isolated estimators that can be dropped into
existing workflows piece by piece, leveraging the existing infrastructure
within other Scikit-Learn-compatible projects.

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


Deep learning frameworks are overly specialized
-----------------------------------------------

The SciPy/PyData stack thrived because it was modular and adaptable to new
situations.
There are many small issues around integrating components of the deep learning
frameworks into the more general ecosystem.

We went through a similar experience with Dask early on, when the Python
ecosystem wasn't ready for parallel computing.  As Dask expanded we ran into
many small issues around parallel computing that hadn't been addressed before
because, for the most part, few people used Python for parallelism at the time.

-  Various libraries didn't release the GIL (thanks for the work Pandas, Scikit-Image, and others!)
-  Various libraries weren't threadsafe in some cases (like h5py, and even Scikit-Learn in one case)
-  Function serialization still needed work (thanks `cloudpickle` developers!)
-  Compression libraries were unmaintained (like LZ4)
-  Networking libraries weren't used to high bandwidth workloads (thanks Tornado devs!)

These issues were fixed by a combination of Dask developers and
the broader community (it's amazing what people will do if you provide a
well-scoped and well-described problem on GitHub).  These libraries were
designed to be used with other libraries, and so they were well incentivized to
improve their usability by the broader ecosystem.

Today deep learning frameworks have these same problems.  They rarely serialize
well, aren't threadsafe when called by external threads, and so on.  This is to
be expected, most people using a tool like TensorFlow or PyTorch are
operating almost entirely within those frameworks.  These projects aren't being
stressed against the rest of the ecossytem (no one puts PyTorch arrays as
columns in Pandas, or pickles them to send across a wire).  Taking tools that
were designed for narrow workflows and encouraging them towards general
purpose collaboration takes time and effort, both technically and socially.

The non-deep-learning OSS community has not yet made a strong effort to engage
the deep-learning developer communities.  This should be an interesting social
experiment between two different of dev cultures.  I suspect that these
different groups have different styles and can learn from each other.

*Note: Chainer/CuPy is a notable exception here.  The Chainer library (another
deep learning framework) explicitly separates its array library, CuPy, which
makes it easier to deal with.  This, combined with a strict adherence to the
Numpy API, is probably why they've been the early target for most ongoing
Python OSS interactions.*


Dask needs convenience scripts for GPU deployment
-------------------------------------------------

On high-end systems it is common to have several GPUs on a single machine.
Programming across these GPUs is challenging because you need to think about
data locality, load balancing, and so on.

Dask is well-positioned to handle this for users.  However, most people using
Dask and GPUs today have a complex setup script that includes a combination of
environment variables, `dask-worker` calls, additional calls to CUDA profiling
utilities, and so on.  We should make a simple `LocalGPUCluster` Python
object that people can easily call within a local script, similar to how they
do today for `LocalCluster`.

Additionally, this problem applies to the multi-gpu-multi-node case, and will
require us to be creative with the existing distributed
deployment solutions
(like [dask-kubernetes](https://kubernetes.dask.org),
[dask-yarn](https://yarn.dask.org),
and [dask-jobqueue](https://jobqueue.dask.org)).
Of course, adding complexity like this without significantly impacting the
non-GPU case and adding to community maintenance costs will be an interesting
challenge, and will require creativity.


Python needs High Performance Communication libraries
-----------------------------------------------------

High-end GPU systems often use high-end networking.  This is especially
important when our compute times drop significantly because communication time
may quickly become our new bottleneck if we reduce computation time with GPUs.

Last year Antoine worked to improve Tornado's handling of high-bandwidth
connections to get about 1GB/s per process on Infiniband networks from Python.
We may need to go well above this, both for Infiniband and for more exotic
networking solutions.  In particular NVIDIA has systems that support efficient
transfer directly between GPU devices without going through host memory.

There is already work here that we can leverage.
The [OpenUCX](http://www.openucx.org/) project offloads exotic networking
solutions (like Infiniband) to a uniform API.  They're now working to provide a
Python accessible API that we can then then connect to Dask.  This is good
also for Dask-CPU users because Infiniband connections will become more
efficient (HPC users rejoice) and also for the general Python HPC community,
which will finally have a reasonable Python API for high performance
networking.  This work currently targets the Asyncio event loop.

*As an aside, this is the kind of work I'd like to see coming out of NVIDIA
(and other large technology companies) in the future.  It helps to connect
Python users to their specific hardware yes, but also helps lots of other
systems and provides general infrastructure applicable across the community at
the same time.*


Come help!
----------

This post outlined challenges surrounding the Python and GPU experience today.
NVIDIA's plan to build a GPU-compatible data science stack seems ambitious.
Fortunately, all of the challenges above seem to have straightforward
solutions, and NVIDIA seems to be treating the problem seriously, and seems
willing to put resources and company focus behind the problem.

If any of the work above sounds interesting to you please engage either as an
...

-  **Individual**: either as an open source contributor (RAPIDS is Apache 2.0
   licensed and seems to be operating as a normal OSS project on GitHub) or as
   an employee
   (see active [job postings](https://www.google.com/search?q=nvidia+rapids&ibp=htl;jobs#fpstate=tldetail&htidocid=PEj50HJ9NiABW4nJAAAAAA%3D%3D&htivrt=jobs)).

   There is lots of exciting work to do here.

   .. or as an ...

-  **Institution**: You may already have both an under-utilized cluster of GPUs
   within your institution, and also large teams of data scientists familiar
   with the Python but unfamiliar with CUDA.  NVIDIA seems eager to find
   partners who are interested in mutual arrangements to build out
   functionality for specific domains.  Please reach out if this sounds
   familiar.
