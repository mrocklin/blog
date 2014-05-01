---
layout: post
title: Python Data Structures are Fast
tagline:
category : work
draft: true
tags : [SciPy, scipy, Python, Programming]
---
{% include JB/setup %}

**tl;dr: Our intuition that Python is slow is often incorrect.  Data structure
bound Python computations are fast.**


## We think that Python is slow

Our intuition says that Python is slow:

~~~ python
>>> # Python speeds
>>> L = range(1000000)
>>> timeit sum(L)
timeit np.s100 loops, best of 3: 7.79 ms per loop

>>> # C speeds
>>> import numpy as np
>>> A = np.arange(1000000)
>>> timeit np.sum(A)
1000 loops, best of 3: 725 µs per loop
~~~

Generally speaking anything involving loops and lots of arithmetic operations
is much slower than the equivalent C or Java code.  For this we use one of
the numeric projects like NumPy, Cython, Theano, or Numba.


## But that only applies to normally cheap operations

This slowdown is especially true of small arithmetic operations which incur a
high overhead relative to their cost in C.  However, for more complex
operations, like data structure random access, this overhead is less important.
Consider the relative difference between integer addition and dictionary
assignment.

~~~~~~~~~~Python
>>> x, y = 3, 3
>>> timeit x + y
10000000 loops, best of 3: 43.7 ns per loop

>>> d = {1: 1, 2: 2}
>>> timeit d[x] = y
10000000 loops, best of 3: 65.7 ns per loop
~~~~~~~~~~

A Python dictionary assignment is about as fast as a Python add.

*Disclaimer: this benchmark gets a point across but is is very artificial,
micro-benchmarks like this are hard to do well.*


## Micro-Benchmark: Frequency Counting

*Warning: cherry-picked example*

To really show off the speed of Python data structures lets count frequencies
of strings.  I.e. given a long list of repeated strings like the following:

~~~~~~~~~~Python
>>> data = ['Alice', 'Bob', 'Charlie', 'Dan', 'Edith', 'Frank'] * 1000000
~~~~~~~~~~

We want to count the occurence of each name.  In principle we would write a
little function like `frequencies`

~~~~~~~~~~~~Python
def frequencies(seq):
    """ Count the number of occurences of each element in seq """
    d = dict()
    for item in seq:
        if item not in d:
            d[item] = 1
        else:
            d[item] = d[item] + 1
    return d

>>> frequencies(data)
{'Alice': 1000000,
 'Bob': 1000000,
 'Charlie': 1000000,
 'Dan': 1000000,
 'Edith': 1000000,
 'Frank': 1000000}
~~~~~~~~~~~~~

This simple operation tests grouping reductions on non-numerical data.
This represents an emerging class of problems that doesn't fit into our
numerical intuition on performance.

We compare the following equivalent implementations

*   Our naive Python implementation of `frequencies`
*   The standard library's `collections.Counter`
*   PyToolz' benchmarked and tuned `frequencies` operation
*   Pandas' `Series.value_counts` method
*   A naive implementation in Java, found [here](https://gist.github.com/mrocklin/3a774401288a5aad12c6)

We present the results from worst to best:


~~~~~~~~~~Python
>>> timeit collections.Counter(data)        1.59  s     # Standard Lib
>>> timeit frequencies(data)                 805 ms     # Naive Python
>>> timeit toolz.frequencies(data)           522 ms     # Tuned Python
>>> series = Series(data)
>>> timeit series.value_counts()             286 ms     # Pandas
~~~~~~~~~~
~~~~~~~~~~
$ java Frequencies                           207 ms     # Straight Java
~~~~~~~~~~

Lets observe the following:

*   The standard library solution `Counter` surprisingly performs the
    worst.  This is a bit unfair as the `Counter` object is a bit more complex,
    providing slightly more exotic functionality that we don't use here.
*   The Pandas solution, which uses C code and C data structures is definitely
    better than the Python solution, but not by a huge amount.  It's not the
    10x-100x speedup that we expect in numerical applications.
*   The `toolz.frequencies` function improves on the standard Python solution
    and gets to within a factor of 2x of Pandas.   The PyToolz development team
    has benchmarked and tuned several implementatations.  I believe that this is
    the [fastest solution available](http://toolz.readthedocs.org/en/latest/_modules/toolz/itertoolz.html#frequencies) in Pure Python.

The compiled [Java
Solution](https://gist.github.com/mrocklin/3a774401288a5aad12c6) is generally
fast but, as with the Pandas case it's not *that* much faster.

For data structure bound computations, like frequency counting, Python is
generally fast enough for me.  I'm willing to pay a 2x cost in order to gain
access to Pure Python's streaming data structures and low entry cost.


CyToolz
-------

Personally, I'm fine with fast Python speeds.  Erik Welch on the other hand,
wanted unreasonably fast C speeds so he rewrote `toolz` in Cython;  he calls it
[CyToolz](http://github.com/pytoolz/cytoolz/).  His results are pretty amazing.

~~~~~~~~~~Python
>>> # import toolz
>>> import cytoolz

>>> timeit toolz.frequencies(data)           522 ms
>>> timeit series.value_counts()             286 ms
>>> timeit cytoolz.frequencies(data)         214 ms
~~~~~~~~~~
~~~~~~~~~~
$ java Frequencies                           207 ms
~~~~~~~~~~

CyToolz actually beats the Pandas solution.  Lets appreciate this for a moment.

Cython on raw Python data structures runs at Java speeds.


Conclusion
----------

We learn that Python data structures are just as fast as Java data structures.
Although we incur a small slowdown (2x-5x), probably due to Python method
dispatching, this can be avoided through Cython.

The `toolz` functions are simple, fast, and a great way to compose clear and
performant code.  Check out [the docs](http://toolz.readthedocs.org/) and find
a function that you didn't know you needed, or a function that you needed,
wrote, but didn't benchmark quite as heavily as we did.

If you're already a savvy `toolz` user and want Cython speed then you'll be
happy to know that the cytoolz library is a drop in replacement.

    $ pip install cytoolz

~~~~~~~~~~Python
# from toolz import *
from cytoolz import *
~~~~~~~~~~

Most functions improve by 2x-5x with some fantastic exceptions.
