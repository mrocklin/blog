---
layout: post
title: Pandas Categoricals
category : work
tags : [scipy, Python, Programming]
---
{% include JB/setup %}

**tl;dr: Pandas Categoricals efficiently encode and dramatically improve
performance on data with text categories**

*Disclaimer: Categoricals were created by the Pandas development team and not
by me.*

There is More to Speed Than Parallelism
---------------------------------------

I usually write about parallelism.  As a result people ask me how to
parallelize their slow computations.
The answer is usually **just use pandas** in a better way

*  Q: *How do I make my pandas code faster with parallelism?*
*  A: *You don't need parallelism, you can use Pandas better*

This is almost always simpler and more effective than using multiple cores or
multiple machines.  You should look towards parallelism only after you've
made sane choices about storage format, compression, data representation, etc..

Today we'll talk about how Pandas can represent categorical text data
numerically.  This is a cheap and underused trick to get an order of magnitude
speedup on common queries.


Categoricals
------------

Often our data includes text columns with many repeated elements. Examples:

*  Stock symbols -- `GOOG, APPL, MSFT, ...`
*  Gender -- `Female, Male, ...`
*  Experiment outcomes -- `Healthy, Sick, No Change, ...`
*  States -- `California, Texas, New York, ...`

We usually represent these as text.  Pandas represents text with the `object`
dtype which holds a normal Python string.  This is a common culprit for slow
code because `object` dtypes run at Python speeds, not at Pandas' normal C
speeds.

Pandas categoricals are a new and powerful feature that encodes categorical
data numerically so that we can leverage Pandas' fast C code on this kind of
text data.

{% highlight Python %}
>>> # Example dataframe with names, balances, and genders as object dtypes
>>> df = pd.DataFrame({'name': ['Alice', 'Bob', 'Charlie', 'Danielle'],
...                    'balance': [100.0, 200.0, 300.0, 400.0],
...                    'gender': ['Female', 'Male', 'Male', 'Female']},
...                    columns=['name', 'balance', 'gender'])

>>> df.dtypes                           # Oh no!  Slow object dtypes!
name        object
balance    float64
gender      object
dtype: object
{% endhighlight %}

We can represent columns with many repeats, like gender, more efficiently by
using categoricals.  This stores our original data in two pieces

*  Original data

        Female, Male, Male, Female

1.  Index mapping each category to an integer

        Female: 0
        Male: 1
        ...

2.  Normal array of integers

        0, 1, 1, 0

This integer array is more compact and is now a normal C array.  This allows
for normal C-speeds on previously slow object dtype columns.
Categorizing a column is easy:

{% highlight Python %}
In [5]: df['gender'] = df['gender'].astype('category')  # Categorize!
{% endhighlight %}

Lets look at the result

{% highlight Python %}
In [6]: df                          # DataFrame looks the same
Out[6]:
       name  balance  gender
0     Alice      100  Female
1       Bob      200    Male
2   Charlie      300    Male
3  Danielle      400  Female

In [7]: df.dtypes                   # But dtypes have changed
Out[7]:
name         object
balance     float64
gender     category
dtype: object

In [8]: df.gender                   # Note Categories at the bottom
Out[8]:
0    Female
1      Male
2      Male
3    Female
Name: gender, dtype: category
Categories (2, object): [Female, Male]

In [9]: df.gender.cat.categories    # Category index
Out[9]: Index([u'Female', u'Male'], dtype='object')

In [10]: df.gender.cat.codes        # Numerical values
Out[10]:
0    0
1    1
2    1
3    0
dtype: int8                         # Stored in single bytes!
{% endhighlight %}

Notice that we can store our genders much more compactly as single bytes.  We
can continue to add genders (there are more than just two) and Pandas will
use new values (2, 3, ...) as necessary.

Our dataframe looks and feels just like it did before.  Pandas internals will
smooth out the user experience so that you don't notice that you're actually
using a compact array of integers.


Performance
-----------

Lets look at a slightly larger example to see the performance difference.

We take a small subset of the NYC Taxi dataset and group by medallion ID to
find the taxi drivers who drove the longest distance during a certain period.

{% highlight Python %}
In [1]: import pandas as pd
In [2]: df = pd.read_csv('trip_data_1_00.csv')

In [3]: %time df.groupby(df.medallion).trip_distance.sum().sort(ascending=False,
inplace=False).head()
CPU times: user 161 ms, sys: 0 ns, total: 161 ms
Wall time: 175 ms

Out[3]:
medallion
1E76B5DCA3A19D03B0FB39BCF2A2F534    870.83
6945300E90C69061B463CCDA370DE5D6    832.91
4F4BEA1914E323156BE0B24EF8205B73    811.99
191115180C29B1E2AF8BE0FD0ABD138F    787.33
B83044D63E9421B76011917CE280C137    782.78
Name: trip_distance, dtype: float64
{% endhighlight %}

That took around 170ms.  We categorize in about the same time.

{% highlight Python %}
In [4]: %time df['medallion'] = df['medallion'].astype('category')
CPU times: user 168 ms, sys: 12.1 ms, total: 180 ms
Wall time: 197 ms
{% endhighlight %}

Now that we have numerical categories our computaion runs 20ms, improving by
about an order of magnitude.

{% highlight Python %}
In [5]: %time df.groupby(df.medallion).trip_distance.sum().sort(ascending=False,
inplace=False).head()
CPU times: user 16.4 ms, sys: 3.89 ms, total: 20.3 ms
Wall time: 20.3 ms

Out[5]:
medallion
1E76B5DCA3A19D03B0FB39BCF2A2F534    870.83
6945300E90C69061B463CCDA370DE5D6    832.91
4F4BEA1914E323156BE0B24EF8205B73    811.99
191115180C29B1E2AF8BE0FD0ABD138F    787.33
B83044D63E9421B76011917CE280C137    782.78
Name: trip_distance, dtype: float64
{% endhighlight %}

We see almost an order of magnitude speedup after we do the one-time-operation
of replacing object dtypes with categories.  Most other computations on this
column will be similarly fast.  Our memory use drops dramatically as well.


Conclusion
----------

Pandas Categoricals efficiently encode repetitive text data.  Categoricals are
useful for data like stock symbols, gender, experiment outcomes, cities,
states, etc..  Categoricals are easy to use and greatly improve performance on
this data.

We have several options to increase performance when dealing with
inconveniently large or slow data.  Good choices in storage format,
compression, column layout, and data representation can dramatically improve
query times and memory use. Each of these choices is as important as
parallelism but isn't overly hyped and so is often overlooked.
