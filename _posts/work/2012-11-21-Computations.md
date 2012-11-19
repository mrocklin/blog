---
layout: post
title: Computations
tagline: beyond expression trees
category : work
draft : true
tags : [SymPy]
---
{% include JB/setup %}

We normally represent our expressions as trees.  Each node in our graph is an expression. It depends on some operation like `Add` or `Mul` and a sequence of arguments.

![blah](/images/add-mul-tree.png)

While trees are a very convenient data structure they are also very restrictive. Consider the following operation

![blah](/images/min-max-dag.png)

The `MinMax` operation takes two variables, `x`, and `y`, and computes the minimum and maximum of the pair.  For computational convenience this can happen all at once rather than with two separate `Min` and `Max` operations.  It only takes one comparison.  

Because the `MinMax` operation has two outputs we can no longer represent its graph with a tree, we need a more general data structure.  This graph can be described as a bipartite directed acyclic graph.  It is bipartite because there are two types of nodes, variables and operations.  It is directed and acyclic by the dependence of data (`MinMax` needs `x` and `y`).

Computation Type
----------------

Enter the `Computation` base type.  This is an abstract interface that must provide a tuples of `inputs` and `outputs` instead of the standard `args` for trees.

We also add a `CompositeComputation` type which collects many computations together.  Consider the collection of the following computations.

![](/images/min-max-dag.png)
![](/images/op.png)

This computation also has inputs (`w`, `y`) and outputs (`Min(x, y)`, `Max(x, y)`).  Note that `x` is no longer an input.  The data dependencies also infer an ordering.  We can infer that the `A` computation must occur before the `MinMax` computation.

Relation to other work
----------------------

There are a number of projects, both within and external to Python, that create and manipulate DAGs of computations.  
