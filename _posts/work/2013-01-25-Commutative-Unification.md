---
layout: post
title:  Commutative Unification
tagline: 
category : work 
tags : [LogPy, SymPy]
---

LogPy now supports commutative and associative pattern matching on expression trees.  This is a standard requirement for computer algebra systems like SymPy but not a traditional feature of logic programming systems.

Pattern-matching in LogPy is expressed by the `eq` goal.  This goal relies on unification to match trees of tuples.  Unification is a computational cornerstone of LogPy.  Traditionally `eq` performs exact structural pattern matching.  For example

    (1, x, (5, y, 7))  matches  (1, (2, 3, 4), (5, 6, 7))

with the following substitution
    
    {x: (2, 3, 4), y: 6}

Expression Trees
----------------

We traditionally represent both mathematical expressions and computer programs with expression trees.  For example \\(y * (1 + x)\\) can be visualized as follows

![]({{ BASE_PATH }}/images/arith-expr.png)

We represent this expression in LogPy with tuples.  The head/first element of each tuple is an operation like `add` or `mul`.  All subsequent elements (the tail) are the arguments/children of that expression.  

    y * (x + 1) -> (mul, y, (add, x, 1))

Matching Expression Trees
-------------------------

This form is exactly what we use for unification.  We could match this pattern against the following expression, treating `x` and `y` as wildcard logic variables

    (mul, y, (add, x, 1))  matches  (mul, (pow, 2, 10), (add, 3, 1))

with the following substitution
    
    {x: 3, y: (pow, 2, 10)}

But what about the following?

    (add, x, 1)  matches?  (add, 1, 3)

This doesn't unify.  While the first (`add`, `add`) and second (`x`, `1`) elements can match (if `{x: 1}`) the third elements (`1`, `3`) will not.  

As mathematicians however we know that because `add` is commutative these expressions should match if we are allowed to rearrange the terms in the tail and match `1` to `1` and `x` to `3`.  LogPy doesn't know this by default.  LogPy is not a math library.

Building Commutative Equality
-----------------------------

Given the goal `seteq` for set unification and a goal `conso` for head-tail pattern matching we build `eq_commutative` for commutative matching.  

Example of `seteq`

    run(0, x, seteq((1, 2, x), (3, 1, 2)))  # seteq matches within sets
    (3,)

Example of `conso`

    run(0, head,  conso(head, tail, (1, 2, 3, 4)))
    (1,)
    run(0, tail,  conso(head, tail, (1, 2, 3, 4)))
    ((2, 3, 4),)

Given these two it is easy to build `eq_commutative`


{% highlight python %}
def eq_commutative(u, v):
    operation, utail, vtail = var(), var(), var()
    return lall(conso(operation, utail, u),
                conso(operation, vtail, v),
                commutative(operation),
                seteq(utail, vtail))
{% endhighlight %}

That is we require all of the following (`lall` is logical all).

*   `u` must be of the form `(operation, utail....)`
*   `v` must be of the form `(operation, vtail....)`.  Note that the same variable `operation` must be the same in both expressions.
*   The operation must be commutative (operations register themselves beforehand, see example below)
*   `utail` and `vtail` must unify under set equality.

I am glossing over some details here, like "what about associative matching" and "how does `seteq` work?" but this should give a high-level view of how logic programs are made.  Lets see an example of associative/commutative matching 

Example
-------

This is the [standard example](https://github.com/logpy/logpy/blob/master/examples/commutative.py) for commutative matching found in the [repository](https://github.com/logpy/logpy)

{% highlight python %}
from logpy import run, var, fact
from logpy.assoccomm import eq_assoccomm as eq
from logpy.assoccomm import commutative, associative

# Define some dummy Operationss
add = 'add'
mul = 'mul'

# Register that these ops are commutative using the facts system
fact(commutative, mul)
fact(commutative, add)
fact(associative, mul)
fact(associative, add)

# Define some wild variables
x, y = var('x'), var('y')

# Two expressions to match
pattern = (mul, (add, 1, x), y)                # (1 + x) * y
expr    = (mul, 2, (add, 3, 1))                # 2 * (3 + 1)
print run(0, (x,y), eq(pattern, expr))         
# ((3, 2),) #  meaning one result with x matches to 3 and y matches to 2
{% endhighlight %}

Conclusion
----------

With this LogPy contains all of the functionality of SymPy's old `unify` module but in a cleaner and much more extensible form.
