---
layout: post
title: Streaming Analytics
tagline: Data analytics recipes for PyToolz
category : work
theme: twitter
tags : [scipy, Python, Programming]
---
{% include JB/setup %}

**tl;dr: We demonstrate data workflows with Python data structures and PyToolz.
We also introduce `join`, a new operation in `toolz`.**

Prelude
-------

In my last two posts I show that [Python data structures are
fast](http://mrocklin.github.com/blog/work/2014/05/01/Fast-Data-Structures) and
that
[CyToolz](http://mrocklin.github.com/blog/work/2014/05/01/Introducing-CyToolz),
an implementation of [`toolz`](http://toolz.readthedocs.org) in Cython,
achieves Java speeds on standard Python core data structures like `dict`s,
`list`s, and `tuple`s.  As a reminder, `toolz` provides functions like
`groupby`

{% highlight Python %}
>>> from toolz import groupby

>>> names = ['Alice', 'Bob', 'Charlie', 'Dan', 'Edith', 'Frank']
>>> groupby(len, names)
{3: ['Bob', 'Dan'],
 5: ['Alice', 'Edith', 'Frank'],
 7: ['Charlie']}
{% endhighlight %}

I always give this example when talking about `toolz`.  It often spurs the
following question:

*That looks like `GROUP BY` from SQL.  In what other ways does `toolz` let me
do SQL-like operations in Python?*

My answer for this is to *go look at Pandas* which really does a wonderful job
at in-memory data analytics.  Toolz targets functional programming more than it
targets data analytics.  Still this question is common enough to warrant a
blogpost.  The following is my stock answer on how to use pure Python and
`toolz` (or `cytoolz`) for streaming data analytic workflows like selections,
split-apply-combine, and joins.  I'll note throughout when operations are
streaming (can support datasets bigger than memory) or not.  This is one of the
few ways in which analysis with `toolz` might be preferred over `pandas`.


Streaming Analytics
===================

The toolz functions can be composed to analyze large streaming datasets.
Toolz supports common analytics patterns like the selection, grouping,
reduction, and joining of data through pure composable functions. These
functions often have analogs to familiar operations in other data
analytics platforms like SQL or Pandas.

Throughout this post we'll use this simple dataset of accounts.

{% highlight Python %}
>>> #           id, name, balance, gender
>>> accounts = [(1, 'Alice', 100, 'F'),
...             (2, 'Bob', 200, 'M'),
...             (3, 'Charlie', 150, 'M'),
...             (4, 'Dennis', 50, 'M'),
...             (5, 'Edith', 300, 'F')]
{% endhighlight %}

Selecting with `map` and `filter`
---------------------------------

Simple projection and linear selection from a sequence is achieved
through the standard functions `map` and `filter`.

{% highlight SQL %}
SELECT name, balance
FROM accounts
WHERE balance > 150;
{% endhighlight %}

These functions correspond to the SQL commands `SELECT` and `WHERE`.

{% highlight Python %}
>>> from toolz.curried import pipe, map, filter, get

>>> pipe(accounts, filter(lambda (id, name, balance, gender): balance > 150),
...                map(get([1, 2])),
...                list)
{% endhighlight %}

*note: this uses the [curried](http://toolz.readthedocs.org/en/latest/curry.html) versions of `map` and `reduce`.*


Of course, these operations are also well supported with standard
list/generator comprehension syntax. This syntax is more often used and
generally considered to be more Pythonic.

{% highlight Python %}
>>> [(name, balance) for (id, name, balance, gender) in accounts
...                  if balance > 150]
{% endhighlight %}

Split-apply-combine with `groupby` and `reduceby`
-------------------------------------------------

We separate split-apply-combine operations into the following two
concepts

1.  Split the dataset into groups by some property
2.  Reduce each of the groups with some aggregation function

Toolz supports this common workflow with

1.  a simple in-memory solution
2.  a more sophisticated streaming solution.

### In Memory Split-Apply-Combine

The in-memory solution depends on the functions
[`groupby`](http://toolz.readthedocs.org/en/latest/api.html#toolz.itertoolz.groupby)
to split, and
[`valmap`](http://toolz.readthedocs.org/en/latest/api.html#toolz.itertoolz.valmap)
to apply/combine.

{% highlight SQL %}
SELECT gender, SUM(balance)
FROM accounts
GROUP BY gender;
{% endhighlight %}

We first show `groupby` and `valmap` separately to show the intermediate
groups.

{% highlight Python %}
>>> from toolz import groupby, valmap, compose
>>> from toolz.curried import get, pluck

>>> groupby(get(3), accounts)
{'F': [(1, 'Alice', 100, 'F'), (5, 'Edith', 300, 'F')],
 'M': [(2, 'Bob', 200, 'M'), (3, 'Charlie', 150, 'M'), (4, 'Dennis', 50, 'M')]}

>>> valmap(compose(sum, pluck(2)),
...        _)
{'F': 400, 'M': 400}
{% endhighlight %}

Then we chain them together into a single computation

{% highlight Python %}
>>> pipe(accounts, groupby(get(3)),
...                valmap(compose(sum, pluck(2))))
{'F': 400, 'M': 400}
{% endhighlight %}

### Streaming Split-Apply-Combine

The `groupby` function collects the entire dataset in memory into a
dictionary. While convenient, the `groupby` operation is *not streaming*
and so this approach is limited to datasets that can fit comfortably
into memory.

Toolz achieves streaming split-apply-combine with
[reduceby](http://toolz.readthedocs.org/en/latest/api.html#toolz.itertoolz.reduceby),
a function that performs a simultaneous reduction on each group as the
elements stream in. To understand this section you should first be
familiar with the builtin function `reduce`.

The `reduceby` operation takes a key function, like `get(3)` or `lambda x:
x[3]`, and a binary operator like `add` or `lesser = lambda acc, x: acc if acc
< x else x`. It successively applies the key function to each item in
succession, accumulating running totals for each key by combining each new
value with the previous total using the binary operator. It can't accept full
reduction operations like `sum` or `min` as these require access to the entire
group at once. Here is a simple example:

{% highlight Python %}
>>> from toolz import reduceby

>>> def iseven(n):
...     return n % 2 == 0

>>> def add(x, y):
...     return x + y

>>> reduceby(iseven, add, [1, 2, 3, 4])
{True: 6, False: 4}
{% endhighlight %}

The even numbers are added together `(2 + 4 = 6)` into group `True`, and
the odd numbers are added together `(1 + 3 = 4)` into group `False`.


Note that we have to replace the reduction `sum` with the binary operator
`add`.  The incremental nature of `add` allows us to do the summation work as
new data comes in.  The use of binary operators like `add` over full reductions
like `sum` enables computation on very large streaming datasets.

The challenge to using `reduceby` often lies in the construction of a
suitable binary operator. Here is the solution for our accounts example
that adds up the balances for each group:

{% highlight Python %}
>>> binop = lambda total, (id, name, bal, gend): total + bal

>>> reduceby(get(3), binop, accounts)
{'F': 400, 'M': 400}
{% endhighlight %}

This construction supports datasets that are much larger than available
memory. Only the output must be able to fit comfortably in memory and
this is rarely an issue, even for very large split-apply-combine
computations.

Semi-Streaming `join`
---------------------

We register multiple datasets together with
[join](http://toolz.readthedocs.org/en/latest/api.html#toolz.itertoolz.join).
Consider a second dataset that stores addresses by ID:

{% highlight Python %}
>>> addresses = [(1, '123 Main Street'),  # id, address
...              (2, '5 Adams Way'),
...              (5, '34 Rue St Michel')]
{% endhighlight %}

We can join this dataset against our accounts dataset by specifying
attributes which register different elements with each other; in this
case they share a common first column, id.

{% highlight SQL %}
SELECT accounts.name, addresses.address
FROM accounts, addresses
WHERE accounts.id = addresses.id;
{% endhighlight %}

{% highlight Python %}
>>> from toolz import join, first, second

>>> result = join(first, accounts,
...               first, addresses)

>>> for ((id, name, bal, gender), (id, address)) in result:
...     print((name, address))
('Alice', '123 Main Street')
('Bob', '5 Adams Way')
('Edith', '34 Rue St Michel')
{% endhighlight %}

Join takes four main arguments, a left and right key function and a left
and right sequence. It returns a sequence of pairs of matching items. In our
case the return value of `join` is a sequence of pairs of tuples such that the
first element of each tuple (the ID) is the same.  In the example above we
unpack this pair of tuples to get the fields that we want (`name` and
`address`) from the result.

### Join on arbitrary functions / data

Those familiar with SQL are accustomed to this kind of join on columns.
However a functional join is more general than this; it doesn't need to
operate on tuples, and key functions do not need to get particular
columns. In the example below we match numbers from two collections so
that exactly one is even and one is odd.

{% highlight Python %}
>>> def iseven(n):
...     return n % 2 == 0
>>> def isodd(n):
...     return n % 2 == 1

>>> list(join(iseven, [1, 2, 3, 4],
...           isodd, [7, 8, 9]))
[(2, 7), (4, 7), (1, 8), (3, 8), (2, 9), (4, 9)]
{% endhighlight %}

### Semi-Streaming Join

The Toolz Join operation fully evaluates the *left* sequence and streams
the *right* sequence through memory. Thus, if streaming support is
desired the larger of the two sequences should always occupy the right
side of the join.

### Algorithmic Details

The semi-streaming join operation in `toolz` is asymptotically optimal.
Computationally it is linear in the size of the input + output. In terms
of storage the left sequence must fit in memory but the right sequence
is free to stream.

The results are not normalized, as in SQL, in that they permit repeated
values. If normalization is desired, consider composing with the
function `unique` (note that `unique` is not fully streaming.)

### More Complex Example

The accounts example above connects two one-to-one relationships, `accounts`
and `addresses`; there was exactly one name per ID and one address per ID. This
need not be the case. The join abstraction is sufficiently flexible to join
one-to-many or even many-to-many relationships. The following example finds
city/person pairs where that person has a friend who has a residence in that
city. This is an example of joining two many-to-many relationships because a
person may have many friends and because a friend may have many residences.

{% highlight Python %}
>>> friends = [('Alice', 'Edith'),
...            ('Alice', 'Zhao'),
...            ('Edith', 'Alice'),
...            ('Zhao', 'Alice'),
...            ('Zhao', 'Edith')]

>>> cities = [('Alice', 'NYC'),
...           ('Alice', 'Chicago'),
...           ('Dan', 'Syndey'),
...           ('Edith', 'Paris'),
...           ('Edith', 'Berlin'),
...           ('Zhao', 'Shanghai')]

>>> # Vacation opportunities
>>> # In what cities do people have friends?
>>> result = join(second, friends,
...               first, cities)
>>> for ((name, friend), (friend, city)) in sorted(unique(result)):
...     print((name, city))
('Alice', 'Berlin')
('Alice', 'Paris')
('Alice', 'Shanghai')
('Edith', 'Chicago')
('Edith', 'NYC')
('Zhao', 'Chicago')
('Zhao', 'NYC')
('Zhao', 'Berlin')
('Zhao', 'Paris')
{% endhighlight %}

Join is computationally powerful:

-   It is expressive enough to cover a wide set of analytics operations
-   It runs in linear time relative to the size of the input and output
-   Only the left sequence must fit in memory


Conclusion
----------

Toolz gives a compact set of primitives for data analysis on plain Python data
structures.  CyToolz accelerates those workflows through Cython.  This approach
is both low-tech and supports uncomfortably big data through streaming.

At the same time, Toolz is a general purpose functional standard library, and
is not specifically dedicated to data analysis. While there are obvious
benefits (streaming, composition, etc.) users interested in data analysis might
be better served by using projects dedicated projects like Pandas or
SQLAlchemy.

This post is also part of the
[`toolz` docs](http://toolz.readthedocs.org/en/latest/).
Thanks to
[John Jacobsen](http://johnj.com),
[Clark Fitzgerald](https://github.com/clarkfitzg), and
[Erik Welch](https://github.com/eriknw/)
for their help with this post.
