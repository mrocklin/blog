---
layout: post
title: Credit Modeling with Dask
category: work
tags: [Programming, Python]
theme: twitter
author: Richard Postelnik
---
{% include JB/setup %}

This post explores an actual use case for dask and how we used it to create a new calculation engine for credit models in python. Special thanks to Matt Rocklin, Michael Grant, and Gus Cavanagh for their feedback as well as thanks to Matt for the guest spot on his blog.

## The Problem

When applying for a loan, like a credit card, mortgage, auto loan, etc., we want to estimate the likelihood of default and the profit (or loss) to be gained. Those models are composed of a complex set of equations that depend on each other. There can be hundreds of equations each of which could have up to 20 inputs and yield 20 outputs. That is a lot of information to keep track of and we want to avoid manually keeping track of the dependencies. We want to avoid this:

```python
def final_equation(inputs):
    out1 = equation1(inputs)
    out2_1, out2_2 = equation2(inputs, out1)
    ...
    out_final = equation_n(inputs, out,...)
    return out_final
```

This boils down to a dependency and ordering problem known as task scheduling.

## DAGs to the rescue 
<img src="{{BASE_PATH}}/images/credit_models/snatch.jpg" alt="snatch joke">

A [directed acyclic graph](https://en.wikipedia.org/wiki/Directed_acyclic_graph) (DAG) is commonly used to solve task scheduling problems. Dask is a library for delayed task computation that makes use of directed graphs at it's core. [dask.delayed](http://dask.pydata.org/en/latest/delayed.html) is a simple decorator that turns a python function into a graph vertex. If I pass the output from one delayed function as a parameter to another delayed function, dask creates a directed edge between them. Let's look at an example:

```python
def add(x, y):
    return x + y

add(2, 2)
>>> 4
```
So here we have a function to add two numbers together. Let's see what happens when we wrap it with `dask.delayed`:

```python
add = dask.delayed(add)
left = add(1, 1)
left
>>> Delayed('add-f6204fac-b067-40aa-9d6a-639fc719c3ce')
```

`add` now returns a `Delayed` object. We can pass this as an argument back into our `dask.delayed` function to start building out a chain of computation.

```python
right = add(1, 1)
four = add(left, right)
four.compute()
>>> 4
four.visualize()
```

Below we can see how the DAG starts to come together.

<img src="{{BASE_PATH}}/images/credit_models/four.png" alt="four graph">

## Mock credit example

Let's assume I'm a mortgage bank and have 10 people applying for a mortgage. I want to estimate the group's average likelihood to default based on years of credit history and income. 

```python
hist_yrs = range(10)
incomes = range(10)
```

Let's also assume that productivity is a function of the incremented years history and half the years experience. While this could be written like:

```python
def default(hist, income):
    return (hist + 1) ** 2 + (income / 2)
```

I know in the future that I will need the incremented history for another calculation and want to be able to reuse the code as well as avoid doing the computation twice. Instead, I can break those functions out:

```python
from dask import delayed

@delayed
def increment(x):
    return x + 1

@delayed
def halve(y):
    return y / 2

@delayed
def default(hist, income):
    return hist**2 + income
```

Note, how I wrapped the functions with `delayed`. Now instead of returning a number these functions will return a `Delayed` object. Even better is that these functions can also take `Delayed` objects as inputs. It is this passing of `Delayed` objects as inputs to other `delayed` functions that allows dask to construct the task graph. I can now call these functions on my data:

```python
inc_hist = [increment(n) for n in hist_yrs]
halved_income = [halve(n) for n in income]
estimated_default = [default(hist, income) for hist, income in zip(inc_hist, halved_income)]
```
If you look at these variables, you will see that nothing has actually been calculated yet. They are all lists of `Delayed` objects.

Now, to get the average, I could just take the sum of `estimated_default` but I want this to scale (and make a more interesting graph) so let's do a merge-style reduction.

```python
@delayed
def agg(x, y):
    return x + y

def merge(seq):
    if len(seq) < 2:
        return seq
    middle = len(seq)//2
    left = merge(seq[:middle])
    right = merge(seq[middle:])
    if not right:
        return left
    return [agg(left[0], right[0])]

default_sum = merge(estimated_defaults)
```

At this point `default_sum` is a list of length 1 and that first element is the sum of estimated default for all applicants. To get the average, we divide by the number of applicants and call compute:

```python
avg_default = default_sum[0] / 10
avg_default.compute()  # 40.75
```

To see the computation graph that dask will use, we call `visualize`:

```python
avg_default.visualize()
```

<img src="{{BASE_PATH}}/images/credit_models/dummy_graph.png" alt="default graph">

And that is how dask can be used to construct a complex system of equations with reusable intermediary calculations.

## How we used dask

For our credit modeling problem, we used dask to make a custom data structure to represent the individual equations. Using the default example above, this looked something like:

```python
class Default(Equation):
    inputs = ['inc_hist', 'halved_income']
    outputs = ['defaults']
    
    @delayed
    def equation(self, inc_hist, halved_income, **kwargs):
        return inc_hist**2 + halved_income
```

This allows us to write each equation as it's own isolated function and mark it's inputs and outputs. With this set of equation objects, we can determine the order of computation (with a [topological sort](https://en.wikipedia.org/wiki/Topological_sorting)) and let dask handle the graph generation and computation. This eliminates the onerous task of manually passing around the arguments in the code base. Below is an example task graph for one particular model that the bank actually does.

<img src="{{BASE_PATH}}/images/credit_models/graph.svg" alt="calc task graph">

Thanks to [Gephi](https://gephi.org), I am able to process the large dot file outputted from `my_task.visualize()` and make the pretty colored graph above. The chaotic upper region of this graph is the individual equation calculations. Zooming in we can see the entry point, our input pandas DataFrame, as the large orange circle at the top and how it gets fed into the equations.

<img src="{{BASE_PATH}}/images/credit_models/graph_model.svg" alt="zoomed model section">

The output of the model is about 100 times the size of the input so we do some aggregation at the end via tree reduction. This accounts for the more structured bottom half of the graph. The large green node at the bottom is our final output.

<img src="{{BASE_PATH}}/images/credit_models/graph_agg.svg" alt="zoomed agg section">

## Final Thoughts

With our dask-based data structure, we spend more of our time writing model code rather than maintenance of the engine itself. Dask also offers a number of advantages not covered above. For example, with dask you also get access to [diagnostics](https://distributed.readthedocs.io/en/latest/web.html) such as time spent running each task and resources used. Also, you can easily distribute your computation with [dask distributed](https://distributed.readthedocs.io/en/latest/) with relative ease. Now if I want to run our model across out-of-core distributed data, we don't have to worry about extending our code to incorporate something like Spark. Finally, dask allows you to give pandas-capable business analysts or less technical folks access to large datasets with the [dask dataframe](http://dask.pydata.org/en/latest/dataframe.html).

## Full Example

```python
from dask import delayed


@delayed
def increment(x):
    return x + 1
    
    
@delayed
def halve(y):
    return y / 2


@delayed
def default(hist, income):
    return hist**2 + income
    

@delayed
def agg(x, y):
    return x + y


def merge(seq):
    if len(seq) < 2:
        return seq
    middle = len(seq)//2
    left = merge(seq[:middle])
    right = merge(seq[middle:])
    if not right:
        return left
    return [agg(left[0], right[0])]


hist_yrs = range(10)
incomes = range(10)
inc_hist = [increment(n) for n in hist_yrs]
halved_income = [halve(n) for n in incomes]
estimated_defaults = [default(hist, income) for hist, income in zip(inc_hist, halved_income)]
default_sum = merge(estimated_defaults)
avg_default = default_sum[0] / 10
avg_default.compute()
avg_default.visualize()  # requires graphviz and python-graphviz to be installed
```
