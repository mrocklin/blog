---
layout: post
title: Introducing Blaze - Expressions
tagline: interfaces for tabular data
category : work
draft : true
tags : [scipy, Python, Programming]
---
{% include JB/setup %}

**tl;dr Blaze abstracts tabular computation, providing uniform access to a
variety of database technologies**

Introduction
------------

NumPy and Pandas couple a high level interface with fast low-level computation.
They allow us to manipulate data intuitively and efficiently.

Occasionally we run across a dataset that is too big to fit in our computer's
memory.  In this case NumPy and Pandas don't fit our needs and we look to
other tools to manage and analyze our data.  Popular choices include databases
like Postgres and MongoDB, out-of-disk storage systems like PyTables and BColz
and the menagerie of HDFS tools building from Hadoop and Spark.

Each of these systems has their own strengths and weaknesses and an experienced
data analyst will choose the right tool for the problem at hand.  Unfortunately
learning how each system works and pushing data into the proper form often
takes most of the data scientist's time.

*The startup costs of learning to munge and migrate data between new
technologies often dominate biggish-data analytics.*

Blaze strives to reduce this friction.  Blaze provides a uniform interface to
a variety of database technologies and abstractions for migrating data to and
fro.


Expressions
-----------

At its core, Blaze is an way to express data and computations.

In the following example we build an abstract table for accounts in a
simple bank.  We then describe query, `deadbeats`, to find the names of the
account holders with a negative balance.

{% highlight Python %}
from blaze import *
accounts = TableSymbol('accounts', '{id: int, name: string, amount: int}')

# The names of account holders with negative balance
deadbeats = accounts[accounts['amount'] < 0]['name']
{% endhighlight %}

Programmers familiar with Pandas should find the syntax to create `deadbeats`
familiar.  Note that we haven't actually done any work yet.  The table
`accounts` is purely imaginary and so the `deadbeats` expression is just an
expression of intent.  The Pandas-like syntax builds up a graph of operations
to perform later.

However, if we happen to have some similarly shaped data lying around

{% highlight Python %}
L = [[1, 'Alice',   100],
     [2, 'Bob',    -200],
     [3, 'Charlie', 300],
     [4, 'Dennis',  400],
     [5, 'Edith',  -500]]
{% endhighlight %}

We can combine our expression, `deadbeats` with our data `L` to compute an
actual result

{% highlight Python %}
>>> list(compute(deadbeats, L))
['Bob', 'Edith']
{% endhighlight %}

So in its simplest incarnation, Blaze is a way to write down computations
abstractly which can later be applied to real data.


### Multiple Backends - Pandas

Fortunately the `deadbeats` expression can run against many different kinds of
data.  We just computed `deadbeats` against Python lists, here we compute it
against a Pandas DataFrame

{% highlight Python %}
df = DataFrame([[1, 'Alice',   100],
                [2, 'Bob',    -200],
                [3, 'Charlie', 300],
                [4, 'Dennis',  400],
                [5, 'Edith',  -500]],
               columns=['id', 'name', 'amount'])

>>> compute(deadbeats, df)
1      Bob
4    Edith
Name: name, dtype: object
{% endhighlight %}

Note that Blaze didn't perform the computation here, Pandas did (it's good at
that), Blaze just told Pandas what to do.  Blaze doesn't compute results; Blaze
drives other systems to compute results.


### Multiple Backends - MongoDB

To demonstrate some breadth, let's show Blaze driving a Mongo Database.

    $ # We install and run MongoDB locally
    $ sudo apt-get install mongodb-server
    $ mongod &
    $ pip install pymongo

{% highlight Python %}
import pymongo
db = pymongo.MongoClient().db
db.mycollection.insert([{'id': 1, 'name': 'Alice',   'amount':  100},
                        {'id': 2, 'name': 'Bob',     'amount': -200},
                        {'id': 3, 'name': 'Charlie', 'amount':  300},
                        {'id': 4, 'name': 'Dennis',  'amount':  400},
                        {'id': 5, 'name': 'Edith',   'amount': -500}])

>>> compute(deadbeats, db.mycollection)
[u'Bob', u'Edith']
{% endhighlight %}


Recap
-----

To remind you we created a single Blaze query

{% highlight Python %}
accounts = TableSymbol('accounts', '{id: int, name: string, amount: int}')
deadbeats = accounts[accounts['amount'] < 0]['name']
{% endhighlight %}

And then executed that same query against multiple backends

{% highlight Python %}
>>> list(compute(deadbeats, L))          # Python
['Bob', 'Edith']

>>> compute(deadbeats, df)               # Pandas
1      Bob
4    Edith
Name: name, dtype: object

>>> compute(deadbeats, db.mycollection)  # MongoDB
[u'Bob', u'Edith']
{% endhighlight %}

At the time of this writing Blaze supports the following backends

* Pure Python
* Pandas
* MongoDB
* SQL
* PySpark
* PyTables
* BColz


Interactivity
-------------

The separation of expressions and computation is core to Blaze.  It's also
confusing for new users.
NumPy and Pandas have demonstrated the value of immediate data interaction and
having to explicitly call `compute` is a step backward from that goal.

To this end we create the `Table` abstraction, a `TableSymbol` that knows about
a particular data resource.  Operations on this `Table` object produce abstract
expressions just like normal, but statements that would normally print results
to the screen initiate calls to `compute` and then print those results, giving
an interactive feel in a console or notebook

{% highlight Python %}
>>> t = Table(db.mycollection)  # give MongoDB resource to Table
>>> t
   amount  id     name
0     100   1    Alice
1    -200   2      Bob
2     300   3  Charlie
3     400   4   Dennis
4    -500   5    Edith

>>> t[t.amount < 0]
   amount  id   name
0    -200   2    Bob
1    -500   5  Edith
{% endhighlight %}

These expressions generate the appropriate MongoDB queries, call `compute` only
when we print a result to the screen, and then push the result into a
`DataFrame` to use Pandas' excellent tabular printing.  For large datasets we
always append a `.head(10)` call to the expression to only retrieve the sample
of the output necessary to print to the screen;  this avoids large data
transfers when not necessary.

Using the interactive `Table` object we can interact with a variety of
computational backends with the familiarity of a local DataFrame.
