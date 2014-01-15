---
layout: post
title: Python v. Clojure v. Julia
tagline: a contest of text and grouping!
category : work
tags : [SciPy, Python, Programming]
---
{% include JB/setup %}

**tl;dr: We compare Python performance against Clojure, Julia, and Java in
text-processing and dynamic collections.  Remarkably, Python does well.**

## Situation

I mostly understand numeric performance; I am ignorant when it comes to text
and basic data wrangling.  Actually, that's an understatement

*The SciPy community has optimized the heck out of numerics; lets think about
text!*

I think that many of us are in the same position.  At work we analyze
non-numeric data and run-times now slow down my work cycle.  After benchmarking
and tuning code within Python I have the following three options to
further increase performance:

1.  Use more machines
2.  Invent a better algorithm
3.  Switch to a lower level language

Often we choose number 1, "use more machines".  We make this
choice because it's easy.  Option 2, "invent better algorithms" is hard and
so we avoid it if we're not intellectually interested in the problem.

In numeric work we often pursue option 3, "switch to a lower level language"
and with good reason.  The Python -> numpy -> fancy-numeric-package -> tuned
C/Fortran -> CUDA progression often comes along with somewhat predictable
order-of-magnitude gains at each step.  We know we can improve computation and
we know roughly by how much.

In text-based work I lack the same strong intuition on performance that I have
in numeric work.  I don't know how valuable lower level languages really are.
This blogpost helps to answer that question.


## A Small Language Shootout

Can my 30-core shared memory machine or large distributed system be replaced
with a few cores running tight compiled code?  To test this we run a very
simple parse-and-group operation in three languages of current interest:

*   Python -- our favorite low-performance language
*   Clojure -- A compiled lisp on the JVM with a vibrant community
*   Julia -- The language all of Scientific Python is talking about but no one
    seems to have used.

Each is a modern high-productivity language optimized for development time as
well as performance.  I would feel comfortable marrying myself to any of them
long-term.

Later on in the blogpost I introduce Java as a baseline language:

*   Java -- the oddly effective language that everyone loves to hate


## Installing Julia

Julia is a compiled language that targets

*   imperative array code (like C/Fortran)
*   with a lightweight syntax (like Python)
*   but with a real type system (like Haskell).

Along with Rust and Go it is one of the recent advances in imperative
languages.  It caters more to the Matlab/Fortran crowd than the Systems/C crowd
(like Go).

