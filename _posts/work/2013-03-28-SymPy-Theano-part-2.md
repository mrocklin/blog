---
layout: post
title:  SymPy -> Theano -- Scalar Simplification
tagline:  
category : work 
tags : [SymPy, Theano]
---
{% include JB/setup %}

Introduction
------------

*This post uses some LaTeX.  You may want to read it on the original site.*

In my [last post](http://matthewrocklin.com/blog/work/2013/03/19/SymPy-Theano-part-1/) I showed how SymPy can benefit from Theano.  In particular Theano provided a mature platform for code generation that outperformed SymPy's attempt at the same problem.  I argued that projects should stick to one specialty and depend on others for secondary concerns.  Interfaces are better than add-ons.

In this post I'll show how Theano can benefit from SymPy.  In particular I'll demonstrate the practicality of SymPy's impressive scalar simplification routines for generating efficient programs.  

After re-reading over this post I realize that it's somewhat long.  I've decided to put the results first in hopes that it'll motivate you to keep reading.

| Project          | operation count  |
|:-----------------|:----------------:|
| SymPy            |       27         |
| Theano           |       24         |
| SymPy+Theano     |       17         |


Now, lets find out what those numbers mean.

Example problem
---------------

We use a larger version of our problem from last time; a radial wavefunction corresponding to `n = 6` and `l = 2` for Carbon (`Z = 6`)

    from sympy.physics.hydrogen import R_nl
    from sympy.abc import x
    n, l, Z = 6, 2, 6
    expr = R_nl(n, l, x, Z)
    print latex(expr)

$$\frac{1}{210} \sqrt{70} x^{2} \left(- \frac{4}{3} x^{3} + 16 x^{2} - 56 x + 56\right) e^{- x}$$

We want to generate code to compute both this expression and its derivative.  Both SymPy and Theano can compute and simplify derivatives.  In this post we'll measure the complexity of a computation that simultaneously computes both the above expression and its derivative.  We'll arrive at this computation through a couple of different routes that use overlapping parts of SymPy and Theano.  This will supply a couple of direct comparisons.

*Disclaimer: I've chosen a larger expression here to exaggerate results.  Simpler expressions yield less impressive results.*

Simplification
--------------

We show the expression, it's derivative, and SymPy's simplification of that derivative.  In each case we quantify the complexity of the expression by the number of algebraic operations

**The target expression:**

    print latex(expr)

$$\frac{1}{210} \sqrt{70} x^{2} \left(- \frac{4}{3} x^{3} + 16 x^{2} - 56 x + 56\right) e^{- x}$$

    print "Operations: ", count_ops(expr)
    Operations:  17

**It's derivative**

    print latex(expr.diff(x))

$$ \frac{1}{210} \sqrt{70} x^{2} \left(- 4 x^{2} + 32 x - 56\right) e^{- x} - \frac{1}{210} \sqrt{70} x^{2} \left(- \frac{4}{3} x^{3} + 16 x^{2} - 56 x + 56\right) e^{- x} + \frac{1}{105} \sqrt{70} x \left(- \frac{4}{3} x^{3} + 16 x^{2} - 56 x + 56\right) e^{- x} $$

    print "Operations: ", count_ops(expr.diff(x))
    Operations:  48

**The result of `simplify`** on the derivative.  Note the significant cancellation of the above expression.

    print latex(simplify(expr.diff(x)))

$$ \frac{2}{315} \sqrt{70} x \left(x^{4} - 17 x^{3} + 90 x^{2} - 168 x + 84\right) e^{- x} $$
    
    print "Operations: ", count_ops(simplify(expr.diff(x)))
    Operations:  18

**An unevaluated derivative object**.  We'll end up passing this to Theano so that it computes the derivative on its own.

    print latex(Derivative(expr, x))

$$ \frac{\partial}{\partial x}\left(\frac{1}{210} \sqrt{70} x^{2} \left(- \frac{4}{3} x^{3} + 16 x^{2} - 56 x + 56\right) e^{- x}\right) $$

Bounds on the cost of Differentiation
-------------------------------------

Scalar differentiation is actually a very simple transformation.  

You need to know how to transform all of the elementary functions (`exp, sin, cos, polynomials, etc...`), the chain rule, and that's it.  Theorems behind automatic differentiation state that the cost of a derivative will be at most five times the cost of the original.  In this case we're guaranteed to have at most `17*5 == 85` operations in the derivative computation; this holds in our case because `48 < 85`

However derivatives are often far simpler than this upper bound.  We see that after simplification the operation count of the derivative is `18`, only one more than the original.  This is common.


Theano Simplification
---------------------

Like SymPy, Theano transforms graphs to mathematically equivalent but computationally more efficient representations.  It provides standard compiler optimizations like constant folding, and common sub-expressions as well as array specific optimizations like the element-wise operation fusion.  

Because users regularly handle mathematical terms Theano also provides a set of optimizations to simplify some common scalar expressions.  For example Theano will convert expressions like `x*y/x` to `y`.  In this sense it overlaps with SymPy's `simplify` functions.  This post is largely a demonstration that SymPy's scalar simplifications are far more powerful than Theano's and that their use can result in significant improvements.  This shouldn't be surprising.  Sympians are devoted to scalar simplification to a degree that far exceeds the Theano community's devotion to this topic.


Experiment
----------

We'll compute the derivative of our radial wavefunction and then simplify the result.  We'll do this using both SymPy's derivative and simplify routines and using Theano's derivative and simplify routines.  We'll then compare the two results by counting the number of required operations.

Here is some setup code that you can safely ignore:

{% highlight python %}
def fgraph_of(*exprs):
    """ Transform SymPy expressions into Theano Computation """
    outs = map(theano_code, exprs)
    ins = theano.gof.graph.inputs(outs)
    ins, outs = theano.gof.graph.clone(ins, outs)
    return theano.gof.FunctionGraph(ins, outs)

def theano_simplify(fgraph):
    """ Simplify a Theano Computation """
    mode = theano.compile.get_default_mode().excluding("fusion")
    fgraph = fgraph.clone()
    mode.optimizer.optimize(fgraph)
    return fgraph

def theano_count_ops(fgraph):
    """ Count the number of Scalar operations in a Theano Computation """
    return len(filter(lambda n: isinstance(n.op, theano.tensor.Elemwise),
                      fgraph.apply_nodes))

{% endhighlight %}

In SymPy we create both an unevaluated derivative and a fully evaluated and sympy-simplified version.  We translate each to Theano, simplify within Theano, and then count the number of operations both before and after simplification.  In this way we can see the value added by both SymPy's and Theano's optimizations.

{% highlight python %}
exprs = [Derivative(expr, x),    # derivative computed in Theano
         simplify(expr.diff(x))] # derivative computed in SymPy, also sympy-simplified

for expr in exprs:
    fgraph = fgraph_of(expr)
    simp_fgraph = theano_simplify(fgraph)
    print latex(expr)
    print "Operations:                             ", theano_count_ops(fgraph)
    print "Operations after Theano Simplification: ", theano_count_ops(simp_fgraph)
{% endhighlight %}


Theano Only

$$ \frac{\partial}{\partial x}\left(\frac{1}{210} \sqrt{70} x^{2} \left(- \frac{4}{3} x^{3} + 16 x^{2} - 56 x + 56\right) e^{- x}\right) $$

    Operations:                              40
    Operations after Theano Simplification:  21

SymPy + Theano

$$ \frac{2}{315} \sqrt{70} x \left(x^{4} - 17 x^{3} + 90 x^{2} - 168 x + 84\right) e^{- x} $$ 

    Operations:                              13
    Operations after Theano Simplification:  10

Analysis
--------

On its own Theano produces a derivative expression that is about as complex as the unsimplified SymPy version.  Theano simplification then does a surprisingly good job, roughly halving the amount of work needed (`40 -> 21`) to compute the result.  If you dig deeper however you find that this isn't because it was able to algebraically simplify the computation (it wasn't) but rather because the computation contained several common sub-expressions.  The Theano version looks a lot like the unsimplified SymPy version.  Note the common sub-expressions like `56*x` below.

