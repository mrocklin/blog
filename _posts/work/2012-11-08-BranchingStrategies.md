---
layout: post
title: Branching Strategies
tagline: handling divergent rules
category : work 
draft : true
tags : [SymPy]
---
{% include JB/setup %}

In my last post on [strategies](matthewrocklin.com/blog/work/2012/11/07/Strategies/) I introduced a set of higher order functions to represent common control patterns (like `top_down`).  We combined these with transformation rules (like `flatten`) to create complex functions for tree manipulation (like `flatten_tree`)

    rule     :: expr -> expr
    strategy :: parameters, rule -> rule

In my post on [unification](matthewrocklin.com/blog/work/2012/11/01/Unification/) we showed how to easily create rules from patterns.  At the end of this post I described that because patterns might match in multiple ways one rule might produce many different results.  To avoid combinatorial blowup in the number of possible matches we solved this by yielding matches lazily.  

Transformation rules produced by unify don't return values, they yield possible solutions lazily.  How do we reconcile this with our previous notion of rules and strategies? We make a new set of strategies for branching rules.

    branching-rule      :: expr -> {expr} 
    branching-strategy  :: parameters, branching-rule -> branching-rule

In `sympy.rules.branch` we have implemented lazy analogs for the strategies found in `sympy.rules`.  This allows us to apply strategies to transformations like the `sincos_to_one` rule created in the unification post.

{% highlight python %}
    >>> from sympy.rules.branch.traverse import top_down
    >>> from sympy.unify.usympy import patternify
    >>> from sympy.unify.rewrite import rewriterule

    >>> pattern_source = patternify(sin(x)**2 + cos(x)**2, x)
    >>> sincos_to_one = rewriterule(pattern_source, S.One)
    >>> sincos_tree = top_down(sincos_to_one)
    
    >>> list(sincos_tree(2 + c**(sin(a+b)**2 + cos(a+b)**2)))  # see footnote
    [c**1 + 2] 
{% endhighlight %}

Search
------

When we combine many branching rules we increase the number of potential outcomes.  We need to think about how best to manage this growth of possibilities.
