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

>>> # Set up a mathematical problem to solve
>>> X = MatrixSymbol('X', n, n)
>>> Z = MatrixSymbol('Z', n, n)
>>> target = (4*X*X.T + 2*Z).I*X
>>> assumptions = (Q.positive_definite(X) & Q.positive_definite(Z) &
                   Q.symmetric(Z))
{% endhighlight %}

We have described a set of BLAS operations to perform certain transformations when the right conditions are met.  Each BLAS operation is a single rewrite rule.  

{% highlight python %}
>>> from sympy.matrices.expressions.gen import rr_from_blas
>>> from sympy.matrices.expressions.blas import   GEMM, SYMM, TRMM, TRSV
>>> from sympy.matrices.expressions.lapack import POSV, GESV
>>> routines = (TRSV, POSV, GESV, TRMM, SYMM, GEMM)
>>> rules = [rr_from_blas(r, assumptions) for r in routines]
{% endhighlight %}

Each of these rules can convert one kind of expression into a computation given
certain conditions. For example

    SYMM:  alpha A B + beta C -> SYMM(alpha, A, B, beta, C) if A or B are symmetric

We need to combine them to turn the large target expression into a set of atomic inputs.  Some of the BLAS routines overlap so there are potentially many possibilities.

{% highlight python %}
>>> from sympy.matrices.expressions.gen import top_down 
>>> from sympy.rules.branch import multiplex

>>> rule = top_down(multiplex(*rules))

>>> computations = list(rule(target))
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
      info = f(x,z,[n])
    Required arguments:
      x : in/output rank-2 array('d') with bounds (n,n)
      z : in/output rank-2 array('d') with bounds (n,n)
    Optional arguments:
      n := shape(x,0) input int
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

Code Separation
---------------

The definition of BLAS/LAPACK is separated from the pattern matching code and the branching control code. This allows me (or other people) to develop one without thinking about the other. It also allows for a declarative definition of BLAS and LAPACK routines. If anyone is interested I could use more routines than just the six used in this example. 

This project requires the technology from the previous four posts. While all of that technology (strategies, unification, code generation) is necessary to this project none of it is specific to this project. All of the pieces are general, composable, and applicable to other ends. I hope that others are able to find some use for them. 

Caveats
-------

This code is still experimental. It is not yet merged into the SymPy master branch. The interface may change. Results are promising but there are stil big pieces missing before its ready for public use.

References
----------

1.  [F2PY](http://cens.ioc.ee/projects/f2py2e/)
2.  [Example code]({{ BASE_PATH }}/storage/blas_prelim.py) from this post
3.  [BLAS branch](https://github.com/mrocklin/sympy/tree/blas)