$$ \frac{1}{210} \sqrt{70} x^{2} \left(- 4 x^{2} + 32 x - 56\right) e^{- x} - \frac{1}{210} \sqrt{70} x^{2} \left(- \frac{4}{3} x^{3} + 16 x^{2} - 56 x + 56\right) e^{- x} + \frac{1}{105} \sqrt{70} x \left(- \frac{4}{3} x^{3} + 16 x^{2} - 56 x + 56\right) e^{- x} $$

The pure-SymPy simplified result is again substantially more efficient (`13` operations).  Interestingly Theano is still able to improve on this, again not because of additional algebraic simplification but rather due to constant folding.  The two projects simplify in orthogonal ways.


Simultaneous Computation
------------------------

When we compute both the expression and its derivative simultaneously we find substantial benefits from using the two projects together.

{% highlight python %}
orig_expr = R_nl(n, l, x, Z)
for expr in exprs:
    fgraph = fgraph_of(expr, orig_expr)
    simp_fgraph = theano_simplify(fgraph)
    print latex((expr, orig_expr))
    print "Operations:                             ", len(fgraph.apply_nodes)
    print "Operations after Theano Simplification: ", len(simp_fgraph.apply_nodes)
{% endhighlight %}

$$ \begin{pmatrix}\frac{\partial}{\partial x}\left(\frac{1}{210} \sqrt{70} x^{2} \left(- \frac{4}{3} x^{3} + 16 x^{2} - 56 x + 56\right) e^{- x}\right), & \frac{1}{210} \sqrt{70} x^{2} \left(- \frac{4}{3} x^{3} + 16 x^{2} - 56 x + 56\right) e^{- x}\end{pmatrix} $$

    Operations:                              57
    Operations after Theano Simplification:  24

$$ \begin{pmatrix}\frac{2}{315} \sqrt{70} x \left(x^{4} - 17 x^{3} + 90 x^{2} - 168 x + 84\right) e^{- x}, & \frac{1}{210} \sqrt{70} x^{2} \left(- \frac{4}{3} x^{3} + 16 x^{2} - 56 x + 56\right) e^{- x}\end{pmatrix} $$

    Operations:                              27
    Operations after Theano Simplification:  17

The combination of SymPy's scalar simplification and Theano's common sub-expression optimization yields a significantly simpler computation than either project could do independently.

To summarize

| Project          | operation count  |
|:-----------------|:----------------:|
| SymPy            |       27         |
| Theano           |       24         |
| SymPy+Theano     |       17         |

References
----------

*   [A script of this session]({{ BASE_PATH }}/scripts/sympy_theano_simplification.py)
