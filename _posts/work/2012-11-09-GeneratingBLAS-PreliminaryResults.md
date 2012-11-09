---
layout: post
title: Preliminary BLAS Results
tagline: putting it all together
category : work 
draft : true
tags : [SymPy, Matrices]
---
{% include JB/setup %}

In the last few posts I've built up some independent technology. 

1.  [BLAS and code generation]({{ BASE_PATH }}/work/2012/10/29/Matrix-Computations/) - a logical description
2.  [Unification]({{ BASE_PATH }}/work/2012/11/01/Unification/) - advanced pattern matching
3.  [Strategies]({{ BASE_PATH }}/work/2012/11/07/Strategies/) - programmatic control
4.  [Branching Strategies]({{ BASE_PATH }}/work/2012/11/09/BranchingStrategies/) - control with multiple possibilities

In this post I'll pull them all together for my first substantial results generating Fortran code to call BLAS/LAPACK. Lets go through a working example


We set up a problem that we'd like to solve. This case we try to compute  \\((4 X X^{T} + 2 Z)^{-1} X\\\) where \\( X \\) and \\(Z\\) are positive definite and \\(Z\\) is also symmetric.

{% highlight python %}
>>> from sympy.matrices.expressions.gen import build_rule, top_down,rr_from_blas
>>> from sympy.matrices.expressions import MatrixSymbol

>>> # Set up a mathematical problem to solve
>>> X = MatrixSymbol('X', n, n)
>>> Z = MatrixSymbol('Z', n, n)
>>> target = (4*X*X.T + 2*Z).I*X
>>> assumptions = (Q.positive_definite(X) & Q.positive_definite(Z) &
                   Q.symmetric(Z))
{% endhighlight %}

We have described a set of BLAS operations to perform certain transformations when the right conditions are met.  Each BLAS operation is a single rewrite rule.  We need to combine them to turn the target expression into a set of atomic inputs.  Some of the BLAS routines overlap so there are potentially many possibilities.

{% highlight python %}
>>> computations = list(top_down(build_rule(assumptions))(target))
>>> len(computations)
2
{% endhighlight %}

We generate Fortran code from the first computation

{% highlight python %}
>>> print computations[0].print_Fortran(str, assumptions)
{% endhighlight %}

{% highlight fortran %}
subroutine f(X, Z, INFO, n)

real*8, intent(inout) :: X(n, n)
real*8, intent(inout) :: Z(n, n)
integer, intent(out) :: INFO
integer, intent(in) :: n

call dgemm('N', 'T', n, n, n, 4, X, n, X, n, 2, Z, n)
call dposv(U, n, n, Z, n, X, n, INFO)

RETURN
END
{% endhighlight %}

This solution first uses `GEMM` to multiply \\(4X X^{T} + 2 Z\\). It then uses `POSV` to perform the solve \\((4X X^{T} + 2Z)^{-1} X\\).  The `POSV` routine solves systems the form \\(A^{-1}B\\) where \\(A\\) is symmetric positive definite.  We were able to infer that \\(4X X^{T} + 2Z\\) is symmetric positive definite given the assumptions stated in the problem.  

This computation is in-place. `GEMM` stores its result in the argument `Z`. `POSV` uses `Z` and stores the output in `X`. Note that both `X` and `Z` have been declared with `inout` intents.

This Fortran code is independent of Python or SymPy and can be used in any project. However, if we prefer the Python environment we can bring it back into the Python session with F2PY.

    >>> f = computations[0].build(str, assumptions) 
    >>> f?
    f - Function signature:
      info = f(x,z)
    Required arguments:
      x : in/output rank-2 array('d') with bounds (3,3)
      z : in/output rank-2 array('d') with bounds (3,3)
    Return objects:
      info : int

This function seemlessly accepts numpy arrays

Multiple Matches 
----------------

There were two computations. What was the other? 

{% highlight python %}
>>> len(computations)
2
>>> print computations[1].print_Fortran(str, assumptions)
{% endhighlight %}

{% highlight fortran %}
subroutine f(X, Z, INFO, IPIV, n)

real*8, intent(inout) :: X(n, n)
real*8, intent(inout) :: Z(n, n)
integer, intent(out) :: INFO
integer, intent(out) :: IPIV(n)
integer, intent(in) :: n

call dgemm('N', 'T', n, n, n, 4, X, n, X, n, 2, Z, n)
call dgesv(n, n, Z, n, IPIV, X, n, INFO)

RETURN
END
{% endhighlight %}

This solution uses the general solve `GESV` routine in place of the specialized `POSV` for symmetric positive definite matrices.  Which is best?  In this case `POSV` is likely faster because it is able to use faster algorithms due to the symmetric positive definite assumption.  After looking at both possibilities we choose it. 

For large matrix expressions the number of possible computations may stop us from inspecting all possible solutions.  How can we ensure that the best solution is in the first few?

References
----------

1.  [F2PY](http://cens.ioc.ee/projects/f2py2e/)
2.  [Example code]({{ BASE_PATH }}/storage/blas_prelim.py) from this post
3.  [BLAS branch](https://github.com/mrocklin/sympy/tree/blas)
