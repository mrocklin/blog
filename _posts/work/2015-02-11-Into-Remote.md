---
layout: post
title: Into and Remote Data
tagline: Mucking about with `ssh` and `hdfs`
draft: True
category : work
tags : [scipy, Python, Programming, Blaze]
---
{% include JB/setup %}

**tl;dr `into` now handles data on remote machines, including HDFS and the Hive
Metastore (kinda).**


Motivation
----------

[Last week]({{ BASE_PATH }}/work/2015/02/03/Into/) I wrote about
[`into`](http://into.readthedocs.org), a library to migrate data between
formats.  We saw that a network of pairwise data conversions can robustly
migrate data, eliminating some of the frustration of data science.

This frustration compounds when data lives on other computers or distributed
file systems like HDFS.  Moving data from your local machine into something
like the Hive metastore often requires several steps.

1.  `scp` data to cluster
2.  `hadoop fs -cp` data to HDFS
3.  `CREATE TABLE` in Hive/Impala to register data with metastore
4.  Write SQL queries

While each of these steps may be relatively straightforward, their combination
can be daunting to the casual analyst.

<a href="http://into.readthedocs.org/en/latest/_images/hdfs.png">
    <img src="http://into.readthedocs.org/en/latest/_images/hdfs.png"
         align="right" width="50%"></a>


Remote data and into
--------------------

So we took this as a case study and extended the `into` network appropriately.
We integrate the following libraries and protocols

*  `ssh://hostname:myfile.csv` accesses data on remote machines through `paramiko`
*  `hdfs://hostname:myfile.csv` accesses data on the Hadoop distributed file
    system through WebHDFS using the `pywebhdfs` library
*  `hive://hostname::tablename` accesses data on the Hive Metastore using a
    combination of SQLAlchemy and hand crafted `CREATE TABLE` / `LOAD`
    statements


SSH
---

`into` is now a fancy `scp`.

{% highlight Python %}
>>> auth = {'username': 'alice',
...         'key_filename': '.ssh/id_rsa'}

>>> into('ssh://hostname:myfile.csv', 'myfile.csv', **auth)   # Move local file
>>> into('ssh://hostname:myfile.csv', 'myfile.json', **auth)  # Move local file
{% endhighlight %}

Because we're connected to the network, lots of other things work too.

{% highlight Python %}
>>> df = into(pd.DataFrame, 'ssh://hostname:myfile.json', **auth)
{% endhighlight %}

Note that we're not calling any code on the remote machine so fancy conversions
always happen locally.

If you'd like to use ssh generally you might want to take a look at
[Paramiko](http://www.paramiko.org/) which is really doing all of the heavy
lifting here.


HDFS
----

WebHDFS is a web interface to the Hadoop File System.  It is surprisingly high
performance (I often erroneously think of HTTP as slow) but isn't always turned
on in every instance.  If it is then you should be able to transfer data in and
out easily, just as we did for `SSH`

{% highlight Python %}
>>> auth = {'user': 'hdfs',
...         'port': '14000'}
>>> into('hdfs://hostname:myfile.csv', 'myfile.csv', **auth)
{% endhighlight %}


Hive
----

The interesting piece comes when we come to Hive, which, in `into` parlance
expects one of the following kinds of data:

    ssh://single-file.csv
    ssh://directory-of-files/*.csv
    hdfs://directory-of-files/*.csv

And so we build these routes, enabling operations like the following:

{% highlight Python %}
>>> into('hive://hostname/default::mytable',
...      'ssh://hostname:myfile.csv' **auth)
>>> into('hive://hostname/default::mytable',
...      'ssh://hostname:mydata/*.csv' **auth)
>>> into('hive://hostname/default::mytable',
...      'hdfs://hostname:mydata/*.csv' **auth)
{% endhighlight %}

But Hive is also a bit finicky.  Blaze uses the
[PyHive](https://github.com/dropbox/PyHive/) sqlalchemy dialect to query Hive
tables; unfortunately the way Hive works we need to create them by hand.  Hive
is different from most databases in that it doesn't have an internal format.
Instead, it represents tables as directories of CSV files (or other things).
This distinction mucks up `into`'s approach a bit but things work ok in normal
situations.


Lessons Learned
---------------

We had to add a couple new ideas to `into` to expand out to these systems.

### Type Modifiers

First, we needed a way to refer to different variants of the same format of
file.  For example, for CSV files we now have the following variants

    A local CSV file
    A CSV file accessible through HDFS
    A CSV file accessible through SSH
    A directory of CSV files
    A directory of CSV files on HDFS
    ...

And the same for JSON, text, etc..  Into decides what conversion functions to
run based on the type of the data, so in principle we need subclasses for all
combinations of format and location.  Yuck.

To solve this problem we create functions, `SSH, HDFS, Directory` to create
subclasses, we call these *type modifiers*.  So `SSH(CSV)` is a new type that
acts like a CSV file and like the hidden `_SSH` superclass.

{% highlight Python %}
>>> SSH(CSV)('/path/to/data', delimiter=',', user='ubuntu')
>>> Directory(JSON)('/path/to/data/')
{% endhighlight %}

Note that users don't usually see these (unless they want to be explicit) they
usually interact with uri strings.


### Temporary files

Second, we need a way to route through temporary files.  E.g. consider the
following route:

    SSH(CSV) -> CSV -> pd.DataFrame

Each step of this path is quite easy given `paramiko` and `pandas`.  However we
don't want the intermediate CSV file to hang around (users would hate us if we
slowly filled up their `/tmp` folder.)  We need to clean it up when we're done.

To solve this problem, we introduce a new type modifier, `Temp`, that `drop`s
itself on garbage collection (`drop` is another magic function in `into`, [see
docs](http://into.readthedocs.org/en/latest/drop.html)).  This lets us tie the
Python garbage collector to persistent data outside of the Python process.
It's not fool-proof, but it is pretty effective.

    SSH(CSV) -> Temp(CSV) -> pd.DataFrame

This is also a good example of how we build type modifiers.  You can safely
ignore the following code:

{% highlight Python %}
class _Temp(object):
    """ Temporary version of persistent storage

    >>> from into import Temp, CSV
    >>> csv = Temp(CSV)('/tmp/myfile.csv', delimiter=',')
    """
    def __del__(self):
        drop(self)

def Temp(cls):
    return type('Temp(%s)' % cls.__name__, (_Temp, cls), {'persistent_type': cls})

from toolz import memoize
Temp.__doc__ = _Temp.__doc__
Temp = memoize(Temp)
{% endhighlight %}

I won't be surprised if this approach concerns a few people.  I've found it to
be very effective in practice.


### Keyword Arguments

The number of possible keyword arguments to a single `into` call is increasing.
We don't have a good mechanism to help users discover the valid options for
their situation.  Docstrings are hard here because the options depend on the
source and target inputs.  For the moment we're solving this with [online
documentation](http://into.readthedocs.org) for each complicated format but
there is probably a better solution out there.


Help!
-----

The new behavior around `ssh://` and `hdfs://` and `hive://` is new, error
prone, and could really use play-testing.  I strongly welcome feedback and
error reporting here.  You could
[file an issue](https://github.com/ContinuumIO/into/issues/new)
or e-mail blaze-dev@continuum.io.


Other
-----

I didn't mention anything about `S3` and `RedShift` support that was also
recently merged.  This is because I think Phil Cloud might write a separate
blogpost about it.  We did this work in parallel in an effort to hash out how
best to solve the problems above.  I think it worked decently well

Also, we've added an `into` command line interface.  It works just like the
into function with strings, except that we've reversed the order of the
arguments to be more like `cp`.  An example is below:

    $ into source target --key value --key value --key value
    $ into myfile.csv ssh://hostname:myfile.json --delimter ','

We also have docs!
[http://into.readthedocs.org/en/latest/](http://into.readthedocs.org/en/latest/)
