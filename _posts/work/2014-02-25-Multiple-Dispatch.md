---
layout: post
title: Multiple Dispatch
tagline: not a terrible idea
category : work
tags : [SciPy, Python, Programming]
---
{% include JB/setup %}

**tl;dr: We present a multiple dispatch system for Python.  We discuss issues
that arise from multiple dispatch.  We try to allay fears related to these
issues.**

## Dispatch

Abstract operations like addition, `+`, have several different implementations.
We choose which implementation to use based on the type of the inputs.  For example:

*   The addition of two numbers results in arithmetic addition
*   The addition of two strings results in concatenation
*   The addition of two user defined objects results in `__add__` or `__radd__` calls

The selection of implementation (e.g. arithmetic add) based on input types (e.g. integers) is called dispatch.

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
        raise NotImplementedError()
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
a set of arguments the dispatch system performs dynamic type checking to find
the right function and then executes that function on those arguments.  This is
exactly what happens in the object oriented solution, but now we dispatch on
all of the arguments rather than only the first.

The example above uses the `multipledispatch` library found
[here](https://github.com/mrocklin/multipledispatch/).  It's also installable
from PyPI with the following command:

    pip install multipledispatch

## Dispatch Supports Interactions Between Projects

Multiple dispatch allows distinct types to interact over a shared abstract
interface.  For example, there currently exist several array programming
solutions in Python, each vying for the title "`numpy` of the future".
Multiple dispatch supports efforts to interact between these disparate
solutions.

For example most array programming solutions implement a dot-product operation,
`dot`.  Using multiple dispatch we could implement interactions like the
following:


{% highlight Python %}
@dispatch(numpy.ndarray, scipy.sparse.csr_matrix)
def dot(x, y):
    ....

@dispatch(numpy.ndarray, theano.tensor)
def dot(x, y):
    ...

@dispatch(numpy.ndarray, blaze.array)
def dot(x, y):
    ...
{% endhighlight %}

These interactions don't need to reside in each project.  Multiple dispatch
separates interaction code from core code.  This opens and democratizes
interaction, for better or for worse.


## Issues

Programmers experienced with multiple dispatch know that it introduces the
following problems:

1.  Dynamic multiple dispatch costs performance
2.  It is possible to generate two type signatures that are equally valid for a
    given set of inputs.
3.  Because we collect functions around their name we ignore namespaces.
    Different projects that reuse the same names may conflict.

Lets handle these in order

### 1. Performance

Each call to a dispatched function requires a dynamic check of the types of the
inputs against the type signatures of the known implementations at runtime.  This takes time.

Using dictionaries, some static analysis, and caching we can push this cost
down to a couple of microseconds.  While this is slower than straight Python
it's not *that* much slower.  Don't forget that objects do this dynamic
checking too.


### 2. Conflicting type signatures raise ambiguities

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
implementations that contain an *ambiguity*.  Due to inheritance both type
signatures `(object, float)` and `(float, object)` satisfy our argument types,
`(float, float)` equally well.  It's ambiguous which implementation of `f` we
is most valid.  In large projects that depend on multiple dispatch, this
behavior can create bugs that are difficult to track down.

Fortunately, we detect this problem statically at function definition time.
Inheritance of each of the type inputs induces a graph on all of the
signatures.  By looking for uncovered cycles within this graph we can identify
ambiguous collections of signatures and report them *before the code is run*.
We can suggest new signatures to cover the ambiguity:

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


### 3. Collecting functions by name ignores namespaces

Different projects implement functions with the same name all the time.  This
can cause some confusion.  Normally Python handles this problem with
namespaces.  Namespaces help to distinguish between `your_library.foo` and
`my_library.foo`.  Namespaces are one heck of a good idea.

Unfortunately multiple dispatch systems often group functions by their name and
ignore namespaces completely.  Can an ecosystem exist when several projects use
multiple dispatch without coordination?  Coordinating `(name, type-signature)`
pairs to avoid conflicts between projects would inhibit the growth of the
ecosystem.  Do multiple dispatch systems like what is described above make this
necessary?

My opinion: *Yes, they do, but this coordination is easy - we do it already.*

Python already has globally dispatched operations.  Consider `+`.  People add
implementations to `+` every day.  The `+` operation isn't in a namespace, it
doesn't need to be imported, it just dispatches based on the data given to it.
And yet no problems arise *as long as no one monkey patches*.  That is, as long
as people only define methods for types that they manage then globally
distributed dispatching systems are safe.

Of course, dispatch systems like what we show above make monkey-patching of
types easier.  For example in writing this post I defined `add` on
`(object, object)` to mean string concatenation, clearly a pretty bold
decision.

{% highlight Python %}
>>> @dispatch(object, object)
... def add(x, y):
...     return "%s + %s" % (x, y)
{% endhighlight %}

This was bad, as bad as is monkey patching.  My opinion is that globally
distributed dispatch is safe if we do not make broad claims like the example
above.


## Background

There have been several attempts at multiple dispatch in Python.  I'll list a few below:


*   [Five-minute Multimethods in Python by Guido](http://www.artima.com/weblogs/viewpost.jsp?thread=101605):
    A quick explanation of multimethods and a simple implementation.  He leaves
    the hard parts as "an exercise for the reader".
*   Most links today point to the [`multimethods` package on PyPI](https://pypi.python.org/pypi/multimethods).
*   The single dispatch decorator is in Python 3.4's `functools`.  See [PEP-443](http://legacy.python.org/dev/peps/pep-0443/) and the [`functools` docs](http://docs.python.org/3.4/library/functools.html)
*   PEP-443 also calls out [The `generic` library](https://github.com/andreypopp/generic) and [the `magic` module of `Gnosis`](https://github.com/smokedice/Gnosis/blob/master/gnosis/magic/multimethods.py) as additional implementations.
*   [PEP 3124 - *Overloading, Generic Functions, Interfaces, and Adaptation*](http://legacy.python.org/dev/peps/pep-3124/) is a good read.  It was an ambitious proposal that didn't stick.  Still contains lots of good thoughts.

*Special thanks to [Erik Welch](https://github.com/eriknw) for pointing me to a number of excellent Python references.*

The quickly growing Julia language handles multiple dispatch wonderfully.  Julia's solution was what inspired me to play with this idea.

*  See the [Julia methods docs](http://julia.readthedocs.org/en/latest/manual/methods/).
*   [Karpinksi's notebook: *The Design Impact of Multiple Dispatch*](http://nbviewer.ipython.org/gist/StefanKarpinski/b8fe9dbb36c1427b9f22) provides motivation.

And finally here is a link to the source code for my
implementation of `multipledispatch`

*   [https://github.com/mrocklin/multipledispatch/](https://github.com/mrocklin/multipledispatch/).
