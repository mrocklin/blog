---
layout: post
title:  Introducing PyToolz
tagline:  a functional standard library
category : work
tags : [Python, SciPy]
---
{% include JB/setup %}

The PyToolz project extends `itertools` and `functools` to provide a set of
standard functions for iterators, functions, and dictionaries.

A year or two ago I, like many programming enthusiasts, started playing with
functional programming.  One common feature of functional languages stuck out
as having very little to do with FP in general.  Modern functional languages
tend to have really killer standard libraries, particularly for iterators,
functions, and dictionaries.  This feature doesn't depend on macros, monads, or
any other mind bending language feature exclusive to LISP or Haskell.  This
feature only requires higher order functions and lazy iterators, both of which
Python does quite well.

This is well known.  The libraries `itertools` and `functools` are supposed to fill
this niche.  Personally I've found these libraries to be very useful but often
incomplete (although the Python 3 versions are showing signs of improvement.)
To fill these gaps the libraries `itertoolz` and `functoolz` (note the `z`)
were formed.  They were eventually merged into a single codebase, named
`toolz` which is available for your hacking pleasure at
[http://github.com/pytoolz/toolz/](http://github.com/pytoolz/toolz/).

Official
--------

The official description follows:

The Toolz project provides a set of utility functions for iterators, functions,
and dictionaries.  These functions are designed to interoperate well, forming
the building blocks of common data analytic operations.  They extend the
standard libraries `itertools` and `functools` and borrow heavily from the
standard     libraries of contemporary functional languages.

Toolz provides a suite of functions which have the following virtues:

-   **Composable:** They interoperate due to their use of core data structures.
-   **Pure:**  They don't change their inputs or rely on external state.
-   **Lazy:**  They don't run until absolutely necessary, allowing them to
    support      large streaming data sets.

This gives developers the power to write *powerful* programs to solve *complex
problems* with relatively *simple code* which is *easy to understand* without
sacrificing *performance*.  Toolz enables this approach, commonly associated
with functional programming, within a natural Pythonic style suitable for most
developers.

This follows in the footsteps of the popular projects `Underscore.js` for
JavaScript and and `Enumerable` for Ruby.


Example
-------

Word counting is a common example used to show off data processing libraries.
The Python version that leverages `toolz` demonstrates how the algorithm can be
deconstructed into splitting, stemming, and frequency counting:

{% highlight python %}
>>> from toolz import *

>>> def stem(word):
... """ Stem word to primitive form """
...     return word.lower().rstrip(",.!:;'-\"").lstrip("'\"")

>>> wordcount = compose(frequencies, partial(map, stem), str.split)

>>> wordcount("This cat jumped over this other cat!"))
{'this': 2, 'cat': 2, 'jumped': 1, 'over': 1, 'other': 1}
{% endhighlight %}

Wordcounting is the composition of three basic operations

1.  Splitting a text into words  (`str.split`)
2.  Stemming those words to a base form (e.g. `'Hello!'` is the same as `'hello'`)  (`partial(map, stem)`)
3.  Counting occurrences of each base word (`frequencies`)

`Toolz` provides both common operations for iterators (like `frequencies` for
counting occurrences) and common operations for functions (like `compose` for
function composition).  Using these together, programmers can describe a
number of data analytic solutions clearly and concisely.

Here is another example performing analytics on the following directed graph

<img src="{{ BASE_PATH }}/images/toolz-example-graph.png"
     width="40%"
     align="center">

{% highlight python %}
>>> from toolz.curried import *
>>> a, b, c, d, e, f, g = 'abcdefg'

>>> edges = [(a, b), (b, a), (a, c), (a, d), (d, a), (d, e),
...          (e, f), (d, f), (f, d), (d, g), (e, g)]

>>> nodes = set(concat(edges))
{'a', 'b', 'c', 'd', 'e', 'f', 'g'}

>>> # Out degree
>>> countby(first, edges)
{'a': 3, 'b': 1, 'd': 4, 'e': 2, 'f': 1}

>>> # In degree
>>> countby(second, edges)
{'a': 2, 'b': 1, 'c': 1, 'd': 2, 'e': 1, 'f': 2, 'g': 2}

>>> # Out neighbors
>>> valmap(compose(list, map(second)),
...        groupby(first, edges))
{'a': ['b', 'c', 'd'],
 'b': ['a'],
 'd': ['a', 'e', 'f', 'g'],
 'e': ['f', 'g'],
 'f': ['d']}

>>> # In neighbors
>>> valmap(compose(list, map(first)),
...        groupby(second, edges))
{'a': ['b', 'd'],
 'b': ['a'],
 'c': ['a'],
 'd': ['a', 'f'],
 'e': ['d'],
 'f': ['e', 'd'],
 'g': ['d', 'e']}
{% endhighlight %}

Learning a small set of higher order functions like `groupby`, `map`, and
`valmap` gives a surprising amount of leverage over this kind of data.
Additionally the streaming nature of many (but not all) of the algorithms
allows `toolz` to perform well even on datasets that do not fit comfortably
into memory.

I routinely process large network datasets at my work and find `toolz` to be
invaluable in this context.


For More Information
--------------------

*   Documentation is available at [http://toolz.readthedocs.org/](http://toolz.readthedocs.org/en/latest/)

*   BSD licensed source code is available at [http://github.com/pytoolz/toolz/](http://github.com/pytoolz/toolz/)

*   The API is thoroughly documented at [http://toolz.readthedocs.org/en/latest/api.html](http://toolz.readthedocs.org/en/latest/api.html)

*   `toolz` is `pip/easy_install`able.  It supports Python 2.6-3.3 and depends only on the standard library.
