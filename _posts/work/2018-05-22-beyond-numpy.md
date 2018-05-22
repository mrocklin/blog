---
layout: post
title: Beyond Numpy Arrays in Python
tagline: Protocols for GPU, distributed, and sparse arrays for Python
draft: true
category: work
tags: [Programming, Python, scipy, dask]
theme: twitter
---
{% include JB/setup %}

Executive Summary
-----------------

There are now several implementations of Numpy's array API for
GPU, sparse, and distributed arrays.

With moderate effort we can define a subset of the Numpy API that works well across all of them,
allowing the ecosystem to more smoothly transition between hardware.

This post describes the opportunities and challenges to accomplishing this.


Context: Array Implementations
------------------------------

The foundational NumPy library represents multidimensional gridded data,
such as is common in satellite and biomedical imagery, super-computer simulations,
financial models, genomics, and thousands of other domains critical to our society.
The Numpy array is one of the foundations of the numeric Python ecosystem,
and serves as the standard model for similar libraries in other languages.

However, Numpy was designed several years ago,
and its implementation no longer reflects modern hardware trends to
multi-core workstations, many-core GPUs, and distributed clusters.

Fortunately other libraries in the ecosystem implement the Numpy array API on these other architectures:

-  [CuPy](https://cupy.chainer.org/): implements the Numpy API on GPUs with CUDA
-  [Sparse](https://sparse.pydata.org/): implements the Numpy API for sparse arrays that are mostly zeros
-  [Dask array](https://dask.pydata.org/): implements the Numpy API in parallel for multi-core workstations or distributed clusters

So even when the Numpy implementation is no longer ideal,
the Numpy API lives on in successor projects.

*Note: the Numpy implementation remains ideal most of the time.
Dense in-memory arrays are still the common case.
This blogpost is about the minority of cases where Numpy is not ideal*

We can write code very similar code between all of
Numpy, GPU, sparse, and parallel arrays:

```python
import numpy as np
x = np.random.random(...)
y = x.T.dot(np.log(x) + 1)
z = y - y.mean(axis=0)
print(z[:5])

import cupy as cp
x = cp.random.random(...)
y = x.T.dot(cp.log(x) + 1)
z = y - y.mean(axis=0)
print(z[:5].get())

import dask.array as da
x = da.random.random(...)
y = x.T.dot(da.log(x) + 1)
z = y - y.mean(axis=0)
print(z[:5].compute())

...
```

Additionally, each of the deep learning frameworks
(TensorFlow, PyTorch, MXNet)
has a Numpy-like thing that is *similar-ish* to Numpy's API,
but definitely not trying to be an exact match.


Context: Algorithmic Libraries
------------------------------

Simultaneous to the development of Numpy-like arrays for different hardware,
many libraries build algorithmic functionality on top of the Numpy API:

1.  [XArray](http://xarray.pydata.org/en/stable/) for labeled and indexed collections of arrays
2.  [Autograd](https://github.com/hips/autograd) and [Tangent](https://github.com/google/tangent/): for automatic differentiation
3.  [TensorLy](http://tensorly.org/stable/index.html) for higher order array factorizations
4.  [Dask array](https://dask.pydata.org) which coordinates many Numpy-like arrays into a logical parallel array

    (dask array both *consumes* and *implements* the Numpy API)
5.  ...

These enhance array computing in Python, building on new features beyond what Numpy itself provides.

Additionally, there are many other libraries like Pandas, Scikit-Learn, SciPy, etc.
that use the Numpy API *and* its internal representation (they dive into the dense in-memory representation).
We're going to ignore these libraries for the purposes of this blogpost
and focus only on those that only use the high-level Numpy API
and not the low-level representation.


Opportunities and Challenges
----------------------------

So now that we have these new Numpy-like arrays,
and these new Numpy-enhancing algorithmic libraries,
we would like to use them together.
This will enable the ecosystem to scale and transition more easily
between different hardware contexts.

We would like to apply the new algorithmic functionality
(labels, automatic differentiation, parallelism, ...)
to the new implementations
(GPUs, sprase, parallel, ...)
and to all future implementations that might follow.

Unfortunately,
while all of the array implementations APIs are *very similar* to Numpy's API,
they do technically use different functions.

```python
>>> numpy.sin is cupy.sin
False
```

This creates problems for the algorithmic libraries mentioned above,
because now they need to switch out which functions they use,
depending on which array-like objects they've been given.
To resolve these problems
each of the array projects mentioned above
implements a custom plugin system
that they use to switch between
a few of the array options.
We include links to these plugin mechanisms below if you're interested in
looking at code:

-  [xarray/core/duck_array_ops.py](https://github.com/pydata/xarray/blob/master/xarray/core/duck_array_ops.py)
-  [tensorly/backend](https://github.com/tensorly/tensorly/tree/master/tensorly/backend)
-  [autograd/numpy/numpy_vspaces.py](https://github.com/HIPS/autograd/blob/master/autograd/numpy/numpy_vspaces.py)
-  [tangent/template.py](https://github.com/google/tangent/blob/master/tangent/template.py)
-  [dask/array/core.py#L51-L54](https://github.com/dask/dask/blob/master/dask/array/core.py#L51-L54)

For example XArray can use either Numpy arrays or Dask arrays.
This has been hugely beneficial to users of that project,
which today seamlessly transition from small in-memory datasets on their laptops
to 100TB datasets on clusters,
all using the same programming model.

However building, maintaining, and extending these plugin mechanisms is *costly*.
These bits of plugin code in each project are not alike.
Any new array implementation has to go to each library and build more-or-less the same code several times.
Similarly any new algorithmic library has to build plugins to every ndarray implementation.
Each library has to explicitly import and understand each other library,
and has to adapt as those libraries change over time.
This coverage is not complete,
and so users lack confidence that their applications are portable between hardware.

Pair-wise plugin mechanisms make sense for a single project,
but are not an efficient choice for the full ecosystem.


Solutions
---------

I see two solutions today:

1.  Build a new library that holds dispatch-able versions of all of the relevant Numpy functions
    and convince everyone to use it instead of Numpy internally

2.  Build this dispatch mechanism into Numpy itself

Each has challenges.


### Build a new centralized plugin library

We can build a new library,
here called `arrayish`,
that holds dispatch-able versions of all of the relevant Numpy functions.
We then convince everyone to use it instead of Numpy internally.

So in each array-like library's codebase we write code like the following:

```python
# inside numpy's codebase
import arrayish
import numpy
@arrayish.sin.register(numpy.ndarray, numpy.sin)
@arrayish.cos.register(numpy.ndarray, numpy.cos)
@arrayish.dot.register(numpy.ndarray, numpy.ndarray, numpy.dot)
...
```

```python
# inside cupy's codebase
import arrayish
import cupy
@arrayish.sin.register(cupy.ndarray, cupy.sin)
@arrayish.cos.register(cupy.ndarray, cupy.cos)
@arrayish.dot.register(cupy.ndarray, cupy.ndarray, cupy.dot)
...
```

and so on for Dask, Sparse, and any other Numpy-like libraries.

In all of the algorithm libraries (like XArray, autograd, TensorLy, ...)
we use arrayish instead of Numpy

```python
# inside XArray's codebase
# import numpy
import arrayish as numpy
```

This is the same plugin solution as before,
but now we build a community standard plugin system
that hopefully all of the projects can agree to use.

This reduces the big `n by m` cost of maintaining several plugin systems,
to a more managable `n plus m` cost of using a single plugin system in each library.
This centralized project would also benefit, perhaps,
from being better maintained than any individual project is likely to do on its own.

However this has costs:

1.  Getting many different projects to agree on a new standard is hard
2.  Algorithmic projects will need to start using arrayish internally,
    adding new imports like the following:

    ```python
    import arrayish as numpy
    ```

    And this wll certainly cause some complications interally

3.  Someone needs to build an maintain the central infrastructure

Hameer Abbasi put together a rudimentary prototype for arrayish here: [github.com/hameerabbasi/arrayish](https://github.com/hameerabbasi/arrayish).
There has been some discussion about this topic, using XArray+Sparse as an example, in [pydata/sparse #1](https://github.com/pydata/sparse/issues/1)


### Dispatch from within Numpy

Alternatively, the central dispatching mechanism could live within Numpy itself.

Numpy functions could learn to hand control over to their arguments,
allowing the array implementations to take over when possible.
This would allow existing Numpy code to work on externally developed array implementations.

There is precedent for this.
The [`__array_ufunc__`](https://docs.scipy.org/doc/numpy/reference/arrays.classes.html#numpy.class.__array_ufunc__) protocol
allows any class that defines the `__array_ufunc__` method
to take control of any Numpy ufunc like `np.sin` or `np.exp`.
Numpy reductions like `np.sum` already look for `.sum` methods on their arguments and defer to them if possible.

Some array projects, like Dask and Sparse, already implement the `__array_ufunc__` protocol.
There is also [an open PR for CuPy](https://github.com/cupy/cupy/pull/1247).
Here is an example showing Numpy functions on Dask arrays cleanly.

```python
>>> import numpy as np
>>> import dask.array as da

>>> x = da.ones(10, chunks=(5,))  # A Dask array

>>> np.sum(np.exp(x))             # Apply Numpy function to a Dask array
dask.array<sum-aggregate, shape=(), dtype=float64, chunksize=()>  # get a Dask array
```

*I recommend that all Numpy-API compatible array projects implement the `__array_ufunc__` protocol.*

This works for many functions, but not all.
Other operations like `tensordot`, `concatenate`, and `stack`
occur frequently in algorithmic code but are not covered here.

This solution avoids the community challenges of the `arrayish` solution above.
Everyone is accustomed to aligning themselves to Numpy's decisions,
and relatively little code would need to be rewritten.

The challenge with this approach is that historically
Numpy has moved more slowly than the rest of the ecosystem.
For example the `__array_ufunc__` protocol mentioned above
was discussed for several years before it was merged.
Fortunately Numpy has recently
[received](https://www.numfocus.org/blog/numpy-receives-first-ever-funding-thanks-to-moore-foundation)
[funding](https://bids.berkeley.edu/news/bids-receives-sloan-foundation-grant-contribute-numpy-development)
to help it make changes like this more rapidly.
The full time developers hired under this funding have just started though,
and it's not clear how much of a priority this work is for them at first.

For what it's worth I'd prefer to see this Numpy protocol solution take hold.


Final Thoughts
--------------

In recent years Python's array computing ecosystem has grown organically to support
GPUs, sparse, and distributed arrays.
This is wonderful and a great example of the growth that can occur in decentralized open source development.

However to solidify this growth and apply it across the ecosystem we now need to do some central planning
to move from a pair-wise model where packages need to know about each other
to a ecosystem model where packages can negotiate by developing and adhering to community-standard protocols.

The community has done this transition before
(Numeric + Numarray -> Numpy, the Scikit-Learn fit/predict API, etc..)
usually with surprisingly positive results.

The open questions I have today are the following:

1.  How quickly can Numpy adapt to this demand for protocols
    while still remaining stable for its existing role as foundation of the ecosystem
2.  What algorithmic domains can be written in a cross-hardware way
    that depends only on the high-level Numpy API,
    and doesn't require specialization at the data structure level.
    Clearly some domains exist (XArray, automatic differentiation),
    but how common are these?
3.  Once a standard protocol is in place,
    what other array-like implementations might arise?
    In-memory compression?  Probabilistic?  Symbolic?
