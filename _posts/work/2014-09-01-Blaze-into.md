---
layout: post
title: Introducing Blaze - Migrations
tagline: interfaces for migrating data
category : work
tags : [scipy, Python, Programming]
---
{% include JB/setup %}

**tl;dr Blaze migrates data efficiently between a variety of data stores.**

In our [last post on Blaze expressions](./foo) we showed how Blaze can execute
the same tabular query on a variety of computational backends.  However, this
ability is only useful if you can migrate your data to the new computational
system in the first place.  To help with this, Blaze provides the `into`
function which moves data from one container type to another:

{% highlight Python %}
>>> into(list, (1, 2, 3))
[1, 2, 3]

>>> into(set, (1, 2, 3))
{1, 2, 3}

>>> into(np.ndarray, [1, 2, 3])
array([1, 2, 3])
{% endhighlight %}

The `into` function takes two arguments, `a` and `b`, and it puts the data in
`b` into a container like `a`.  For example, if we have the class iris dataset
in a CSV file (`iris.csv` includes measurements and species of various flowers)


    $ head iris.csv
    SepalLength,SepalWidth,PetalLength,PetalWidth,Species
    5.1,3.5,1.4,0.2,setosa
    4.9,3.0,1.4,0.2,setosa
    4.7,3.2,1.3,0.2,setosa
    4.6,3.1,1.5,0.2,setosa
    5.0,3.6,1.4,0.2,setosa
    5.4,3.9,1.7,0.4,setosa
    4.6,3.4,1.4,0.3,setosa
    5.0,3.4,1.5,0.2,setosa
    4.4,2.9,1.4,0.2,setosa


We can load this csv file into a Python list, a numpy array, and a Pandas
DataFrame, all using the `into` function.

#### List $\leftarrow$ CSV
{% highlight Python %}
csv = CSV('iris.csv')
>>> L = into(list, csv)
>>> L[:4]
[(5.1, 3.5, 1.4, 0.2, u'Iris-setosa'),
 (4.9, 3.0, 1.4, 0.2, u'Iris-setosa'),
 (4.7, 3.2, 1.3, 0.2, u'Iris-setosa'),
 (4.6, 3.1, 1.5, 0.2, u'Iris-setosa')]
{% endhighlight %}

#### NumPy $\leftarrow$ CSV
{% highlight Python %}
>>> x = into(np.ndarray, csv)
>>> x[:4]
rec.array([(5.1, 3.5, 1.4, 0.2, 'Iris-setosa'),
           (4.9, 3.0, 1.4, 0.2, 'Iris-setosa'),
           (4.7, 3.2, 1.3, 0.2, 'Iris-setosa'),
           (4.6, 3.1, 1.5, 0.2, 'Iris-setosa')],
           dtype=[('SepalLength', '<f8'), ('SepalWidth', '<f8'),
           ('PetalLength', '<f8'), ('PetalWidth', '<f8'), ('Species', 'O')])
{% endhighlight %}

#### Pandas $\leftarrow$ CSV
{% highlight Python %}
>>> df = into(DataFrame, csv)
>>> df[:4]
     SepalLength  SepalWidth  PetalLength  PetalWidth         Species
     0            5.1         3.5          1.4         0.2     Iris-setosa
     1            4.9         3.0          1.4         0.2     Iris-setosa
     2            4.7         3.2          1.3         0.2     Iris-setosa
     3            4.6         3.1          1.5         0.2     Iris-setosa
{% endhighlight %}

Again, Blaze isn't doing any of the work, it just calls out to the
`read_csv` function of the appropriate library with the right inputs.


## Demonstrating Breadth

We demonstrate breadth by moving data between more exotic backends


#### SQL $\leftarrow$ CSV

{% highlight Python %}
>>> sql = SQL('sqlite:///iris.db', 'iris', schema=csv.schema)  # SQLite database

>>> into(sql, csv)                  # CSV to SQL migration
<blaze.data.sql.SQL at 0x7fb4305423d0>
{% endhighlight %}


#### MongoDB $\leftarrow$ Pandas
`into` doesn't work just with csv files.  We can use it to convert between any
pair of data types.

{% highlight Python %}
>>> import pymongo
>>> db = pymongo.MongoClient().db
>>> into(db.iris, df)               # Migrate from Pandas DataFrame to MongoDB
Collection(Database(MongoClient('localhost', 27017), u'db'), u'iris')
{% endhighlight %}

And to demonstrate that it's there

{% highlight Python %}
>>> next(db.iris.find())  # First entry from database
{u'PetalLength': 1.4,
 u'PetalWidth': 0.2,
 u'SepalLength': 5.1,
 u'SepalWidth': 3.5,
 u'Species': u'Iris-setosa',
 u'_id': ObjectId('53f6913ff0470512a4e782e6')}
{% endhighlight %}


#### BColz $\leftarrow$ MongoDB

Finally we migrate from a Mongo database to a BColz out-of-core array.

{% highlight Python %}
>>> into(bcolz.ctable, db.iris) # Migrate between MongoDB and BColz
ctable((150,), [('PetalLength', '<f8'), ('PetalWidth', '<f8'), ('SepalLength',
'<f8'), ('SepalWidth', '<f8'), ('Species', '<U15')])
  nbytes: 13.48 KB; cbytes: 319.98 KB; ratio: 0.04
    cparams := cparams(clevel=5, shuffle=True, cname='blosclz')
    [(1.4, 0.2, 5.1, 3.5, u'Iris-setosa') (1.4, 0.2, 4.9, 3.0, u'Iris-setosa')
     (1.3, 0.2, 4.7, 3.2, u'Iris-setosa') (1.5, 0.2, 4.6, 3.1, u'Iris-setosa')
     (1.4, 0.2, 5.0, 3.6, u'Iris-setosa') (1.7, 0.4, 5.4, 3.9, u'Iris-setosa')
     (1.4, 0.3, 4.6, 3.4, u'Iris-setosa') (1.5, 0.2, 5.0, 3.4, u'Iris-setosa')
     ...
{% endhighlight %}


## Robustness and Performance

Blaze leverages known solutions where they exist, for example migrating from
CSV files to SQL databases we use fast the built-in loaders for that particular
database.

Blaze manages solutions where they don't exist, for example when migrating from
a MongoDB to a BColz out-of-core array we stream the database through Python,
translating types as necessary.

More Information
----------------

*   Documentation: [blaze.pydata.org/](http://blaze.pydata.org/)
*   Source: [github.com/ContinuumIO/blaze/](http://github.com/ContinuumIO/blaze/)
*   Install with [Anaconda](https://store.continuum.io/cshop/anaconda/):

        conda install blaze
