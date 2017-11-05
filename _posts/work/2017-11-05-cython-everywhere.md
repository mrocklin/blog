---
layout: post
title: Should PyData switch to Cython entirely?
draft: true
category: work
tags: [Programming, Python, scipy, dask]
theme: twitter
---

{% include JB/setup %}

*This work is supported by [Anaconda Inc](http://anaconda.com) and the Data
Driven Discovery Initiative from the [Moore Foundation](https://www.moore.org/)*

*This post is mainly written for other developers*

### tl;dr

Cython's support of PEP-484 type annotations allows us to write code that both
runs naively from Python and can be compiled for significant speedups from
Cython.  This, combined with the ability to be used within Python 2, might
make it attractive enough for PyData projects to consider adopting it more
wholistically throughout the ecosystem.


### Background

The current numeric Python stack (NumPy, Pandas, Matplotlib, Jupyter, ...) is
mostly written in a subset of Python that is simultaneously valid for Python 2
and Python 3, with occasional use of C and Cython for speed.  This choice has
some pros and cons

- **Pros**
    - Supports both major branches of the language from a single codebase
    - Easy to develop on from either language
    - Occasional use of C/Cython gives us speed when necessary but doesn't get
      in the way otherwise
    - We don't need to compile when developing
-  **Cons**
    - We can't use Python 3 features like static typing or async-await
    - Use of the Cython language is not well understood by the majority of our
      developers

I'm starting to consider that we should instead write in the subset that is
simultaneously valid Python 3 and Cython, and then use Cython to support Python
2 .  This blog post explores this idea.


### Cython in PyData Today

Most use of Cython today involves the Cython language, a superset of Python with
optional type annotations and a few other niceties (like nogil blocks, prange,
typed memoryviews, ...).  Typically we take our existing Python code, annotate
it with more information, and then compile it with Cython into C.

The side-by-side example below provides a sense of the work involved to get
a 10x speedup on numeric code with Cython:

```python
# Python code                          # Cython code

                                        cdef int i        # Add type declarations
                                        cdef float total

total = 0.0                             total = 0.0
for i in range(10000000):               for i in range(10000000):
    total += i                              total += i

# runs in 0.5 seconds                   # runs in 0.06 seconds
```

We see that minor modifications can produce significant speedups in numeric
cases.  However this new code isn't Python code any more, so calling `python
my_cython_file.pyx` will raise a syntax error in either Python 2 or 3.  As a
result we typically isolate our use of Cython to only those few numerical
routines where it makes the most impact.  Maintenance of this code is typically
restricted to only a few core developers of any project while the majority of
developers remain in Pure Python.


### But Cython now supports Python 3 type annotations

Recently Cython started supporting Python 3 type annotations in addition to its
own annotations.  This means that we can Cythonize pure Python code and still
get nice speedups:

```python
# Python code                           # Cython code
import cython

x: cython.int                           cdef int i
total: float                            cdef float total

total = 0.0                             total = 0.0
for i in range(10000000):               for i in range(10000000):
    total += i                              total += i

# runs in 0.5 seconds with python       # runs in 0.06 seconds
# runs in 0.06 seconds when compiled with Cython
```

Our Python code on the left still behaves as normal Python code when run with
the normal Python interpreter, but can now optionally reach the same speed as
our Cython code on the right when compiled with Cython.  We can develop in
Python as normal and then, when we want to package our code for distribution or
want to run benchmarks we can Cythonize our code and get the extra speed boost
that compilation offers.


### Costs and benefits

So we get to stay in Python and optionally add Cython without pulling our code
out into a new language or file.

There are some costs here though.

-  We had to use Cython types to get performance in some cases
-  We lost Python 2 support
-  We had to invoke Cython and use a C compiler to get speedups

In the example above we had to `import cython`, creating a runtime dependence on
the Cython library.  In our specific case this is because Cython won't convert
Python integers into C integers for safety reasons (Python integers handle
things like overflow and large numbers while C integers don't).  More generally
we can imagine wanting more features from Cython that are not easily or safely
expressible with Python type hints.  This will create a constant pressure to
include runtime dependence on Cython.  This isn't terrible; Cython has no
dependencies outside of the standard library and imports in around 5ms.

We've also lost Python 2 interpretability (type annotations raise
SyntaxErrors in Python 2).  However code compiled with Cython can also target
Python 2, even if it used Python 3 syntax.  This means that Python 2 users can
still use our libraries, but only after they've gone through a compilation
cycle.  Git-master becomes inaccessible to Python 2 users if they're not able to
compile.

-  **Pros**
    -  We get to use Python 3 features
    -  We get speedups in some cases from Cython compilation
    -  We find a possible resolution to the Python 2 legacy maintenance problem
    -  We might be able to drop some existing Cython pyx files, and unify
       development in the core language, broadening the developer base that can
       touch core routines
    -  We gain extra motivation to add type annotations to our codebases,
       enabling other tools like MyPy
-  **Cons**
    -  This increases our packaging burden to include a Cython compilation step
    -  This limits our ability to inspect / debug / profile within our compiled
       Python code
    -  Python 2 users need to compile on their own to use dev versions
