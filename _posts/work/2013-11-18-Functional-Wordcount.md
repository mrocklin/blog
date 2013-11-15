---
layout: post
title:  Wordcounting with PyToolz
tagline:  a discussion of functional vocabulary
category : work
draft: true
tags : [Python, scipy]
---
{% include JB/setup %}

In a
[blogpost](http://matthewrocklin.com/blog/work/2013/10/17/Introducing-PyToolz/)
last month I announced [PyToolz](http://toolz.readthedocs.org/) a Python
implementation of the functional standard library.  Today I want to discuss the
wordcounting example in more depth, highlighting differences between
simple/verbose and complex/concise code.


### Verbose solution with simple terms

My standard wordcount function looks like the following

{% highlight python %}
def stem(word):
    """ Stem word to primitive form

    >>> stem("Hello!")
    'hello'
    """
    return word.lower().rstrip(",.!)-*_?:;$'-\"").lstrip("-*'\"(_$'")


def wordcount(string):
    words = string.split()

    stemmed_words = []
    for word in words:
        stemmed_words.append(stem(word))

    counts = dict()
    for word in stemmed_words:
        if word not in counts:
            counts[word] = 1
        else:
            counts[word] += 1

    return counts

>>> sentence = "This cat jumped over this other cat!"
>>> wordcount(sentence)
{'cat': 2, 'jumped': 1, 'other': 1, 'over': 1, 'this': 2}
{% endhighlight %}

While long/verbose, this solution is straightforward and comprehensible to all
moderately experienced Python programmers.


### Concise solution with complex terms

Using the definition for `stem` above and the `frequencies` function from
`toolz` we can condense `wordcount` into the following line.

{% highlight python %}
>>> from toolz import frequencies

>>> frequencies(map(stem, sentence.split()))
{'cat': 2, 'jumped': 1, 'other': 1, 'over': 1, 'this': 2}
{% endhighlight %}

While dense, this solution solves the problem concisely using
pre-existing functionality.


### Increasing readability with `pipe`

The functional solution above with `frequencies(map(stem, sentence.split()))` is
concise but difficult for many human readers to parse.  The reader needs to
traverse a tree of parentheses to find the innermost element (`sentence`) and
then work outwards to discover the flow of computation.  The readability of
this solution can be markedly improved by introducing the `pipe` function to
apply a sequence of functions onto data.

To introduce `pipe` consider the process of doing laundry:

{% highlight python %}
>>> # Do Laundry
>>> wet_clothes = wash(clothes)
>>> dry_clothes = dry(wet_clothes)
>>> result = fold(dry_clothes)
{% endhighlight %}

This pushes the data, `clothes` through a pipeline of functions, `wash`, `dry`,
and `fold`.  This pushing of data through a pipeline of functions is a common
pattern.  Using `pipe` we push the clothes through three transformations in sequence:

{% highlight python %}
>>> result = pipe(clothes, wash, dry, fold)
{% endhighlight %}

Pipe pushes data (first argument) through a sequence of functions (rest of the
arguments) from left to right.  Here is another example.

{% highlight python %}
from toolz import pipe

# Simple example
def double(x):
    return 2 * x

>>> pipe(3, double, double, str)
'12'
{% endhighlight %}

Using `pipe` we can rearrange our functional wordcounting solution to the
following form

{% highlight python %}
>>> from toolz.curried import map

>>> pipe(sentence, str.split, map(stem), frequencies)
{'cat': 2, 'jumped': 1, 'other': 1, 'over': 1, 'this': 2}
{% endhighlight %}

To me this code reads very clearly from left to right.  We take a sentence,
split it, stem each word, and then count frequencies.  This is sufficiently
simple so that I am confident in the result after a brief review of the code.


### Discussion

The first solution uses lots of simple words.  The second solution uses a few
complex words.  Just as in natural language there are benefits and
drawbacks to both approaches.  The choice of suitable vocabulary largely
depends on your audience.

Long solutions of simple words are universally understandable but require
reader effort to construct meaning.  Most Python programmers can understand the
first solution without additional training but will need to expend effort to
deduce its meaning.

Concise solutions of complex words are not universally understandable but
do convey meaning more quickly if the terms are already known by the reader.
Additionally if the terms themselves are well tested then these solutions are
less prone to error.

A good vocabulary can concisely express most relevant problems with a small
number of terms.  The functional standard library (e.g. `map`, `groupby`,
`frequencies`, ...) is such a set.  It has been developed and honed over
decades of language development.  Understanding a relatively few number of
terms (around 10-20) enables the concise expression of most common programming
tasks.
