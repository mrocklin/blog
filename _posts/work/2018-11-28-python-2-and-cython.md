---
layout: post
title: Support Python 2 with Cython
category: work
tags: [Programming, Python, scipy]
theme: twitter
---
{% include JB/setup %}


Summary
-------

Many popular Python packages are dropping support for Python 2 next month.
This will be painful for several large institutions.
Cython can provide a temporary fix by letting us compile a Python 3 codebase into something usable by Python 2 in
many cases.

It's not clear if we should do this, but it's an interesting and little known feature of Cython.


Background: Dropping Python 2 Might be Harder than we Expect
------------------------------------------------------------

Many major numeric Python packages are dropping support for Python 2 at the end
of this year.  This includes packages like Numpy, Pandas, and Scikit-Learn.
Jupyter already dropped Python 2 earlier this year.

For most *developers* in the ecosystem this isn't a problem.
Most of our packages are Python-3 compatible and we've learned how to switch libraries.
However, for larger companies or government organizations it's often far harder to switch.
The [PyCon 2017 keynote by Lisa Guo and Hui Ding from Instagram](https://www.youtube.com/watch?v=66XoCk79kjM)
gives a good look into why this can be challenging for large production codebases
and also gives a good example of someone successfully navigating this transition.

It will be interesting to see what happens when Numpy, Pandas, and Scikit-Learn start publishing Python-3 only releases.
We may uncover a lot of pain within larger institutions.
In that case, what should we do?

*(Although, to be fair, the data science stack tends to get used more often in
isolated user environments, which tend to be more amenable to making the Python
2-3 switch than web-services production codebases).*


Cython
------

The Cython compiler provides a possible solution that I don't hear discussed
very often, so I thought I'd cover it briefly.

The Cython compiler can convert a Python 3 codebase into a C-Extension
module that is usable by both Python 2 and 3.  We could probably use Cython
to prepare Python 2 packages for a large subset of the numeric Python
ecosystem after that ecosystem drops Python 2.

Lets see an example...


Example
-------

Here we show a small Python project that uses Python 3 language features.
[(source code here)](https://github.com/mrocklin/py32test)

```
py32test$ tree .
.
├── py32test
│   ├── core.py
│   └── __init__.py
└── setup.py

1 directory, 3 files
```


```python
# py32test/core.py
def inc(x: int) -> int:         # Uses typing annotations
    return x + 1


def greet(name: str) -> str:
    return f'Hello, {name}!'    # Uses format strings
```

```python
# py32test/__init__.py
from .core import inc, greet
```

We see that this code uses both typing annotations and format strings, two
language features that are well-loved by Python-3 enthusiasts, and entirely
inaccessible if you want to continue supporting Python-2 users.

We also show the `setup.py` script, which includes a bit of Cython code if
we're running under Python 2.

```python
# setup.py

import os
from setuptools import setup, find_packages
import sys


if sys.version_info[0] == 2:
    from Cython.Build import cythonize
    kwargs = {'ext_modules': cythonize(os.path.join("py32test", "*.py"),
                                       language_level='3')}
else:
    kwargs = {}

setup(
    name='py32test',
    version='1.0.0',
    packages=find_packages(),
    **kwargs
)
```

This package works fine in Python 2
-----------------------------------

```python
>>> import sys
>>> sys.version_info
sys.version_info(major=2, minor=7, micro=14, releaselevel='final', serial=0)

>>> import py32test
>>> py32test.inc(100)
101

>>> py32test.greet(u'user')
u'Hello, user!'
```

In general things seem to work fine.  There are a couple of gotchas though


Potential problems
------------------

1.  We can't use any libraries that are Python 3 only, like asyncio.

2.  Semantics may differ slightly, for example I was surprised (though pleased)
    to see the following behavior.

    ```python
    >>> py32test.greet('user')  # <<--- note that I'm sending a str, not unicode object
    TypeError: Argument 'name' has incorrect type (expected unicode, got str)
    ```

    I suspect that this is tunable with a keyword parameter somewhere in
    Cython.  More generally this is a warning that we would need to be careful
    because semantics may differ slightly between Cython and CPython.

3.  Introspection becomes difficult.  Tools like `pdb`, getting frames and
    stack traces, and so forth will probably not be as easy when going through
    Cython.

4.  Python 2 users would have to go through a compilation step to get
    development versions.  More Python 2 users will probably just wait for
    proper releases or will install compilers locally.

5.  Moved imports like the `from collections.abc import Mapping` are not
    supported, though presumably changes like this could be baked into Cython
    in the future.

So this would probably take a bit of work to make clean, but fortunately
most of this work wouldn't affect the project's development day-to-day.


Should we do this?
------------------

Just because we can support Python 2 in this way doesn't mean that we should.
Long term, institutions do need to drop Python 2 and either move on to Python 3
or to some other language.  Tricks like using Cython only extend the inevitable
and, due to the complexities above, may end up adding as much headache for
developers as Python 2.

However, as someone who maintains a sizable Python-2 compatible project that is
used by large institutions, and whose livelihood depends a bit on continued
uptake, I'll admit that I'm hesitant to jump onto the
[Python 3 Statement](https://python3statement.org/).
For me personally, seeing Cython as an option to provide continued to support
makes me much more comfortable with dropping Python 2.

I also think that maintaining a conda channel of Cython-compiled
Python-2-compatible packages would be an excellent effort for a for-profit
company like Anaconda Inc, Enthought, or Quansight (or someone new).
Companies may be willing to pay for access to such a channel, and presumably
the company providing these packages would then be incentivized to improve
support for the Cython compiler.
