---
layout: post
title: Python Data Structures are Fast
tagline:
category : work
tags : [scipy, Python, Programming]
---
{% include JB/setup %}

**tl;dr: Our intuition that Python is slow is often incorrect.  Data structure
bound Python computations are fast.**

You may also want to see the companion post, [Introducing
CyToolz](http://matthewrocklin.com/blog/work/2014/05/01/Introducing-CyToolz/).


## We think that Python is slow

Our intuition says that Python is slow:

{% highlight Python %}
>>> # Python speeds
>>> L = range(1000000)
>>> timeit sum(L)
timeit np.s100 loops, best of 3: 7.79 ms per loop

>>> # C speeds
>>> import numpy as np
>>> A = np.arange(1000000)
>>> timeit np.sum(A)
1000 loops, best of 3: 725 µs per loop
{% endhighlight %}

Numerical Python with lots of loops is much slower than the equivalent C or
Java code.  For this we use one of the numeric projects like NumPy, Cython,
Theano, or Numba.


## But that only applies to normally cheap operations

This slowdown occurs for cheap operations for which the Python overhead
is large relative to their cost in C.  However for more complex operations,
like data structure random access, this overhead is less important.  Consider
the relative difference between integer addition and dictionary assignment.

{% highlight Python %}
>>> x, y = 3, 3
>>> timeit x + y
10000000 loops, best of 3: 43.7 ns per loop

>>> d = {1: 1, 2: 2}
>>> timeit d[x] = y
10000000 loops, best of 3: 65.7 ns per loop
{% endhighlight %}

A Python dictionary assignment is about as fast as a Python add.

*Disclaimer: this benchmark gets a point across but is is very artificial,
micro-benchmarks like this are hard to do well.*


## Micro-Benchmark: Frequency Counting

*Warning: cherry-picked*

To really show off the speed of Python data structures lets count frequencies
of strings.  I.e. given a long list of strings

{% highlight Python %}
>>> data = ['Alice', 'Bob', 'Charlie', 'Dan', 'Edith', 'Frank'] * 1000000
{% endhighlight %}

We want to count the occurence of each name.  In principle we would write a
little function like `frequencies`

{% highlight Python %}
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
{% endhighlight %}

This simple operation tests grouping reductions on non-numerical data.
This represents an emerging class of problems that doesn't fit our
performance intuition from our history with numerics.

We compare the naive `frequencies` function against the following equivalent implementations

*   The standard library's `collections.Counter`
*   PyToolz' benchmarked and tuned `frequencies` operation
*   Pandas' `Series.value_counts` method
*   A naive implementation in Java, found [here](https://gist.github.com/mrocklin/3a774401288a5aad12c6)

We present the results from worst to best:


{% highlight Python %}
>>> timeit collections.Counter(data)        1.59  s     # Standard Lib
>>> timeit frequencies(data)                 805 ms     # Naive Python
>>> timeit toolz.frequencies(data)           522 ms     # Tuned Python
>>> series = Series(data)
>>> timeit series.value_counts()             286 ms     # Pandas
{% endhighlight %}
~~~~~~~~~~
$ java Frequencies                           207 ms     # Straight Java
~~~~~~~~~~

Lets observe the following:

*   The standard library `collections.Counter` performs surprisingly poorly.
    This is unfair because the `Counter` object is more complex,
    providing more exotic functionality that we don't use here.
*   The Pandas solution uses C code and C data structures to beat the Python
    solution, but not by a huge amount.  This isn't the 10x-100x speedup that
    we expect from numerical applications.
*   The `toolz.frequencies` function improves on the standard Python solution
    and gets to within a factor of 2x of Pandas.   The PyToolz development team
    has benchmarked and tuned several implementatations.  I believe that this is
    the [fastest solution available](http://toolz.readthedocs.org/en/latest/_modules/toolz/itertoolz.html#frequencies) in Pure Python.
*   The compiled [Java Solution](https://gist.github.com/mrocklin/3a774401288a5aad12c6)
    is generally fast but, as with the Pandas case it's not *that* much faster.

For data structure bound computations, like frequency counting, Python is
generally fast enough for me.  I'm willing to pay a 2x cost in order to gain
access to Pure Python's streaming data structures and low entry cost.


CyToolz
-------

Personally, I'm fine with fast Python speeds.  Erik Welch on the other hand,
wanted unreasonably fast C speeds so he rewrote `toolz` in Cython;  he calls it
[CyToolz](http://github.com/pytoolz/cytoolz/).  His results are pretty amazing.

{% highlight Python %}
>>> # import toolz
>>> import cytoolz

>>> timeit toolz.frequencies(data)           522 ms
>>> timeit series.value_counts()             286 ms
>>> timeit cytoolz.frequencies(data)         214 ms
{% endhighlight %}
~~~~~~~~~~
$ java Frequencies                           207 ms
~~~~~~~~~~

CyToolz actually beats the Pandas solution (in this one particular benchmark.)  Lets appreciate this for a moment.

Cython on raw Python data structures runs at Java speeds.  We discuss CyToolz
further in [our next blog
post](http://matthewrocklin.com/blog/work/2014/05/01/Introducing-CyToolz/)


Conclusion
----------

We learn that data structure bound computations aren't as slow in Python as we
might think.  Although we incur a small slowdown (2x-5x), probably due to
Python method dispatching, this can be avoided through Cython. When using
Cython, the use of Python data structures can match perofrmance we expect from
compiled languages like Java.
