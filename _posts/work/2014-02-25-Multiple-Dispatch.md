---
layout: post
title: Multiple Dispatch
tagline: not a terrible idea
category : work
draft: true
tags : [SciPy, Python, Programming]
---
{% include JB/setup %}

**tl;dr: We present a multiple dispatch system for Python.  We discuss issues
that arise from multiple dispatch.  We try to allay fears associated to these
issues.**

## Dispatch

Abstract operations like addition, `+`, have several different implementations.
We choose which implementation to use based on the type of the inputs.  For example:

*   Adding two numbers results in arithmetic addition
*   Adding two strings means concatenation
*   Adding user defined objects results in `__add__` or `__radd__` calls

This selection of function implementation (e.g. arithmetic add) based on input types (e.g. integers) is called dispatch.

As an object oriented language, Python dispatches on the type of the first
argument, `self`.  We call this single dispatch because it makes a selection
from a single input.


## Dispatching on multiple input types

The standard way to do multiple dispatch in Python is to branch on the type
of other inputs within `__add__`

{% highlight Python %}
def __add__(self, other):
    if isinstance(other, Foo):
        ...
    elif isinstance(other, Bar):
        ...
    else:
        ...
{% endhighlight %}

Or to raise a `NotImplementedError`, which then tells Python to try
`other.__radd__(self)`

Both of these solutions are complex.  It gets worse when you consider
operations with more than two inputs.


## Dispatching on all types with decorators

The non-standard approach to multiple dispatch in Python is to decorate
functions with type signatures:

{% highlight Python %}
>>> from multipledispatch import dispatch

>>> @dispatch(int, int)
... def add(x, y):
...     return x + y

>>> @dispatch(object, object)
... def add(x, y):
...     return "%s + %s" % (x, y)

>>> add(1, 2)
3

>>> add(1, 'hello')
'1 + hello'
{% endhighlight %}

As we define new implementations of `add` decorated with new types we add to a
collection of `{type-signature: function}` associations.  When we call `add` on
some arguments the dispatch system performs dynamic type checking and then
executes the right function definiion on those arguments.  This is exactly what
happens in the object oriented solution, but now we dispatch on all of the
arguments rather than only the first.

The example above uses the `multipledispatch` library found
[here](https://github.com/mrocklin/multipledispatch/).  It's also available on
PyPI with

    pip install multipledispatch

## Issues

Programmers experienced with multiple dispatch know that it introduces the
following problems:

1.  Dynamic multiple dispatch costs performance
2.  It is possible to generate two type signatures that are equally valid to a
    given set of inputs.
3.  Because we collect functions around their name we ignore namespaces.
    Different projects that reuse the same names may conflict.

Lets handle these in order

### Performance

Each call to a dispatched function requires a dynamic check of the types of the
inputs against the type signatures of the known implementations at runtime.

Using dictionaries, some static analysis, and caching we can push this cost
down to a couple of microseconds.  While this is slower than straight Python
it's not *that* much slower.  Don't forget that objects do this dynamic
checking too.


### Conflicting type signatures cause ambiguities

Consider the following two functions

{% highlight Python %}
>>> @dispatch(object, float)
... def f(x, y):
...     return 1

>>> @dispatch(float, object)
... def f(x, y):
...     return 2

>>> f(1.0, 2.0)
?
{% endhighlight %}

What output do we expect, `1` or `2`?  In this case we have defined a set of
implementations that contain an *ambiguity*.  Arguments of the type (`float`,
`float`) don't know exactly which version of `f` they should use.  In large
projects that depend on multiple dispatch, this behavior can create bugs that
are difficult to track down.

Fortunately, we detect this problem statically at function definition time.
Inheritance of each of the type inputs induces a graph on all of the
signatures.  By looking for uncovered cycles within this graph we can identify
ambiguous collections of signatures and report them *before the code is ever
run*.  We can even suggest new signatures that the user should implement:

    >>> @dispatch(float, object)
    ... def f(x, y):
    ...     return 2

    multipledispatch/core.py:52: AmbiguityWarning:

    Ambiguities exist in dispatched function f

    The following signatures may result in ambiguous behavior:
        [float, object], [object, float]


    Consider making the following additions:

        @dispatch(float, float)
        def f(...)


### Collecting functions by name ignores namespaces

Different projects implement functions with the same name all the time.  This
can cause some confusion.  Normally Python handles this problem with
namespaces.  Namespaces help to distinguish between `your_library.foo` and
`my_library.foo`.  They're generally thought of as a heck of a good idea.

Unfortunately multiple dispatch systems often group functions by their name and
generally ignore namespaces completely.  Can an ecosystem exist when several
projects use multiple dispatch?  Coordinating `(name, type-signature)` pairs to
avoid conflicts between projects would inhibit the growth of the ecosystem.  Do
multiple dispatch systems like what is described above make this necessary?

My opinion: *Yes, they do, but this coordination is easy - we do it already.*

Python already has globally dispatched operations.  Consider `+`.  Everyone adds
implementations to `+`.  The `+` operation isn't in a namespace, it doesn't need
to be imported, it just dispatches based on the data given to it.  And yet no
problems arise *as long as no one monkey patches*.  That is, as long as people
only define methods for types that they manage then globally distributed
dispatching systems are safe.

Of course, dispatch systems like what we show above make monkey-patching of
types easier.  For example in writing this I defined `add` on
`(object, object)` to mean string concatenation, clearly a pretty bold
decision.

{% highlight Python %}
>>> @dispatch(object, object)
... def add(x, y):
...     return "%s + %s" % (x, y)
{% endhighlight %}

This was bad, as bad as is monkey patching.  Don't do it.  My opinion is that
globally distributed dispatch is safe if we do not make broad claims like the
example above.  This is in line with our current ability and aversion to monkey
patching.


## Background

There have been several attempts at multiple dispatch in Python and in other
languages.  I'll list a few below:


*   [Five-minute Multimethods in Python by Guido](http://www.artima.com/weblogs/viewpost.jsp?thread=101605):
    A quick explanation of multimethods and a simple implementation.  He leaves
    the hard parts as "an excercise for the reader".
*   The [`multimethods` package on PyPI](https://pypi.python.org/pypi/multimethods) is a fine implementation that, among other things, supports methods within classes.  Sadly it doesn't support a number of the more complex cases.
*  The [Julia methods docs](http://julia.readthedocs.org/en/latest/manual/methods/) are a great place to read about Julia's approach to multiple dispatch.  Julia handles this problem remarkably well and was a strong inspiration for my attempt here.
*   [Karpinksi's notebook: *The Design Impact of Multiple Dispatch*](http://nbviewer.ipython.org/gist/StefanKarpinski/b8fe9dbb36c1427b9f22) is a good read on the motivations behind multiple dispatch in a language built for it.
*   The [Wikipedia article](http://en.wikipedia.org/wiki/Multiple_dispatch)
