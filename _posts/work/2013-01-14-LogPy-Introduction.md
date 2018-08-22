---
layout: post
title:  Introducing LogPy
tagline:
category : work
theme: twitter
tags : [LogPy, SymPy]
---
{% include JB/setup %}

[LogPy](http://github.com/logpy/logpy) is a library for logic and relational programming in Python.  This post contains some introductory examples.

Informative Examples
--------------------

LogPy enables the expression of relations and the search for values which satisfy them.  The following code is the "Hello, world!" of logic programming.  It asks for `1` number, `x`, such that `x == 5`

{% highlight python %}
>>> from logpy import run, eq, membero, var, conde
>>> x = var()
>>> run(1, x, eq(5, x))
(5,)
{% endhighlight %}

Multiple variables and multiple goals can be used simultaneously.  The
following code asks for a number x such that `x == z` and `z == 3`

{% highlight python %}
>>> z = var()
>>> run(1, x, eq(x, z),
              eq(z, 3))
(3,)
{% endhighlight %}

LogPy uses [unification](http://en.wikipedia.org/wiki/Unification_%28computer_science%29), an advanced form of pattern matching, to match within expression trees.
The following code asks for a number, x, such that `(1, 2) == (1, x)` holds.

{% highlight python %}
>>> run(1, x, eq((1, 2), (1, x)))
(2,)
{% endhighlight %}

The above examples use `eq`, a *goal* to state that two expressions are equal.  Other goals exist.  `membero(item, coll)`, a goal, states that `item`
is a member of `coll`, a collection.

The following example uses `membero` twice to ask for 2 values of x, such that x is a member of `(1, 2, 3)` *and* that x is a member of `(2, 3, 4)`.

{% highlight python %}
>>> run(2, x, membero(x, (1, 2, 3)),  # x is a member of (1, 2, 3)
              membero(x, (2, 3, 4)))  # x is a member of (2, 3, 4)
(2, 3)
{% endhighlight %}

We can write other fancier goals too.  Here is a list of all prime numbers
within `1..10`.  `primo` depends on the traditional `prime` and `isprime` functions found in `sympy`.

{% highlight python %}
>>> from logpy.math import primo
>>> run(0, x, (membero, x, (1,2,3,4,5,6,7,8,9,10)),
              (primo, x))
(3, 2, 7, 5)
{% endhighlight %}

Want just a few primes?  Here are five numbers that satisfy the `primo` goal
{% highlight python %}
>>> run(5, x, primo(x))
(2, 3, 5, 7, 11)
{% endhighlight %}


Relations
---------

We often want to state and then query data.  Logic programming represents data a set of facts and represents queries with logical goals.  In the following examples we assert some facts about the Simpsons family, construct queries through logical goals and then run the queries to obtain results.

The following code defines a `parent` relation and uses it to state who fathered whom.

{% highlight python %}
>>> from logpy import Relation, facts
>>> parent = Relation()
>>> facts(parent, ('Homer', 'Bart'),
...               ('Homer', 'Lisa'),
...               ('Abe',  'Homer'))
{% endhighlight %}

We ask some questions using the `parent` relation as a goal constructor.  Who is Bart's father?

{% highlight python %}
>>> run(1, x, parent(x, 'Bart'))  # one x such that x is a parent of Bart
('Homer',)

>>> run(2, x, parent('Homer', x)) # two xs such that Homer is a parent of x
('Lisa', 'Bart')
{% endhighlight %}

We can use intermediate variables for more complex queries.  Who is Bart's grandfather?

{% highlight python %}
>>> y = var()
>>> run(1, x, parent(x, y),
              parent(y, 'Bart'))
('Abe',)
{% endhighlight %}

We can express the grandfather relationship separately.  In this example we use `conde`, a goal constructor for logical *and* and *or*.

{% highlight python %}
>>> def grandparent(x, z):
...     y = var()
...     return conde((parent(x, y), parent(y, z)))

>>> run(1, x, grandparent(x, 'Bart'))
('Abe,')
{% endhighlight %}

`grandparent` demonstrates that we can construct complex relations programmatically.  How would you define sibling?  How about uncle or aunt?  How about descendant?

If you'd like to play with LogPy you can install it with pip or easy_install using

    pip install logic

or clone it directly from github

    git clone git@github.com:logpy/logpy.git

Source is available at [http://github.com/logpy/logpy/](http://github.com/logpy/logpy/), design input and contributions are much appreciated.

Logic Programming in General
----------------------------

Logic and relational programming are making a comeback.  They were popular in the 80s, died during the AI dark ages, and have recently begun a resurgence in the functional programming community.  Logic programs write music, search databases, write numeric algorithms, and build testing frameworks.  It is expressive for a wide class of problems.

The design of LogPy is based off of `miniKanren`, a simple and powerful implementation in Scheme popularized through the `core.logic` Clojure library.


References
----------

1.  [miniKanren](http://kanren.sourceforge.net/)
2.  [core.logic](https://github.com/clojure/core.logic)
3.  [Wikipedia article on Logic Programming](http://en.wikipedia.org/wiki/Logic_programming)
4.  [core.logic primer](https://github.com/clojure/core.logic/wiki/A-Core.logic-Primer)
