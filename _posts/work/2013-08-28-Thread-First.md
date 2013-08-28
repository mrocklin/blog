---
layout: post
title:  Thread First Pattern
tagline: 
category : work 
tags : [Functional, Python]
---
{% include JB/setup %}

My physics colleague is learning Python and asked me for a simple way to parse
the following file header

    CPMD CUBE FILE.
    OUTER LOOP: X, MIDDLE LOOP: Y, INNER LOOP: Z
       3    0.000000    0.000000    0.000000
      40    0.283459    0.000000    0.000000
      40    0.000000    0.283459    0.000000
      40    0.000000    0.000000    0.283459
       8    0.000000    5.570575    5.669178    5.593517
       1    0.000000    5.562867    5.669178    7.428055
       1    0.000000    7.340606    5.669178    5.111259
    -0.25568E-04  0.59213E-05  0.81068E-05  0.10868E-04  0.11313E-04  0.35999E-05
         :             :             :           :            :            :
         :             :             :           :            :            :
         :             :             :           :            :            :
           In this case there will be 40 x 40 x 40 floating point values
         :             :             :           :            :            :
         :             :             :           :            :            :
         :             :             :           :            :            :

Normally for tabular data I would just point him towards `numpy.loadtxt` or the `csv` module.  This particular dataset is a tad annoying though, look closely for the following complications

1.  There are three separate numerical tables
    *   Lines 2-5 are three lines with four columns
    *   Lines 6-9 are three lines with five columns
    *   Lines 11 onward is a traditional table with many float columns
2.  The first column to the first two sections contains integers instead of floating point numbers

Neither the `csv` module nor the `numpy.loadtxt/genfromtext` functions are capable of wrapping this complexity.  This is commonplace, we often have data that doesn't quite fit our module's expectations.  At this point we often fall back to traditional programming.  

My colleague's solution was a sequence of for loops, appending data onto a set of lists.



{% highlight python %}
with open(filename) as f:
    lines = f.readlines()

# First table
int_column = []
float_columns = []
for line in lines[2:5]:
    tokens = line.split()
    int_columns.append(int(tokens[0]))
    float_columns.append([float(tok) for tok in tokens[1:]])

# Second table
....
{% endhighlight %}

This solution is standard but, in my colleague's words, not particularity "cute".  He wanted to know if there was a "cute" language idiom to handle tasks like these.  I've been programming in a functional style for a while now and decided to see if that paradigm could offer a better option.  After some back and forth with him I stabilized on the following solution.


{% highlight python %}
from functoolz import thread_first
from itertools import islice
import StringIO
import numpy

# First table
int_column, float_columns = \
    thread_first(filename,
                 open,
                 (islice, 2, 5),
                 ''.join,
                 StringIO.StringIO,
                 numpy.genfromtxt,
                 lambda X: (X[:,0].astype(int), X[:, 1:])))
# Second table
....
{% endhighlight %}

This solution is very different from my colleague's.  Rather than provide explicit instructions on how to manipulate the data at a low-level (for loop with list appends) it describes a sequence of high-level transformations.  The `thread_first` function takes the first argument (the data) and runs it through the following functions sequentially.  I'll describe those functions below:

<hr>

| Transformation                                      | Explanation                                         |
|:----------------------------------------------------|:----------------------------------------------------|
| `filename`                                          | Our original input, a filename like 'file.txt'      |
| `open`                                              | Open the file for reading                           |
| `(islice, 2, 5)`                                    | Take lines 2:5                                      |
| `''.join`                                           | Join them together into a single string             |
| `StringIO.StringIO`                                 | Turn that string into a file-like object            |
| `numpy.genfromtxt`                                  | Parse into an array                                 |
| `lambda X: (X[:,0].astype(int), X[:, 1:]))`         | Separate array into first and all other columns     |

<hr>

It is equivalent to the following lines:

{% highlight python %}
X = numpy.genfromtxt(''.join(StringIO.StringIO(islice(open('file.txt'), 2, 5))))
X[:,0].astype(int), X[:, 1:]
{% endhighlight %}


### Why this Solution is Worse

Here are my thoughts on why the functional solution is worse.  If you have other thoughts please list them in the comments:

1.  It's weird and the current base of programmers will be put off
2.  It uses functions that are not commonly known like `StringIO`, `islice`, and `numpy.genfromtxt`.  It demands a richer vocabulary.
3.  It is inefficient because it opens and reads the file for each section.  It does not optimally manage state.


### Why this Solution is Better

Here are my thoughts on why the functional solution is better.  Again, if you have other thoughts please do list them in the comments:

1.  The intent of the operation is more explicit.
2.  The component functions used are well tested.  There are fewer opportunities for bugs.  
3.  The information content of each term is high.  This solution reinvents the minimum amount of technology.


### Thoughts

Today I wouldn't use this solution in production code mainly because my usual colleagues aren't familiar with it.  However I do think that the ideas behind the solution do have substantial merit.  In particular

*   Function reuse:  Reinventing wheels is both wasteful to the programmer and harmful to the longevity the code.
*   Standard library - The use of standard library functions supports more rapid understanding of your code.
*   Composition - Mechanisms for function composition and encapsulation (like `thread_first`) promote rapid development of novel and robust solutions.

In general I think that while for loops and low-level code are globally accessible they also demand significant investment to understand their particular role in a certain application.  High-level/broad vocabulary solutions more directly present their intent but are limited to those programmers who understand them.  

### References

*   [`functoolz`](http://github.com/mrocklin/functoolz/): The functional solution uses `thread_first`, a function from the non-standard `functoolz` library. 
