---
layout: post
title:  LogPy - Facts and Relations
tagline: a quick and dirty in-memory database
category : work
theme: twitter
tags : [LogPy, SymPy, scipy]
---
{% include JB/setup %}

In [my last post]({{ BASE_PATH }}/work/2013/01/14/LogPy-Introduction/) I introduced [LogPy](http://github.com/logpy/logpy), a library for logic and relational programming in Python.  In this post I show how LogPy can be used as a quick and dirty in-memory database.


Data
----

As an example we'll look at the 50 states in the US.  We know two things about each state.

1.  Is it coastal? For example California (CA) is coastal because it is next to the Pacific Ocean, Arizona (AZ) is not.
2.  To which other states is it adjacent?  For example California (CA) is adjacent to Oregon (OR), Arizona (AZ) and Nevada (NV).

We express data in LogPy using relations and facts

{% highlight python %}
>>> from logpy import Relation, fact, facts
>>> coastal = Relation()
>>> fact(coastal, 'CA')
{% endhighlight %}

here we have asserted the fact that `'CA'` is coastal.  Lets quickly do this for all of the coastal states

{% highlight python %}
>>> coastal_states = 'WA,OR,CA,TX,LA,MS,AL,GA,FL,SC,NC,VA,MD,DE,NJ,NY,CT,RI,MA,ME,NH,AK,HI'
>>> for state in coastal_states.split(','):
...     fact(coastal, state)
{% endhighlight %}

Adjacency is only slightly more complex to express.  The following code asserts that California (CA) is adjacent to Arizona (AZ) and that California (CA) is adjacent to Oregon (OR).

{% highlight python %}
>>> adjacent = Relation()
>>> fact(adjacent, 'CA', 'AZ')
>>> fact(adjacent, 'CA', 'OR')
{% endhighlight %}

Now we need a list of all adjacent pairs of states.  Fortunately [someone else](http://writeonly.wordpress.com/2009/03/20/adjacency-list-of-states-of-the-united-states-us/) has already compiled such a list.  His data looks like this

    AK
    AL,MS,TN,GA,FL
    AR,MO,TN,MS,LA,TX,OK
    AZ,CA,NV,UT,CO,NM
    CA,OR,NV,AZ
    CO,WY,NE,KS,OK,NM,AZ,UT
    ...

Each line says that the first element is adjacent to the following ones.  So for example Alaska (AK) is adjacent to no states and California (CA) is adjacent to Oregon (OR), Nevada (NV) and Arizona (AZ).  We can parse this file and assert the relevant facts with fairly standard Python code

{% highlight python %}
f = open('examples/data/adjacent-states.txt')  # lines like 'CA,OR,NV,AZ'
adjlist = [line.strip().split(',') for line in f]
f.close()

for L in adjlist:                   # ['CA', 'OR', 'NV', 'AZ']
    head, tail = L[0], L[1:]        # 'CA', ['OR', 'NV', 'AZ']
    for state in tail:
        fact(adjacent, head, state) # e.g. 'CA' is adjacent to 'OR',
                                    #      'CA' is adjacent to 'NV', etc...
{% endhighlight %}

Queries
------

Once have asserted the relevant facts we can run queries with the logical expressions of LogPy.  Recall from the [last post]({{ BASE_PATH }}/work/2013/01/14/LogPy-Introduction/) that we can use relations to express logical goals and use `run` to search for cases that satisfy those goals.  Here are two simple queries

{% highlight python %}
>>> from logpy import var, run
>>> x = var()
>>> print run(0, x, adjacent('CA', 'NY')) # is California adjacent to New York?
()

>>> print run(0, x, adjacent('CA', x))    # all states next to California
('OR', 'NV', 'AZ')
{% endhighlight %}

We can construct more complex queries with multiple goals.  In SQL the following queries would require a `JOIN`

{% highlight python %}
>>> y = var()  # create second variable for complex queries

>>> print run(0, x, adjacent('TX', x),    # all coastal states next to Texas
...                 coastal(x))
('LA',)

>>> print run(5, x, coastal(y),           # five states that border a coastal state
...                 adjacent(x, y))
('VT', 'AL', 'WV', 'DE', 'MA')

>>> print run(0, x, adjacent('TN', x),    # all states adjacent to Tennessee
...                 adjacent('FL', x))    #        and adjacent to Florida
('GA', 'AL')
{% endhighlight %}

Facts and relations are currently indexed by default, yielding relatively fast query times.


Conclusion
----------

LogPy provides a declarative interface to query complex data.  Data is stored
as facts/tuples and queries are expressed as logical goals.  This system is
expressive and can match SQL in many respects.  The use of Logic programming languages for database queries has roots in [Datalog](http://en.wikipedia.org/wiki/Datalog) a subset of Prolog designed for databases.
