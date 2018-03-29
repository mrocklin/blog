Disclaimers and bias: I (the author) have attempted to write this from the perspective of the general open source community, of which I am an active member.  However, I am also employed by employed by Anaconda and a am core maintainer of a particular library mentioned below, Dask.  The reader should keep this bias in mind when consuming the arguments below.



This document outlines three approaches to accelerate Python at a high level:

1.  Scaling in: using efficient compiled code
2.  Scaling up: using a single large machine effectively in parallel
3.  Scaling out: using multiple machines effectively in parallel

This is written for someone who has only modest exposure to Python and wants
a broad overview.


Motivation
----------

People doing data intensive workloads [seem to prefer Python](https://stackoverflow.blog/2017/09/06/incredible-growth-python/),
and in particular popular libraries like Numpy, Pandas, and Scikit-Learn
that combine modern algorithms, efficient code, and intuitive interfaces.

And yet we also hear things like "Python is slow"
or "Python doesn't parallelize well"
which seem to be at odds with Python's popularity.
How can these things both be true, especially in today's Big Data environment?
What are the options we have today to accelerate and scale Python
and how do we choose between them?

This article describes three classes of accelerating or scaling Python code,
the options within each class,
and the pro's and con's of each,
so that people can make high level decisions that are appropriate for their situation.


Scaling in: Accelerating Python in a single thread
--------------------------------------------------

The Python language was not originally designed for speed.
It is about 2-5x slower when dealing with text and JSON-like data
and 100-1000x slower when dealing with numeric data.
If used naively this can slow down analyses,
leading both to analysts that iterate on new ideas more slowly,
and also to analyses on smaller datasets that may integrate less information.

Fortunately, most popular Python packages are written in C and so are generally very fast.
Packages like Numpy, Pandas, and Scikit-Learn have Python user interfaces,
but all of their internal number crunching code is written in a low-level language that is then compiled for speed.
This means that the 100-1000x slowdown you might see from using Pure Python for loops goes away,
and you're left with as much speed as a CPU core is likely to give to you.

However, this only works if analysts stay within the Numpy, Pandas, and Scikit-Learn APIs.
Unfortunately it is common to see non-expert users write Pure Python code (slow) *around* Numpy arrays or Pandas dataframes

```python
for row in my_pandas_dataframe:
    if row.customer_name == 'Alice':
        row.balance = 100
```

Even though they are including Pandas dataframes in their code
it doesn't mean that they are using Pandas algorithms backed by fast C code.
This isn't surprising.
These libraries take skill to use well and the right way to do something may not be immediately obvious.

In this situation you have two options:

1.  Learn more about how to solve your problem within the Numpy/Pandas/Scikit-Learn system so that you leverage fast compiled code
2.  Write fast compiled code yourself

### Learn More

Learning more about these systems is always a good idea.
Here are a few good ways to accomplish this objective:

1.  You can read the documentation online, which is quite thorough
2.  You can ask peers how to solve problems on Stack Overflow.
    Often you will find that your question has already been asked by someone else,
    and you can read their answer immediately.
3.  You can go to a local PyData conference there are dozens both within the US and around the world.
    These almost always have tutorials on using these libraries efficiently.
4.  If you work at a company you can hire a professional trainer to come and deliver a course

### Write compiled code

So you have some pure Python code (slow) and you want to compile it to run more quickly.
Your use case is special enough that you don't expect to find it as a canned algorithm in one of the libraries mentioned above.
There are several options.  Lets mention a few of the more popular ones:

1.  You can write normal C/C++/Fortran code and link it to Python.

    In this case you should look at cffi, Cython, ctypes (C), pybind (C++), f2py (Fortran)

2.  You can write in a compiled variant of Python, called Cython: http://cython.org/

    This allows you to modify your code only slightly to achieve C speeds if you are careful.
    Many of the major libraries like Pandas and Scikit-Learn use Cython extensively,
    so you'll be in good company.
    There are several online resources for how to do this well.

    I recommend [this tutorial by Kurt Smith](https://www.youtube.com/watch?v=gMvkiQ-gOW8&t=1s)

3.  You can continue to write Python code, but compile it with Numba: http://numba.pydata.org/

    This allows you to keep writing normal Python code, but add a small decorator

    ```python
    @numba.jit
    def sum(x):
        total = 0
        for i in range(len(x)):
            total += x[i]
        return total
    ```

    Numba is generally the easiest to write in (unless you already prefer C/C++)
    the easiest to link to Python (you just include it in your normal file),
    and usually gives the best performance.  However it's also newer and less established.

    I recommend [this tutorial by Gil Forsyth and Lorena Barba](https://www.youtube.com/watch?v=1AwG0T4gaO0)

### Costs and Benefits

You should *always* spend some time scaling in before moving on.
The benefits here are often the greatest and there is rarely any administrative cost.
I strongly recommend profiling and tuning your code before trying to scale out your code to parallel systems.

Writing more efficient code can also help with big data problems.
Storing data efficiently can often reduce your memory load by an order of magnitude.


Scaling Up: Using multi-core machines and workstations
------------------------------------------------------

After tuning code you may find that an analysis still runs slowly,
or that when you try it on a larger dataset you run out of memory.
Before you switch to using a massively parallel cluster
you may first want to try parallelizing on a single machine.
This is often a more productive (and more efficient!) choice.

<img src="https://pbs.twimg.com/media/DZOT53jWAAA-vWu.jpg:large"
     width="60%">



