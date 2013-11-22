---
layout: post
title:  Parallelism and Serialization
tagline:  functional performance and pickles
category : work
draft: true
tags : [Python, scipy]
---
{% include JB/setup %}

*This is a draft and should not be publicized.  If you find it in a public
place please e-mail Matthew Rocklin.*

**tl;dr:** Multiprocessing in Python is crippled by `pickle`s poor function
serialization.  The more robust serialization package `dill` improves the
situation.  Dill-based solutions for both `multiprocessing` and
IPython.parallel make distributed computing simple again.

To leverage the cores found in modern processors we need to communicate
functions between different processes.  I.e. if we have some function in one
process

{% highlight python %}
def do_expensive_computations(data):
    ...
    return fancy result
{% endhighlight %}

then we need to communicate that functionality *and all functionality on which
it depends* to our other worker processes.

To communicate this function we translate it down into a blob of text, ship
that text over a wire, and then retranslate that text back into a fully
operational function.  This process, called *serialization*, is like
the teleporters in Star Trek; it takes an important thing (function or crew
member) translates it into something manageable (text or bits) moves it quickly
to some other location, and then reassembles it correctly (we hope!)  Just as
accidents happen in Star Trek it's easy for function serialization to go awry.


### Pickle

The standard serialization package in Python is `pickle`.  The `pickle` package
can serialize and deserialize most Python objects, not just functions.

{% highlight python %}
In [1]: import pickle

In [2]: pickle.dumps({'Alice': 100})
Out[2]: "(dp0\nS'Alice'\np1\nI100\ns."

In [3]: pickle.loads("(dp0\nS'Alice'\np1\nI100\ns.")
Out[3]: {'Alice': 100}
{% endhighlight %}

How does Pickle go about serializing functions?

{% highlight python %}
In [4]: from math import sin

In [5]: pickle.dumps(sin)
Out[5]: 'cmath\nsin\np0\n.'
{% endhighlight %}

Pickle specifies a function using its module name (see `math` on the left) and
its function name (see `sin` in the middle).  Sadly this approach fails for
many cases.  In particular `pickle` fails to serialize the following

*   Methods
*   Lambdas
*   Closures
*   Some functions defined interactively

{% highlight python %}
In [2]: pickle.dumps(str.split)
TypeError: can't pickle method_descriptor objects

In [4]: pickle.dumps(lambda x: x**2)
PicklingError: Can't pickle <function <lambda> at 0x1172410>: it's not found as
__main__.<lambda>
{% endhighlight %}

Most large projects use at least one (often all) of these features.  This makes
multiprocessing a pain.


### Multiprocessing

We care about function serialization because we want to send one function to
many processes in order to leverage parallelism.  The standard way to do this
is with the `multiprocessing` module.  One simple approach is with the `Pool`
abstraction

{% highlight python %}
In [12]: import multiprocessing as mp

In [13]: p = mp.Pool(4)  # Processing Pool with four processors

In [14]: p.map(sin, range(10))
Out[14]:
[0.0,
 0.8414709848078965,
 0.9092974268256817,
 0.1411200080598672,
-0.7568024953079282,
-0.9589242746631385,
-0.27941549819892586,
 0.6569865987187891,
 0.9893582466233818,
 0.4121184852417566]
{% endhighlight %}

But `multiprocessing` uses `pickle` and so inherits its limitations.  Here it
fails to serialize and broadcast a lambda `square` function.

{% highlight python %}
In [15]: p.map(lambda x: x**2, range(10))
PicklingError: Can't pickle <type 'function'>: attribute lookup
__builtin__.function failed
{% endhighlight %}

I rarely see `multiprocessing` in the wild.  I suspect that this is because
poor function serialization makes it a pain for any but the most trivial
of projects.


### `dill` replaces `pickle`

The `dill` library is a drop-in alternative to `pickle` that *can* robustly
handle function serialization.

{% highlight python %}
In [8]: import dill

In [4]: dill.dumps(str.split)
Out[4]:
'cdill.dill\n_getattr\np0\n(cdill.dill\n_load_type\np1\n(S\'StringType\'\np2\ntp3\nRp4\nS\'split\'\np5\nS"<method\'split\' of \'str\' objects>"\np6\ntp7\nRp8\n.'

In [9]: dill.dumps(lambda x: x)
Out[9]:
'\x80\x02cdill.dill\n_load_type\nq\x00U\x0cFunctionTypeq\x01\x85q\x02Rq\x03(cdill.dill\n_unmarshal\nq\x04Usc\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00C\x00\x00\x00s\x04\x00\x00\x00|\x00\x00S(\x01\x00\x00\x00N(\x00\x00\x00\x00(\x01\x00\x00\x00t\x01\x00\x00\x00x(\x00\x00\x00\x00(\x00\x00\x00\x00s\x1e\x00\x00\x00<ipython-input-9-70b342a16b4d>t\x08\x00\x00\x00<lambda>\x01\x00\x00\x00s\x00\x00\x00\x00q\x05\x85q\x06Rq\x07c__builtin__\n__main__\nU\x08<lambda>q\x08NNtq\tRq\n.'
{% endhighlight %}

As a result most of the speed-bumps of using multiprocessing *should*
disappear.


### Dill and Multiprocessing

The makers of `dill` apparently know this and so have developed their own fork
of `multiprocessing` that uses dill.  This resides in the `pathos` library

{% highlight python %}
In [1]: import pathos.multiprocessing as mp

In [2]: p = mp.Pool(4)  # Processing Pool with four processors

In [3]: p.map(lambda x: x**2, range(10))
Out[3]: [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]
{% endhighlight %}


### Dill and IPython Parallel

You should know about IPython parallel.

The IPython notebook has gotten a lot of press recently.  The notebook became
possible after the project was restructured to separate computation and
interaction.  One important result is that we can now perform computation in a
process while interacting in a web browser, giving rise to the ever-popular notebook.

This same computation-is-separate-from-interaction concept supports other
innovations.  In particular IPython parallel uses this to create a simple
platform for both multiprocessing and distributed computing.

    mrocklin@notebook:~$ ipcluster start --n=4
    mrocklin@notebook:~$ ipython

{% highlight python %}
In [1]: from IPython.parallel import Client

In [2]: p = Client()[:]

In [3]: p.map_sync(lambda x: x**2, range(10))
Out[3]: [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]
{% endhighlight %}

Note that this system handles the lambda without failing.  IPython performs
some custom serializations on top of `pickle`.  Unfortunately these
customizations still don't cover *all* use cases.  Fortunately IPython provides
hooks to specify your preferred serialization technique.  Thanks to a recent
change, IPython views now provide a convenient `.use_dill` method.

{% highlight python %}
In [4]: p.use_dill()

In [5]: p.map_sync(str.split, ['Hello world!', 'foo bar'])
[['Hello', 'world!'], ['foo', 'bar']]
{% endhighlight %}

A more explicit treatment of switching IPython's serializers to dill can be
found in [this notebook](http://nbviewer.ipython.org/5241793).


Acknowledgements
----------------

My interest into multiprocessing and serialization was originally spurred by a
talk by [Ian Langmore](http://ianlangmore.com/about).

The `dill` project is developed by [Mike
Mckerns](http://www.cacr.caltech.edu/~mmckerns/my).  Several people have
pointed it out to me.  These include @asmeurer, @themodernscientist, @tweicki,
and @davidli.

Special thanks to @mmckerns and @minrk for their recent interactions to resolve
issues related to this topic.

Once we get past the serialization issue embarrassingly parallel processing in
Python should be trivial.
