---
layout: post
title: Craft Minimal Bug Reports
category: work
tags: [Programming, scipy, Python]
theme: twitter
---
{% include JB/setup %}

Following up on a post on [supporting users in open source](../../../2016/08/25/supporting-users)
this post lists some suggestions on how to ask a package maintainer to help you with a problem.

You don't have to follow these suggestions.  They are optional.
They make it more likely that a project maintainer to spend time helping you.
It's important to remember that their willingness to support you for free is optional too.


Minimal Complete Verifiable Examples
------------------------------------

I strongly recommend following Stack Overflow's guidelines on [Minimal Complete Verifiable Exmamples](https://stackoverflow.com/help/mcve).  I'll include brief highlights here:

... code should be ...

-  Minimal – Use as little code as possible that still produces the same problem
-  Complete – Provide all parts needed to reproduce the problem
-  Verifiable – Test the code you're about to provide to make sure it reproduces the problem

Lets be clear, this is *hard* and takes time.
I find that creating an MCVE often takes 10-30 minutes.
Fortunately this work is usually straightforward,
even if I don't know very much about the package I'm having trouble with.
Most of creating an MCVE is about removing all of the code that was specific to my application.

When answering questions I often point people to this document.
They sometimes come back with a better-but-no-yet-minimal example.
This post clarifies a few common issues.

As an running example I'm going to use Pandas dataframe problems.

Don't post data
---------------

You shouldn't post the file that you're working with.
Instead, try to see if you can reproduce the problem with just a few lines of data rather than the whole thing.

Having to download a file, unzip it, etc. make it much less likely that someone will actually run your example in their free time.

### Don't

I've uploaded my data to Dropbox and you can get it here: [my-data.csv.gz]()

```python
import pandas as pd
df = pd.read_csv('my-data.csv.gz')
```


### Do

You should be able to copy-paste the following to get enough of my data to cause the problem:

```python
import pandas as pd
df = pd.DataFrame({'account-start': ['2017-02-03', '2017-03-03', '2017-01-01'],
                   'client': ['Alice Anders', 'Bob Baker', 'Charlie Chaplin'],
                   'balance': [-1432.32, 10.43, 30000.00],
                   'db-id': [1234, 2424, 251],
                   'proxy-id': [525, 1525, 2542],
                   'rank': [52, 525, 32],
                   ...
                   })
```




Actually don't include your data at all
---------------------------------------

Actually, your data probably has lots of information that is very specific to
your application.  Your eyes gloss over it but a maintainer doesn't know what
is relevant and what isn't, so it will take them time to digest it if you
include it.  Instead see if you can reproduce your same failure with artificial
or random data.

### Don't

Here is enough of my data to reproduce the problem

```python
import pandas as pd
df = pd.DataFrame({'account-start': ['2017-02-03', '2017-03-03', '2017-01-01'],
                   'client': ['Alice Anders', 'Bob Baker', 'Charlie Chaplin'],
                   'balance': [-1432.32, 10.43, 30000.00],
                   'db-id': [1234, 2424, 251],
                   'proxy-id': [525, 1525, 2542],
                   'rank': [52, 525, 32],
                   ...
                   })
```

### Do

My actual problem is about finding the best ranked employee over a certain time period,
but we can reproduce the problem with this simpler dataset.
Notice that the dates are *out of order* in this data (2000-01-02 comes after 2000-01-03).
I found that this was critical to reproducing the error.

```python
import pandas as pd
df = pd.DataFrame({'datetime': ['2000-01-01', '2000-01-03', '2000-01-02'],
                   'id': [1, 2, 3],
                   'name': ['Alice', 'Bob', 'Charlie'})
```


See how small you can make things
---------------------------------

To make it even easier, see how small you can make your data.
For example if working with tabular data (like Pandas),
then how many columns do you actually need to reproduce the failure?
How many rows do you actually need to reproduce the failure?
Do the columns need to be named as you have them now or could they be just "A" and "B"


### Do


```python
import pandas as pd
df = pd.DataFrame({'datetime': ['2000-01-03', '2000-01-02'],
                   'id': [1, 2]})
```


Remove unnecessary steps
------------------------

Is every line in your example absolutely necessary to reproduce the error?
If you're able to delete a line of code then please do.
Because you already understand your problem you are *much more efficient* at doing this than the maintainer is.
They probably know more about the tool, but you know more about your code.

### Don't

The groupby step below is raising a warning that I don't understand

```python
df = pd.DataFrame(...)

df = df[df.value > 0]
df = df.fillna(0)

df.groupby(df.x).y.mean()  # <-- this produces the error
```

### Do

The groupby step below is raising a warning that I don't understand

```python
df = pd.DataFrame(...)

df.groupby(df.x).y.mean()  # <-- this produces the error
```

Think of it like a game.
How many lines can you remove while still getting the same error to occur?


Use Syntax Highlighting
-----------------------

When using Github you can enclose code blocks in triple-backticks (the
character on the top-left of your keyboard on US-standard QWERTY keyboards).
It looks like this:

    ```python
    x = 1
    ```


Provide complete tracebacks
---------------------------

You know all of that stuff between your code and the exception that is hard to
make sense of?  You should include it.

### Don't

    I get a ZeroDivisionError from the following code:

    ```python
    def div(x, y):
        return x / y

    div(1, 0)
    ```


### Do

    I get a ZeroDivisionError from the following code:

    ```python
    def div(x, y):
        return x / y

    div(1, 0)
    ```

    ```python
    ZeroDivisionError                         Traceback (most recent call last)
    <ipython-input-4-7b96263abbfa> in <module>()
    ----> 1 div(1, 0)

    <ipython-input-3-7685f97b4ce5> in div(x, y)
          1 def div(x, y):
    ----> 2     return x / y
          3

    ZeroDivisionError: division by zero
    ```

If the traceback is long that's ok.  If you really want to be clean you can put
it in `<details>`  brackets.

    I get a ZeroDivisionError from the following code:

    ```python
    def div(x, y):
        return x / y

    div(1, 0)
    ```

    ### Traceback

    <details>

    ```python
    ZeroDivisionError                         Traceback (most recent call last)
    <ipython-input-4-7b96263abbfa> in <module>()
    ----> 1 div(1, 0)

    <ipython-input-3-7685f97b4ce5> in div(x, y)
          1 def div(x, y):
    ----> 2     return x / y
          3

    ZeroDivisionError: division by zero
    ```

    </details>
