---
layout: post
title: Matrix Computations in SymPy
tagline: Encoding mathematical BLAS
category : work 
tags : [SymPy, Matrices]
---
{% include JB/setup %}

I want to translate matrix expressions like this

{% highlight python %}

    (alpha*A*B).I * x

{% endhighlight %}

Into Fortran code that call BLAS and LAPACK code like this

{% highlight fortran %}

    subroutine f(alpha, A, B, x, n)

    real*8,  intent(in)     :: A(n, n)
    real*8,  intent(inout)  :: B(n, n)
    real*8,  intent(in)     :: alpha
    integer, intent(in)     :: n
    real*8,  intent(inout)  :: x(n, 1)

    call dgemm('N', 'N', n, n, n, alpha, A, n, B, n, 0, B, n)
    call dtrsv('L', 'N', 'N', n, B, n, x, 1)

    RETURN
    END

{% endhighlight %}

And then call it in Python like this

{% highlight python %}

    nA, nB, nx = .... # Get numpy arrays
    f(nalpha, nA, nB.T, nx.T)) 

{% endhighlight %}

What is BLAS?
-------------

[BLAS](http://en.wikipedia.org/wiki/BLAS) stands for Basic Linear Algebra Subroutines. It is a library of Fortran functions for dense linear algebra first published in 1979. 

The most famous BLAS routine is [DGEMM](http://www.netlib.org/blas/dgemm.f) a routine for **D**ouble precision **GE**nerally structured **M**atrix **M**ultiplication. `DGEMM` is very well implemented. `DGEMM` traditionally handles blocking for fewer cache misses, autotuning for each individual architecture, and even assembly level code optimization. You should never code up your own matrix multiply, you should always use `DGEMM`. Unfortunately, you may not know Fortran, and, even if you did, you might find the function header to be daunting.

    SUBROUTINE DGEMM(TRANSA,TRANSB,M,N,K,ALPHA,A,LDA,B,LDB,BETA,C,LDC)

Even if you're capable of working at this low-level most scientific users are not. `DGEMM` is fast but inaccessible. To solve this problem we usually build layers on top of `BLAS`. For example `numpy.dot` calls `DGEMM` if the BLAS library is available on your system.

Why not just use NumPy?
-----------------------

If you're reading this then you're probably comfortable with NumPy and you're very happy that it gives you access to highly optimized low-level code like `DGEMM`. What else could we desire? NumPy has two flaws

1.  Each operation occurs at the Python level. This causes sub-optimal operation ordering and lots of unnecessary copies. For example the following code is executed as follows
    {% highlight python %}
D = A*B*C # store A*B  -> _1
    D = _1*C  # store _1*C -> _2
    D = _2    # store _2   ->  D
    {% endhighlight %}
    It might have been cleaner to multiply `A*B*C` as `(A*B)*C` or `A*(B*C)` depending on the shapes of the matrices. Additionally the temporary matrices `_1`, and `_2` did not need to be created. If we're allowed to *reason about the computation* before execution then we can make some substantial optimizaitons. 

2.  BLAS contains many special functions for special cases. For example you can use `DSYMM` when one of your matrices is **SY**metric or `DTRMM` when one of your matrices is **TR**iangular. These allow for faster execution time if we are able to reason about our matrices. 

Previous Work
-------------

In the cases above we argue that we can make substantial gains if we are allowed to reason about the computation before it is executed. This is the job of a compiler. Computation usually happens as follows: 

1.  Write down code
2.  Reason about and transform code
3.  Execute code

Step (2) is often removed in scripting languages for programmer simplicity. There has been a lot of activity recently in putting it back in for array computations. The following projects compile array expressions prior to execution

1.  NumExpr
2.  Theano
3.  Numba
4.  ... I'm undoubtedly forgetting many excellent projects. Here is [a more complete list](https://github.com/Theano/Theano/wiki/Lazy-Matrix-Algebra-Ecosystem)

Where does SymPy fit in?
------------------------

The projects above are all numerical in nature. They are generally good at solving problems of the first kind (operation ordering, inplace operations, ...) but none of them think very clearly about the *mathematical* properties of the matrices. This is where SymPy can be useful. Using the assumptions logical programming framework SymPy is able to reason about the properties of matrix expressions. Consider the following situation

We know that `A` is symmetric and positive definite. We know that `B` is orthogonal. 

Question: is `BAB'` symmetric and positive definite?

Lets see how we can pose this question in SymPy.

{% highlight python %}

    >>> A = MatrixSymbol('A', n, n)
    >>> B = MatrixSymbol('B', n, n)
    >>> context = Q.symmetric(A) & Q.positive_definite(A) & Q.orthogonal(B)
    >>> ask(Q.symmetric(B*A*B.T) & Q.positive_definite(B*A*B.T), context)
    True

{% endhighlight %}

Positive-Definiteness is a very important property of matrix expressions. It strongly influences our choice of numerical algorithm. For example the fast [Cholesky algorithm](http://en.wikipedia.org/wiki/Cholesky) for LU decomposition may only be used if a matrix is symmetric and positive definite. Expert numerical analysts know this but most scientific programmers do not. NumPy does not know this but SymPy does.

Describing BLAS
-----------------

We describe a new matrix operation in SymPy with code like the following:

{% highlight python %}
    S = MatrixSymbol('S', n, n)
    class LU(BLAS):
        """ LU Decomposition """
        _inputs   = (S,)
        _outputs  = (Lof(S), Uof(S))
        view_map  = {0: 0, 1: 0} # Both outputs are stored in first input
        condition = True         # Always valid

    class Cholesky(LU):
        """ Cholesky LU Decomposition """
        condition = Q.symmetric(S) & Q.positive_definite(S)
{% endhighlight %}

This description allows us to consisely describe the expert knowledge used by numerical analysts. It allows us to describe the mathematical properties of linear algebraic operations.

Matrix Computation Graphs
-------------------------

We usually write code in a linear top-down text file. This representation does not allow the full generality of a program. Instead we need to use a graph.

A computation can be described as a directed acyclic graph (DAG) where each node in the graph is an atomic computation (a function call like `DGEMM` or `Cholesky`) and each directed edge represents a data dependency between function calls (an edge from `DGEMM` to `Cholesky` implies that the `Cholesky` requires an output of the `DGEMM` call in order to run). This graph may not contain cycles - they would imply that some set of jobs all depend on each other; they could never start.

Graphs must be eventually linearized and turned into code. Before that happens we can think about optimal ordering and, if we feel adventurous, parallel scheduling onto different machines. 

SymPy contains a very simple Computation graph object. Here we localize all of the logic about inplace operations, ordering, and (eventually) parallel scheduling.

Translating Matrix Expressions into Matrix Computations
-------------------------------------------------------

So how can we transform a matrix expression like 
    
{% highlight python %}
    (alpha*A*B).I * x
{% endhighlight %}

And a set of predicates like 

{% highlight python %}
    Q.lower_triangular(A) & Q.lower_triangular(B) & Q.invertible(A*B)
{% endhighlight %}

Into a graph of `BLAS` calls like one of the following?

{% highlight python %}
    DGEMM(alpha, A, B, 0, B) -> DTRSV(alpha*A*B, x)
    DTRMM(alpha, A, B)       -> DTRSV(alpha*A*B, x)
{% endhighlight %}

And, once we have this set of valid computations how do we choose the right one? This is the question that this project faces right now. These are both challenging problems.

References
----------

*   [BLAS](http://www.netlib.org/blas/) and [LAPACK](http://www.netlib.org/lapack/)
*   J. Bergstra, O. Breuleux, F. Bastien, P. Lamblin, R. Pascanu, G. Desjardins, J. Turian, D. Warde-Farley and Y. Bengio. [*Theano: A CPU and GPU Math Expression Compiler*](http://www.iro.umontreal.ca/~lisa/pointeurs/theano_scipy2010.pdf). Proceedings of the Python for Scientific Computing Conference (SciPy) 2010. June 30 - July 3, Austin, TX]
*   [Numba at Continuum](http://www.continuum.io/)
*   [NumExpr](http://code.google.com/p/numexpr/)
*   [A list of matrix projects in Python](https://github.com/Theano/Theano/wiki/Lazy-Matrix-Algebra-Ecosystem)
*   [M. Rocklin, *Partial Ordering in Theano*](http://matthewrocklin.com/pub/ordering/partial-orders.pdf)
