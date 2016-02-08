---
layout: post
title: Computations
tagline: beyond expression trees
category : work
tags : [SymPy]
theme: twitter
---
{% include JB/setup %}

How can we symbolically represent computations? In SymPy we normally represent expressions as trees.  Each node in the graph is an expression; it depends on some operation like `Add` or `Mul` and a sequence of arguments/children.

![]({{ BASE_PATH }}/images/add-mul-tree.png)

While trees are a convenient data structure they are also very restrictive. Consider the following operation

![]({{ BASE_PATH }}/images/min-max-dag.png)

This `MinMax` operation takes two inputs variables, `x`, and `y`, and produces two outputs `Min(x, y)`, `Max(x, y)`.  Computationally you might prefer this over two separate trees because both outputs can be produced at once with a single comparison.  This also supports natural grouping of common sub-expressions.  If `x` and `y` were large trees we would not want two have copies of each in separate `Min` and `Max` trees.

![]({{ BASE_PATH }}/images/min-tree.png)
![]({{ BASE_PATH }}/images/max-tree.png)

Because the `MinMax` operation has two outputs we can no longer represent its graph with a single tree, we need a more general data structure.  This graph can be described as a bipartite directed acyclic graph (BiDAG).  It is bipartite because there are two types of nodes, variables (circles) and operations \[boxes\].  It is directed and acyclic by the dependence of data (e.g. if `Min(x, y)` depends on `x` then `x` can not depend on `Min(x, y)`).

A DAG is the next most restrictive graph subtype.  In some sense this is the smallest generalization we can make.

Computation Type
----------------

Enter the `Computation` base type.  This is an interface that must provide tuples of `inputs` and `outputs` instead of the standard `args` we use for trees.

We also add a `CompositeComputation` type which collects many computations together.  Consider the collection of the following computations.

![]({{ BASE_PATH }}/images/min-max-dag.png)
![]({{ BASE_PATH }}/images/op.png)

Note that `A` produces `x` which is used by `MinMax`.  This computation has inputs (`w`, `y`) and outputs (`Min(x, y)`, `Max(x, y)`).  The data dependencies infer an ordering; the `A` computation must occur before the `MinMax` computation.

Internal Representation
-----------------------

My current implementation of `CompositeComputation` is represented internally as an immutable set of computations.  Inter-computation interactions are inferred as needed by their variables.  We provide methods to form an alternative dict-based data structure with fast access and traversal should performance become necessary.

All variables are assumed immutable and unique.  The intention is that variables should be entirely defined by their mathematical meaning.  The expectation is that the variables are SymPy expressions.

This approach has a focus on immutability and mathematical attributes rather than performance and computational attributes.  For example it is impossible to represent a `Copy` operation within this framework because mathematical meanings of the input and output variable would be identical.  Similarily inplace operations are not checkable in this framework.

Inplace
-------

And yet copies and inplace operations are important parts of real computation.  We make an explicit separation between mathematics-based optimizations and infrastructure-based optimizations (like inplace).  We perform this transition by replacing each variable with a pair that contains a purely mathematical expression (left)  and a purely computational variable (right).

![]({{ BASE_PATH }}/images/min-max-dag-pure.png)

In the example above we see the `MinMax` computation where the `x` and `y` expressions are stored in variables `"x"` and `"y"` and the outputs are stored in dummy variables `"_1"` and `"_2"`.  For performance reasons a computation may write the outputs back into the memory for the inputs as follows (note that the two outputs are stored in the same variables as the inputs.)

![]({{ BASE_PATH }}/images/min-max-dag-inplace.png)

Inplace computations provide higher performance at the cost of memory safety.  We must avoid situations like the following where the `x` variable may be overwritten (for example by `B`) before it is read (by `C`).

![]({{ BASE_PATH }}/images/dangerous-inplace.png)

Motivation
----------

I am working to translate matrix expressions (tree) into a computation (DAG) of BLAS/LAPACK operations.  I do this through setting up and matching mathematical patterns like the following

    alpha*X*Y + beta*Z -> GEMM(alpha, X, Y, beta, Z)

However the available operations (like `GEMM`) are inplace by default.  These two goals of mathematical pattern matching and inplace computations are challenging to solve simultaneously for non-trivial expressions.  My solution has been to consider the mathematical pattern matching problem first and then switch to 'inplace mode' and resolve the inplace issues separately.

Question
--------

Should this be a part of SymPy?
