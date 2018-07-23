---
layout: post
title: Incremental SAGA
category: work
draft: true
tags: [Programming, Python, scipy, dask]
theme: twitter
---
{% include JB/setup %}

*This work is supported by [ETH Zurich](https://www.ethz.ch/en.html), [Anaconda
Inc](http://anaconda.com), and the [Berkeley Institute for Data
Science](https://bids.berkeley.edu/)*

At a recent Scikit-learn/Scikit-image/Dask sprint at BIDS, Fabian Pedregosa (a
machine learning researcher and Scikit-learn developer) and Matthew
Rocklin (Dask core developer) sat down together to develop an implementation of the
[SAGA optimizer](https://arxiv.org/pdf/1407.0202.pdf) on parallel Dask datasets.

It as an interesting both to see how the algorithm performed and also to see
the ease and challenges to parallelizing a research algorithm with Dask.

### Start


We started with an intitial implementation that Fabian had written for Numpy
arrays using Numba. The following code solves an optimization problem of the form

$$
min_x \sum_{i=1}^n f(a_i^t x, b_i)
$$

```python
import numpy as np
from numba import njit
from sklearn.linear_model.sag import get_auto_step_size
from sklearn.utils.extmath import row_norms

@njit
def deriv_logistic(p, y):
    # derivative of logistic loss
    # same as in lightning (with minus sign)
    p *= y
    if p > 0:
        phi = 1. / (1 + np.exp(-p))
    else:
        exp_t = np.exp(p)
        phi = exp_t / (1. + exp_t)
    return (phi - 1) * y

@njit
def SAGA(A, b, f_deriv, step_size, max_iter=100):

    n_samples, n_features = A.shape
    memory_gradient = np.zeros(n_samples)
    gradient_average = np.zeros(n_features)
    x = np.zeros(n_features)  # vector of coefficients
    step_size = 0.3 * get_auto_step_size(row_norms(A, squared=True).max(), 0, 'log', False)

    for _ in range(max_iter):
        # sample randomly
        idx = np.arange(memory_gradient.size)
        np.random.shuffle(idx)

        # .. inner iteration ..
        for i in idx:
            grad_i = f_deriv(np.dot(x, A[i]), b[i])

            # .. update coefficients ..
            delta = (grad_i - memory_gradient[i]) * A[i]
            x -= step_size * (delta + gradient_average)

            # .. update memory terms ..
            gradient_average += (grad_i - memory_gradient[i]) * A[i] / n_samples
            memory_gradient[i] = grad_i

        # monitor convergence
        print('gradient norm:', np.linalg.norm(gradient_average))

    return x
```



This implementation is a simplified version of the [SAGA
implementation](https://github.com/openopt/copt/blob/master/copt/randomized.py)
that Fabian uses regularly as part of his research.  We wanted to apply it
across a parallel Dask array by applying it to each chunk of the Dask array, a
smaller Numpy array, one at a time, carrying along a set of parameters along
the way.


### Process

In order to better understand the challenges of writing Dask algorithms, Fabian
did most of the actual coding to start.  Fabian is good example of a researcher who
knows how to program well and how to design ML algorithms, but has no direct
exposure to the Dask library.  This was an educational opportunity both for
Fabian and for Matt.  Fabian learned how to use Dask, and Matt learned how to
introduce Dask to researchers like Fabian.

### Step 1: Build a sequential algorithm with pure functions

To start we actually didn't use Dask at all, instead, Matt asked Fabian to
modify his algorithm in a few ways:

1.  It should operate over a list of Numpy arrays (this is like a Dask array,
    but simpler)
2.  It should separate blocks of logic into separate functions, these will
    eventually become tasks, so they should be sizable chunks of work. In this
    case, this led to the creating of the function `_chunk_saga` that
    performs an iteration of the SAGA algorithm on a subset of the data.
3.  These functions should not modify their inputs, nor should they depend on
    global state.  All information that those functions require (like
    the parameters that we're learning in our algorithm) should be
    explicitly provided as inputs.

These requested modifiations affect performance a bit, we end up making more
copies of the parameters and of some intermediate state.  In terms of
programming difficulty this took a bit of time (around a couple hours) but is a
straightforward task that Fabian didn't seem to find challenging or foreign.

```python
from numba import njit
from sklearn.utils.extmath import row_norms
from sklearn.linear_model.sag import get_auto_step_size


@njit
def deriv_logistic(p, y):
    # derivative of logistic loss
    # same as in lightning (with minus sign)
    p *= y
    if p > 0:
        phi = 1. / (1 + np.exp(-p))
    else:
        exp_t = np.exp(p)
        phi = exp_t / (1. + exp_t)
    return (phi - 1) * y



@njit
def _chunk_saga(
    A, b, n_samples, f_deriv, x, memory_gradient, gradient_average, step_size):
    x = x.copy()
    gradient_average = gradient_average.copy()
    memory_gradient = memory_gradient.copy()

    # sample randomly
    idx = np.arange(memory_gradient.size)
    np.random.shuffle(idx)

    # .. inner iteration ..
    for i in idx:
        grad_i = f_deriv(np.dot(x, A[i]), b[i])

        # .. update coefficients ..
        delta = (grad_i - memory_gradient[i]) * A[i]
        x -= step_size * (delta + gradient_average)

        # .. update memory terms ..
        gradient_average += (grad_i - memory_gradient[i]) * A[i] / n_samples
        memory_gradient[i] = grad_i

    return x, memory_gradient, gradient_average


def full_saga(data, max_iter=100, callback=None):
    n_samples = 0
    for A, b in data:
        n_samples += A.shape[0]
    n_features = data[0][0].shape[1]
    memory_gradients = [np.zeros(A.shape[0]) for (A, b) in data]
    gradient_average = np.zeros(n_features)
    x = np.zeros(n_features)

    steps = [get_auto_step_size(row_norms(A, squared=True).max(), 0, 'log', False) for (A, b) in data]
    step_size = 0.3 * np.min(steps)

    for _ in range(max_iter):
        for i, (A, b) in enumerate(data):
            x, memory_gradients[i], gradient_average = _chunk_saga(
                    A, b, n_samples, deriv_logistic, x, memory_gradients[i],
                    gradient_average, step_size)
        if callback is not None:
            print(callback(x, data))

    return x
```


### Step 2: Apply dask.delayed

After things looked good, meaning that no functions either modified their
inputs nor relied on global state we went over a [dask.delayed
example](https://mybinder.org/v2/gh/dask/dask-examples/master?filepath=delayed.ipynb
) together, and then applied the `@dask.delayed` decorator to the functions
that Fabian had written.  Fabian did this at first in about five minutes and to
mutual surprise, things actually worked

```diff


-
+@dask.delayed(nout=3)
 @njit
 def _chunk_saga(
     A, b, n_samples, f_deriv, x, memory_gradient, gradient_average, step_size):
@@ -47,6 +47,7 @@ def full_saga(data, max_iter=100, callback=None):
     n_samples = 0
     for A, b in data:
         n_samples += A.shape[0]
+    data = dask.persist(*data)
     n_features = data[0][0].shape[1]
     memory_gradients = [np.zeros(A.shape[0]) for (A, b) in data]
     gradient_average = np.zeros(n_features)
@@ -61,6 +62,13 @@ def full_saga(data, max_iter=100, callback=None):
                     A, b, n_samples, deriv_logistic, x, memory_gradients[i],
                     gradient_average, step_size)
         if callback is not None:
-            print(callback(x, data))
+            cb = dask.delayed(callback)(x, data)
+        else:
+            cb = None
+        x, cb = dask.persist(x, cb)
+        if callback:
+            print(cb.compute())
```

TODO: Example diff when applying dask.delayed and image of dashboard after
running

XXX see SAGA-dask1.ipynb, for the diff, execute nbdime SAGA-dask0 SAGA-dask1


### Step 3: Diagnose and add more dask.delayed calls

However, while things worked, they were also fairly slow.  If you notice the
dashboard plot above you'll see that there is plenty of white inbetween colored
rectangles.  This shows that there are long periods where none of the workers
is doing any work.

This is a common sign that we're mixing work between the workers (which shows
up on the dashbaord) and the client.  The solution to this is usually more
targetted use of dask.delayed.  Dask delayed is very useful to help parallelize
custom code and while it is trivial to start using, does require some
experience to use well.  It's important to keep track of which operations and
variables are delayed and which aren't.  There is some cost to mixing between
them.

At this point Matt stepped in and added delayed in a few more places and things
started looking cleaner.

```diff
-data = [((np.random.randn)(5000, n_features), ((np.random.randint)(0, 2, 5000) - 0.5) * 2) for _ in range(10)]
+data = [(dask.delayed(np.random.randn)(n_rows, n_features), (dask.delayed(np.random.randint)(0, 2, n_rows) - 0.5) * 2) for _ in range(10)]

## modified /cells/3/source:
@@ -47,14 +47,14 @@ def full_saga(data, max_iter=100, callback=None):
     n_samples = 0
     for A, b in data:
         n_samples += A.shape[0]
-    data = dask.persist(*data)
     n_features = data[0][0].shape[1]
-    memory_gradients = [np.zeros(A.shape[0]) for (A, b) in data]
-    gradient_average = np.zeros(n_features)
-    x = np.zeros(n_features)
+    data = dask.persist(*data)
+    memory_gradients = [dask.delayed(np.zeros)(A.shape[0]) for (A, b) in data]
+    gradient_average = dask.delayed(np.zeros)(n_features)
+    x = dask.delayed(np.zeros)(n_features)

-    steps = [get_auto_step_size(row_norms(A, squared=True).max(), 0, 'log', False) for (A, b) in data]
-    step_size = 0.3 * np.min(steps)
+    steps = [dask.delayed(get_auto_step_size)(dask.delayed(row_norms)(A, squared=True).max(), 0, 'log', False) for (A, b) in data]
+    step_size = 0.3 * dask.delayed(np.min)(steps)

     for _ in range(max_iter):
         for i, (A, b) in enumerate(data):
@@ -65,10 +65,8 @@ def full_saga(data, max_iter=100, callback=None):
             cb = dask.delayed(callback)(x, data)
         else:
             cb = None
-        x, cb = dask.persist(x, cb)
+        x, memory_gradients, gradient_average, step_size, cb = dask.persist(x, memory_gradients, gradient_average, step_size, cb)
         if callback:
             print(cb.compute())
```

TODO: show code diff with extra delayed calls and new image of dashboard

XXX see SAGA-dask2


### Step 4: Profile

The dashboard image above gives confidence that our algorithm is operating as
it should.  The block-sequential nature of the algorithm comes out cleanly, and
there gaps between tasks are very short.

However, when we look at the profile plot of the computation across all of our
cores (Dask constantly runs a profiler on all threads on all workers to get
this information) we see that most of our time is spent compiling Numba code.

TODO: image of profile

We started a conversation for this on the [numba issue
tracker](https://github.com/numba/numba/issues/3026)


### Future Work

This was a useful experience to build an interesting algorithm.  Most of the
work above took place in an afternoon.  However to make this more valuable to
actual users we need to do a few things:

1.  Build a normal Scikit-Learn style estimator class for this algorithm
    so that people can use it without thinking too much about delayed objects,
    and can instead just use dask arrays or dataframes
2.  Integrate Fabian's other work that uses sparse arrays.  Hopefully on the
    SAGA side this just means doing a type check and then choosing between the
    two algorithms on a task-by-task basis
3.  Resolve the Numba re-deserialization issue, probably by caching functions
    within Dask