While curious about Julia I've never played with it.  I had been warned about
Julia's installation process.  I was told that it depended on a custom LLVM and
took up a Gig+ of storage.  I was pleasantly surprised when the following
worked (Ubuntu 13.04)

    mrocklin@notebook:~$ sudo add-apt-repository ppa:staticfloat/juliareleases
    mrocklin@notebook:~$ sudo apt-get update
    mrocklin@notebook:~$ sudo apt-get install julia
        ...
        Need to get 12.8 MB of archives.
        After this operation, 37.5 MB of additional disk space will be used.
        ...
    mrocklin@notebook:~$ julia
                   _
       _       _ _(_)_     |  A fresh approach to technical computing
      (_)     | (_) (_)    |  Documentation: http://docs.julialang.org
       _ _   _| |_  __ _   |  Type "help()" to list help topics
      | | | | | | |/ _` |  |
      | | |_| | | | (_| |  |  Version 0.2.0 (2013-11-16 23:48 UTC)
     _/ |\__'_|_|_|\__'_|  |  Official http://julialang.org release
    |__/                   |  x86_64-linux-gnu

    julia> 1 + 2
    3

Well that was simple!  There is no longer an excuse not to try Julia.


## Problem

I want to test

*   File I/O
*   Basic string operations
*   Grouping operations (mostly dictionary lookups and collection appends).

To do this we take all of the word-pairs in "Tale of Two Cities"
and group them by the first word.

Given data that looks like the the following:

    $ cat data.txt
    a,b
    a,c
    a,d
    b,a
    b,d
    d,c
    d,a

We produce data that looks like the following:

    {'a': ['b', 'c', 'd'],
     'b': ['a', 'd'],
     'd': ['c', 'a']}

But instead of `a, b, c` we use words from a long book, *The Tale of Two
Cities*

    it, was
    was, the
    the, best
    best, of
    of, times
    times, it
    it, was
    was, the
    the, worst
    worst, of
    of, times
    ...

We read in a file, split each line by commas, and then perform a groupby
operation.  Comma spliting and grouping are both commonly used operations.
For example these steps might be used to create a Markov chain to power
word prediction in your smartphone keyboard.


## Solutions

Note that these are all done using the pure language.  Both Python and Julia
have a DataFrame project (like `pandas`) with heavily optimized
`groupby` operations.  Today we stick with the core language.

### Python

We use `toolz` for the `groupby` operation

{% gist 8365524 %}

    python benchmark.py word-pairs.txt

### Julia

We first make a `groupby` operation in Julia.

{% gist 8365495 %}

Afterwards out code closely matches the Python Solution

{% gist 8365510 %}

    julia benchmark.jl word-pairs.txt

### Clojure

The Clojure standard library has everything we need

{% gist 8365551 %}

    lein uberjar
    java -jar location-of-standalone.jar word-pairs.txt


## Numeric Results

The results surprised me.

    Python:     200 ms
    Julia:      200 to 800 ms  # I don't know what's going on here
    Clojure:    550 ms

I expected Python to be dead last.  Instead it comfortably hums along in first.
It also has the shortest latency (both Julia and Clojure have painful compile
times (not included in totals)).

Perhaps this is because neither the Clojure nor Julia solutions have sufficient
type information.  If any Clojurians or Julians (is that what we call you?) are
around I welcome better solutions.

In particular, I was sad to learn that Julia's `readlines` function is of type
`file -> Array{Any}` rather than `file -> Array{String}`.  This propagates down
to `word_pairs` being of type `Array{Array{Any}}` which I suspect stops
many meaningful optimizations.


## Thoughts on the Code

### Timing Macros

Writing code to time other code is tricky.  It always requires some sort of
super-code.  In Clojure and Julia this is the `time` macro

    ;; Clojure
    (time (... ))

    # Julia
    @time begin
        ...
    end

In Python I used the `duration` context manager.  Context managers commonly
serve well where macros are desired.

    with duration():
        ...

But normally people use IPython's `timeit` magic (also macro-like).  I used
`duration` here because it was pure Python and because it doesn't benefit from
the caching of repeated iterations.


### Lambdas

I miss nice lambda syntax.  Both Clojure and Julia have concise
multi-line anonymous functions.  Julia even has pretty ones:

    Python  : lambda x: x + 1
    Clojure : #(+ 1 %)
    Julia   : x -> x + 1

As much as I love Clojure I have to say, that's an ugly `lambda`.  It looks
like a child mashing the top row of the keyboard.

### No Obligatory Types

There is no necessary explicit type information in any of the languages.  This
seems to be a common trait among high productivity languages.


### Performance from Optional Types?

Clojure and Julia both support adding optional type information to increase
performance.  Python3 supports static type annotations but doesn't use them
meaningfully.  I suspect that one can get more performance on both the Clojure and Julia
solutions by adding type information.  If any experts are out there on
supplying type hints I'd be grateful for the suggestions.


## Lets Consider Java

To see how much runtimes could improve we test Java, a language without
fanciness, where all types are explicit, and whose compiler optimizations we
mostly understand.

The results?

    Python:     200 ms
    Julia:      200 to 800 ms  # I don't know what's going on here
    Clojure:    550 ms

    Java:       190 ms

Surprisingly, Java is not significantly faster.  This provides us with a pretty
stable lower bound for this problem.  We're unlikely to get much faster with
standard data structures.

As a corollary this probably answers the question:

*"Can more type information accelerate the Clojure/Julia solutions to this
problem?"*

with the answer:

*"No"*.


### Code

The Java standard library has the data structures we need but fancy operations
like `groupby` are absent and difficult to create.

{% gist 8387373 %}

    javac Benchmark.java
    java Benchmark word-pairs.txt

## Conclusion

It turns out that runtimes for this problem are dominated by data structures for
which Python is well optimized.  But how common in this computational focus
among text-analytics problems?  If anyone has insight here I'd love to hear
about it.  Remember that my goal is to generate intuition about computational
performance in text-analytic operations.

I used to feel guilty about using Python for data processing.  But this test
gives me confidence in the performance of Python data structures relative to
other languages and makes me more optimistic about Python's role in data
analytics in general.


## Appendix

My Python `duration` context manager.  This is more a lesson on the value and
simplicity of context managers than anything else:

{% gist 8365436 %}


Also, if you want the data then you should run this script:

{% gist 8365482 %}

It depends on `toolz` which you can get from PyPI with

    pip install toolz

or

    easy_install toolz
