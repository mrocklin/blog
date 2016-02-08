---
layout: post
title:  Operation Ordering in MatLab
tagline:  why you should demand an array compiler
category : work
theme: twitter
tags : [Matrices]
---
{% include JB/setup %}

Consider the following MatLab code

    >> x = ones(10000, 1);
    >> tic; (x*x')*x; toc
    Elapsed time is 0.337711 seconds.
    >> tic; x*(x'*x); toc
    Elapsed time is 0.000956 seconds.

Depending on where the parentheses are placed one either creates `x*x'`, a large 10000 by 10000 rank 1 matrix, or `x'*x`, a 1 by 1 rank 1 matrix.  Either way the result is the same.  The difference in runtimes however spans several orders of magnitude.

Graphically the operation looks something like the following

<img src="{{ BASE_PATH }}/images/xxtrans.png" width="50%" align="right">

This is a common lesson that the order of matrix operations matters.  Do computers know this lesson?  It is difficult to implement this optimization in compiler for C or Fortran.  They would have to inspect sets of nested for loopsto realize the larger picture.  A hosted library like `numpy` is also unlikely to make this optimization; operation ordering is determined by the Python language.  With MatLab it is uncertain.  MatLab is interpreted and so generally doesn't compile.  However it inspect each line statement before execution.

Does Matlab choose wisely?

    >> tic; x*x'*x; toc
    Elapsed time is 0.317499 seconds.

no.
