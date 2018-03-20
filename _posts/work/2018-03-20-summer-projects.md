---
layout: post
title: Summer Student Projects 2018
category: work
draft: true
tags: [Programming, scipy, Python]
theme: twitter
---
{% include JB/setup %}

Around this time of year students look for Summer projects.
Often they get internships at potential future employers.
Sometimes they become more engaged in open source software.

This blogpost contains some projects that I think are appropriate for a summer
student in a computational field.  They reflect my biases (which, assuming you
read my blog, you're ok with) and are by no means comprehensive of
opportunities within the Scientific Python ecosystem.  To be perfectly clear
I'm only providing ideas and context here,
I offer neither funding nor mentorship.


### Criteria for a good project

2.  Is well defined and tightly scoped
    to reduce uncertainty about what a successful outcome looks like,
    and to reduce the necessity for high-level advising
3.  Is calibrated so that an industrious student can complete it in a few months
4.  It's useful, but also peripheral.
    It has value to the ecosystem but is not critical enough
    that a core devs is likely to complete the task in the next few months,
    or be overly picky about the implementation.
5.  It's interesting, and is likely to stimulate thought within the student
6.  It teaches valuable skills that will help the student in a future job search
7.  It can lead to future work, if the student makes a strong connection

The projects listed here target someone who already has decent knowledge of the
fundamentals PyData or SciPy ecosystem (numpy, pandas, general understanding of
programming, etc..).
They are somewhat focused around Dask and other projects that I personally work on.


### Distributed GPU NDArrays with CuPy, Bohrium, or other

Dask arrays coordinate many NumPy arrays to operate in parallel.
It includes all of the parallel algorithms,
leaving the in-memory implementation to NumPy chunks.

But the chunk arrays don't actually have to be NumPy arrays,
they just have to look similar enough to NumPy arrays to fool Dask Array.
We've done this before with [sparse arrays](http://dask.pydata.org/en/latest/array-sparse.html)
which implement a subset of the `numpy.ndarray` API, but with sparse storage,
and it has worked nicely.

There are a few GPU NDArray projects out there that satisfy much of the NumPy interface:

-  [CuPy](https://cupy.chainer.org/)
-  [Bohrium](http://bohrium.readthedocs.io/)
-  ...

It would be valuable to do the same thing with Dask Array with them.
This might give us a decent general purpose distributed GPU array relatively cheaply.
This would engage the following:

1.  Knowledge of GPUs and performance implications of using them
2.  NumPy protocols (assuming that the GPU library will still need some changes to make it fully compatible)
3.  Distributed performance, focusing on bandwidths between various parts of the architecture
4.  Profiling and benchmarking

Github issue for conversation is here: [dask/dask #3007](https://github.com/dask/dask/issues/3007)


### Use Numba and Dask for Numerical Simulations

While Python is very popular in data analytics
it has been less successful in hard-core numeric algorithms and simulation,
which are typically done in C++/Fortran and MPI.
This is because Python is perceived to be too slow for serious numerical computing.

Yet with recent advances in Numba for fast in-core computing and Dask for parallel computing things may be changing.
Certainly fine-tuned C++/Fortran + MPI can out-perform Numba and Dask,
but by how much?
If the answer is only 10% or so then it could be that the lower barrier to entry of Numba,
or the dynamic scaling of Dask,
can make them competitive in fields where Python has not previously had a major impact.

For which kinds of problems is a dynamic JITted language almost-as-good as C++/MPI?
For which kinds of problems is the dynamic nature of these tools valuable,
either due to more rapid development,
greater flexibility in accepting community created modules,
dynamic load balancing,
or other reasons?

This project would require the student to come in with an understanding of their own field,
the kinds of computational problems that are relevant there,
and an understanding of the performance characteristics
that might make dynamic systems tolerable.
They would learn about optimization and profiling,
and would characterize the relevant costs of dynamic languages in a slightly more modern era.


### Blocked Numerical Linear Algebra

Dask arrays contain some algorithms for blocked linear algebra,
like least squares, QR, LU, Cholesky, etc..,
but no particular attention has been paid to them.

It would be interesting to investigate the performance of these algorithms
and compare them to proper distributed BLAS/LAPACK implementations.
This will very likely lead to opportunities to improve the algorithms
and possibly some of Dask's internal machinery.


### Dask-R and Dask-Julia

Someone with understanding of R's or Julia's networking stack
could adapt Dask's distributed scheduler for those languages.
Recall that the dask.distributed network consists of a central scheduler,
many distributed workers, one or more user-facing clients.
Currently these are all written in Python and only really useful from that language.

Making this system useful in another language would require rewriting the client and worker code,
but would not require rewriting the scheduler code, which is intentionally language agnostic.
Fortunately the client and worker are both relatively simple codebases (relative to the scheduler at least)
and minimal implementations could probably be written in around 1-2k lines each.

This would not provide the high-level collections like dask.array or dask.dataframe,
but would provide all of the distributed networking, load balancing, resilience, etc..
that is necessary to build a distributed computing stack.
It would also allow others to come later and build the high level collections that
would be appropriate for that language
(presumably R and Julia user communities don't want exactly Pandas-style dataframe semantics anyway).

This is discussed further in [dask/distributed #586](https://github.com/dask/distributed/issues/586)
and has actually been partially implemented in Julia in the [Invenia project](https://github.com/invenia/DaskDistributedDispatcher.jl).

This would require some knowledge of network programming and,
ideally, async programming in either R or Julia.


### High-Level NumPy Optimizations

Projects like Numpy and Dask array compute what the user says,
even if a more efficient solution exists.

```python
(x + 1)[:5]  # what user said
```

```python
x[:5] + 1    # faster and equivalent solution
```

It would be useful to have a project that exactly copies the Numpy API,
but constructs a symbolic representation of that computation instead of performs work.
This would enable a few important use cases that we've seen arise recently.
These include both applications from just analyzing the symbolic representation
and also applications from changing it to a more optimal form:

1.  You could analyze this representation and warn users
    about intermediate stages that require a lot of RAM or compute time
2.  You could suggest ideal chunking patterns based on the full computation
3.  You could communicate this computation over the network to a remote server to perform the computation
4.  You could visualize the computation to help users or students understand what they're computing
5.  You could manipulate the representation into more efficient forms (such as what is shown above)

The first part of this would be to construct a class that behaves like a Numpy array
but constructs a symbolic tree representation instead.
This would be similar to Sympy, Theano, Tensorflow, Blaze.expr or similar projects,
but it would have much smaller scope and would not be at all creative in
designing new APIs.  I suspect that you could bootstrap this project quickly
using systems like dask.array, which already do all of the shape and dtype computations for you.
This is also a good opportunity to connect to recent and ongoing work in Numpy
to establish protocols that allow other array libraries (like this one) to
work smoothly with existing Numpy code.

Then you would start to build some of the analyses listed above on top of this representation.
Some of these are harder than others to do robustly,
but presumably they would get easier in time.
