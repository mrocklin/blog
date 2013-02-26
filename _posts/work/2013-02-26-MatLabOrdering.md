---
layout: post
title:  Operation Ordering in MatLab
tagline:  why you should demand an array compiler 
category : work 
tags : [Matrices]
---
{% include JB/setup %}

Consider the following MatLab code

    >> x = ones(10000, 1);
    >> tic; (x*x')*x; toc
    Elapsed time is 0.337711 seconds.
    >> tic; x*(x'*x); toc
    Elapsed time is 0.000956 seconds.

Depending on where you place the parentheses you either create `x*x'`, a large 10000 by 10000 rank 1 matrix, or `x'*x`, a 1 by 1 rank 1 matrix.  Either way the result is the same.  The difference in runtimes however spans several orders of magnitude.

Graphically the operation looks something like the following

<img src="{{ BASE_PATH }}/images/xxtrans.png" width="50%" align="right">

This is a common lesson that the order of matrix operations matters.  Do computers know this lesson?  I don't expect a compiler for C or Fortran to make this optimization.  They would have to inspect sets of nested for loops to realize what is happening.  I also don't expect `numpy` to make this optimization; operation ordering is determined by the Python host language.  With MatLab I wasn't sure.  They're interpreted and so generally don't compile, but they could easily look at the expression within each line before execution.  Given that the `Mat` was in the name of the language, I was hopeful.

Does Matlab choose wisely?
    
    >> tic; x*x'*x; toc
    Elapsed time is 0.317499 seconds.

no.
