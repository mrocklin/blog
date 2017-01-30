---
layout: post
title: Two Simple Ways to Use Scikit Learn and Dask
category: work
draft: true
tags: [Programming, Python, scipy]
theme: twitter
---
{% include JB/setup %}

*This work is supported by [Continuum Analytics](http://continuum.io)
the [XDATA Program](http://www.darpa.mil/program/XDATA)
and the Data Driven Discovery Initiative from the [Moore
Foundation](https://www.moore.org/)*

Summary
-------

This post describes two simple ways to use Dask to parallelize Scikit-Learn
operations either on a single computer or across a cluster.

1.  Use the Dask Joblib backend
2.  Use the `dklearn` projects drop-in replacements for `Pipeline`,
`GridSearchCV`, and `RandomSearchCV`

For the impatient, these look like the following:

# Joblib solution
from joblib import parallel_backend
with parallel_backend('dask.distributed', scheduler_host='scheduler-address:8786'):
    # your now-cluster-ified sklearn code here


# Dask-learn pipeline and GridSearchCV drop-in replacements
# from sklearn.grid_search import GridSearchCV
  from dklearn.grid_search import GridSearchCV
# from sklearn.pipeline import Pipeline
  from dklearn.pipeline import Pipeline
```


Joblib
------

Scikit-Learn already implements parallel algorithms using
[Joblib](https://pythonhosted.org/joblib/) a simple but powerful and mature
library that provides an extensible map operation.  Here is a simple example:

```python
from time import sleep
def slowinc(x):
    sleep(1)  # take a bit of time to simulate real work
    return x + 1

>>> [slowinc(i) for i in range(10)]  # this take 10 seconds
[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

from joblib import Parallel, delayed
>>> Parallel(n_jobs=4)(delayed(slowinc)(i) for i in range(10))  # this takes 3 seconds
[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
```

Dask users will recognize the `delayed` function modifier.  Dask stole this
interface from Joblib.

Many of Scikit-learn's parallel algorithms use Joblib internally.  If we can
extend Joblib to clusters then we get some added parallelism from Scikit-learn
functions immediately.


### Distributed Joblib

Fortunately Joblib provides an interface for other parallel systems to step in
and act as an execution engine.  We can do this with the parallel backend
context manager to run with hundreds or thousands of cores in a nearby cluster:

```python
from joblib import parallel_backend

with parallel_backend('dask.distributed', scheduler_host='scheduler-address:8786'):
    print(Parallel()(delayed(slowinc)(i) for i in list(range(100))))
```

The main value for Scikit-learn users here is that Scikit-learn already uses
`joblib.Parallel` within its code, so this trick works with the Scikit-learn
code that you already have.

So we can use Joblib to parallelize normally on our multi-core processor:

```python
estimator = GridSearchCV(n_jobs=4, ...)  # use joblib on local multi-core processor
```

or we can use Joblib together with Dask to parallelize across a multi-node
cluster:

```
with parallel_backend('dask.distributed', scheduler_host='scheduler-address:8786'):
    estimator = GridSearchCV(...)  # use joblib with Dask cluster
```

(There will be a more thorough example towards the end)

### Limitations

Joblib is used throughout many algorithms in Scikit-learn, but not all.
Generally any operation that accepts an `n_jobs=` parameter is a possible
choice.

From Dask's perspective Joblib's interface isn't ideal.  For example it will
always collect intermediate results back to the main process, rather than
leaving them on the cluster until necessary.  Also Joblib doesn't allow for
more complex operations than a parallel map, so the interaction here is
somewhat limited.

Still though, given the wide use of Joblib-accelerated workflows (particularly
Scikit-learn) this is a simple thing to try if you have a cluster nearby with a
possible large payoff.


Dask-learn Pipeline and Gridsearch
----------------------------------

In July 2016, Jim Crist built and
[wrote about](http://jcrist.github.io/blog.html) a small project,
[dask-learn](https://github.com/dask/dask-learn).  This project was a
collaboration with SKLearn developers and an attempt to see which parts of
Scikit-learn were trivially parallelizable.  By far the most productive thing
to come out of this work were a Daskified `Pipeline`, `GridsearchCV`, and
`RandomSearchCV` objects that handled nested parallelism intelligently.  Jim
was getting significant speedups over SKLearn code just by dropping these
objects in and replacing their Scikit-learn equivalents.

So if you replace the following imports you'll get both better single-threaded
performance *and* the ability to scale out to a cluster:

```python
# from sklearn.grid_search import GridSearchCV
  from dklearn.grid_search import GridSearchCV
# from sklearn.pipeline import Pipeline
  from dklearn.pipeline import Pipeline
```

Here is a simple example from [Jim's more in-depth blogpost](http://jcrist.github.io/dask-sklearn-part-1.html):

```python
from sklearn.datasets import make_classification

X, y = make_classification(n_samples=10000,
                           n_features=500,
                           n_classes=2,
                           n_redundant=250,
                           random_state=42)

from sklearn import linear_model, decomposition
from sklearn.pipeline import Pipeline
from dklearn.pipeline import Pipeline

logistic = linear_model.LogisticRegression()
pca = decomposition.PCA()
pipe = Pipeline(steps=[('pca', pca),
                       ('logistic', logistic)])


#Parameters of pipelines can be set using ‘__’ separated parameter names:
grid = dict(pca__n_components=[50, 100, 150, 250],
            logistic__C=[1e-4, 1.0, 10, 1e4],
            logistic__penalty=['l1', 'l2'])

# from sklearn.grid_search import GridSearchCV
from dklearn.grid_search import GridSearchCV

estimator = GridSearchCV(pipe, grid)

estimator.fit(X, y)
```

SKLearn performs this computation in around 40 seconds while the dask-learn
drop-in replacements take around 10 seconds.  Also, if you add the following
lines to connect to a [running
cluster](http://distributed.readthedocs.io/en/latest/quickstart.html) the whole
thing scales out:

```python
from dask.distributed import Client
c = Client('scheduler-address:8786')
```

Here is a live [Bokeh](http://bokeh.pydata.org/en/latest/) plot of the
computation on a tiny eight process "cluster" running on my own laptop.

<iframe src="https://cdn.rawgit.com/mrocklin/a2a42d71d0dd085753277821e24925a4/raw/e29b24bc656ea619eedfaba9ef176d5f3c19a040/dask-learn-task-stream.html"
        width="800" height="400"></iframe>
