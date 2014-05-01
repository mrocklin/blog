---
layout: post
title: Introducing CyToolz
tagline: Functional Python, now in C
category : work
draft: true
tags : [SciPy, scipy, Python, Programming]
---
{% include JB/setup %}

**tl;dr: We reimplement PyToolz, a functional standard library, in Cython.
It's fast.**

**This post highlights work done, and was partially written by, [Erik N.
Welch](http://github.com/eriknw/).  When I say "we" below, I really mean "Erik"**

[Last year](http://matthewrocklin.com/blog/work/2013/10/17/Introducing-PyToolz/)
I introduced [PyToolz](http://toolz.readthedocs.org/en/latest/), a library that
provides a suite of utility functions for data processing commonly found in
functional languages.

{% highlight Python %}
>>> from toolz import groupby

>>> names = ['Alice', 'Bob', 'Charlie', 'Dan', 'Edith', 'Frank']
>>> groupby(len, names)
{3: ['Bob', 'Dan'],
 5: ['Alice', 'Edith', 'Frank'],
 7: ['Charlie']}
{% endhighlight %}

Over the last year a number of [excellent
contributors](https://github.com/pytoolz/toolz/blob/master/AUTHORS.md) have
benchmarked and tuned these functions to the point where they often beat the
standard library.  When you couple these tuned functions with the power of pure
Python data structures you get a nice analytics platform.  In my experience
`toolz` is often [fast enough](http://matthewrocklin.com/blog/work/2014/05/01/Fast-Data-Structures/)
for large streaming data projects.


CyToolz
-------

Personally, I'm fine with fast Python speeds.  Erik Welch on the other hand,
wanted unreasonably fast C speeds so he rewrote `toolz` in Cython;  he calls it
[CyToolz](http://github.com/pytoolz/cytoolz/).

{% highlight Python %}
>>> import toolz
>>> import cytoolz

>>> timeit toolz.groupby(len, names)            3.19 µs
>>> timeit cytoolz.groupby(len, names)           721 ns
{% endhighlight %}

For data structure bound computations this approach competes with Java.
Note that CyToolz accomplishes these speeds even on standard Python data
structures.  This differs from the traditional NumPy/Pandas approach of
applying Cython code onto non-Pythonic C data structures.


| Project               | Computation           |   Data Structures        |
|:----------------------|:----------------------|:-------------------------|
| PyToolz               | Python                | Python                   |
| CyToolz               | C                     | Python                   |
| Pandas/NumPy          | C                     | C                        |


Erik just released CyToolz yesterday.  Get it while it's hot

    $ pip install cytoolz


How?
----

Cython is most effective when leveraging C type information for tight inner
loops or C data structures like numpy arrays, and speed improvements of 10-100x
are common for these cases.  We have found that by utilizing Cython and Python's
C API, significant improvements (typically 2-5x and sometimes much more) can be
achieved when using pure Python data structures.

We actually don't know precisely where most of the performance increases come
from.  Developing for performance was primarily done through trial and error
and was driven by curiosity.  Cython employs many optimizations, and the code
compiles to a native C extension, which is generally faster than the Python
interpreter.  Still, we were able to improve upon the original Python code for
nearly all functions.  Here are some of our best guesses for how this was
achieved:

1. Python's C API exposes functionality unavailable in the Python interpreter.
2. Directly using the C API is faster in some cases even when Python has an equivalent
   function.
3. The C API allows pointers to be used.  In many cases this is a "borrowed reference",
   and it avoids reference counting and the garbage collector.
4. Some C API functions don't check types or raise exceptions; these must be used with
   caution, but can be much faster.
5. Checking types with `isinstance` in Cython is really fast.  So is checking whether a
   pointer is `NULL`.
6. The overhead of calling C extension types developed in Cython is low.  This, for
   instance, makes iterables really fast.
7. Early binding--that is, pre-declaring variables with `cdef`--usually improves
   performance.


Example: `merge`
----------------

{% highlight Python %}
>>> dicts = {'one': 1, 'two': 2}, {'three': 3}, {'two': 2, 'four': 4}
>>> toolz.merge(dicts)
{'one': 1, 'two': 2, 'three': 3, 'four': 4}

>>> timeit toolz.merge(dicts)                   1.76 µs
>>> timeit cytoolz.merge(dicts)                  264 ns
{% endhighlight %}


Why?
----

We love NumPy and Pandas, so why do we use toolz?  Two reasons

1.  Streaming analytics - Python's iterators and Toolz support for lazy operations allows me to crunch over Pretty-Big-Data without the hassle of setting up a distributed machine.
2.  Trivial parallelism - The functional constructs in PyToolz, coupled with the promise of [serialization](http://matthewrocklin.com/blog/work/2013/12/05/Parallelism-and-Serialization/), make parallelizing PyToolz applications to multicore or cluster computing trivial.  See the [toolz docs page](http://toolz.readthedocs.org/en/latest/parallelism.html) on the subject.


Testing
-------

CyToolz perfectly satisfies the PyToolz test suite.  This is especially notable
given that PyToolz has 100% coverage.

PyToolz is stable enough that we were able to just copy over the tests en
masse.  We'd like to find a cleaner way to share test suites between codebases
though.  Ideas and experiences welcome.


Example: `pluck`
----------------

Many Toolz operations provide functional ways of doing plain old Python
operations.  The `pluck` operation gets out elements from items in a collection.

{% highlight Python %}
>>> data = [{'name': 'Alice', 'amount': 100}, {'name': 'Bob', 'amount': 200}]
>>> list(pluck('name', data))
['Alice', 'Bob']
{% endhighlight %}

In PyToolz we work hard to ensure that we're not much slower than straight
Python (this definitely requires work.)

{% highlight Python %}
>>> data = [[i, i**2] for i in range(1000)]

>>> timeit [item[0] for item in data]
10000 loops, best of 3: 54.2 µs per loop

>>> timeit list(toolz.pluck(0, data))
10000 loops, best of 3: 62.9 µs per loop
{% endhighlight %}

But CyToolz just beats Python hands down.

{% highlight Python %}
>>> timeit list(cytoolz.pluck(0, data))
10000 loops, best of 3: 26.7 µs per loop
{% endhighlight %}



A note on Functional Programming
--------------------------------

PyToolz integrates functional principles into traditional Python programming.
CyToolz supports these same functional principles, in the same workflow, but
now backed by C speeds

I started PyToolz because I liked Clojure's standard library but couldn't stay
on the JVM (I needed to interact with native code).  Originally I thought of
Python and PyToolz as a hack providing functional programming abstractions in
an imperative language.  I've now come to think of Python as a performant and
serious functional language in its own right.  While it lacks macros, monads,
or any sort of type system, it is just fine for 99% of the pedestrian
programming that I do every day.


Conclusion
----------

The toolz functions are simple, fast, and a great way to compose clear and
performant code.  Check out [the docs](http://toolz.readthedocs.org/) and find
a function that you didn't know you needed, or a function that you needed,
wrote, but didn't benchmark quite as heavily as we did.

If you're already a savvy toolz user and want Cython speed then you'll be
happy to know that the cytoolz library is a drop in replacement for toolz.

    $ pip install cytoolz

{% highlight Python %}
# from toolz import *
from cytoolz import *
{% endhighlight %}

Most functions improve by 2x-5x with some fantastic exceptions.

Links
-----

* [Cython documentation](http://docs.cython.org/)
* [Cython FAQ](https://github.com/cython/cython/wiki/FAQ)
* [Cython tutorial from 2013 SciPy Conference](http://conference.scipy.org/scipy2013/tutorial_detail.php?id=105)
(resources [here](http://public.enthought.com/~ksmith/scipy2013_cython/))


**Related Blogposts**

*   [Introducing PyToolz](http://matthewrocklin.com/blog/work/2013/10/17/Introducing-PyToolz/)
*   [Verbosity](http://matthewrocklin.com/blog/work/2013/11/15/Functional-Wordcount/)
*   [Text Benchmarks](http://matthewrocklin.com/blog/work/2014/01/13/Text-Benchmarks/)
*   [Fast Data Structures](http://matthewrocklin.com/blog/work/2014/05/01/Fast-Data-Structures/)
