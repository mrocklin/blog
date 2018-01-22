---
layout: post
title: Streaming Python Prototype
category: work
tags: [Programming, Python, scipy]
theme: twitter
---
{% include JB/setup %}

*This work is supported by [Continuum Analytics](http://continuum.io), and the
Data Driven Discovery Initiative from the [Moore
Foundation](https://www.moore.org/).*

*This blogpost is about experimental software.  The project may change or be
abandoned without warning.  You should not depend on anything within this
blogpost.*

This week I built a [small streaming
library](https://github.com/mrocklin/streams) for Python.  This was originally
an exercise to help me understand streaming systems like Storm, Flink,
Spark-Streaming, and Beam, but the end result of this experiment is not
entirely useless, so I thought I'd share it.  This blogpost will talk about my
experience building such a system and what I valued when using it.  Hopefully
it elevates interest in streaming systems among the Python community.

Background with Iterators
-------------------------

Python has sequences and iterators.  We're used to mapping, filtering and
aggregating over lists and generators happily.

```python
seq = [1, 2, 3, 4, 5]
seq = map(inc, L)
seq = filter(iseven, L)

>>> sum(seq) # 2 + 4 + 6
12
```

If these iterators are infinite, for example if they are coming from some
infinite data feed like a hardware sensor or stock market signal then most of
these pieces still work except for the final aggregation, which we replace with
an accumulating aggregation.

```python
def get_data():
    i = 0
    while True:
        i += 1
        yield i

seq = get_data()
seq = map(inc, seq)
seq = filter(iseven, seq)
seq = accumulate(lambda total, x: total + x, seq)

>>> next(seq)  # 2
2
>>> next(seq)  # 2 + 4
6
>>> next(seq)  # 2 + 4 + 6
12
```

This is usually a fine way to handle infinite data streams.  However this
approach becomes awkward if you don't want to block on calling `next(seq)` and
have your program hang until new data comes in.   This approach also becomes
awkward when you want to branch off your sequence to multiple outputs and
consume from multiple inputs.  Additionally there are operations like rate
limiting, time windowing, etc. that occur frequently but are tricky to
implement if you are not comfortable using threads and queues.  These
complications often push people to a computation model that goes by the name
*streaming*.

To introduce streaming systems in this blogpost I'll use my new tiny library,
currently called [streams](https://github.com/mrocklin/streams) (better name to
come in the future).  However if you decide to use streaming systems in your
workplace then you should probably use some other more mature library instead.
Common recommendations include the following:

-  ReactiveX (RxPy)
-  Flink
-  Storm (Streamparse)
-  Beam
-  Spark Streaming


Streams
-------

We make a stream, which is an infinite sequence of data into which we can emit
values and from which we can subscribe to make new streams.

```python
from streams import Stream
source = Stream()
```

From here we replicate our example above.  This follows the standard
map/filter/reduce chaining API.

```python
s = (source.map(inc)
           .filter(iseven)
           .accumulate(lambda total, x: total + x))
```

Note that we haven't pushed any data into this stream yet, nor have we said
what should happen when data leaves.  So that we can look at results, lets make
a list and push data into it when data leaves the stream.


```python
results = []
s.sink(results.append)  # call the append method on every element leaving the stream
```

And now lets push some data in at the source and see it arrive at the sink:

```python
>>> for x in [1, 2, 3, 4, 5]:
...     source.emit(x)

>>> results
[2, 6, 12]
```

We've accomplished the same result as our infinite iterator, except that rather
than *pulling* data with `next` we push data through with `source.emit`.  And
we've done all of this at only a 10x slowdown over normal Python iteators :)
(this library takes a few microseconds per element rather than CPython's normal
100ns overhead).

This will get more interesting in the next few sections.


Branching
---------

This approach becomes more interesting if we add multiple inputs and outputs.

```python
source = Stream()
s = source.map(inc)
evens = s.filter(iseven)
evens.accumulate(add)

odds = s.filter(isodd)
odds.accumulate(sub)
```

Or we can combine streams together

```python
second_source = Stream()
s = combine_latest(second_source, odds).map(sum)
```

So you may have multiple different input sources updating at different rates
and you may have multiple outputs, perhaps some going to a diagnostics
dashboard, others going to long-term storage, others going to a database, etc..
A streaming library makes it relatively easy to set up infrastructure and pipe
everything to the right locations.

Time and Back Pressure
----------------------

When dealing with systems that produce and consume data continuously you often
want to control the flow so that the rates of production are not greater than
the rates of consumption.  For example if you can only write data to a database
at 10MB/s or if you can only make 5000 web requests an hour then you want to
make sure that the other parts of the pipeline don't feed you too much data,
too quickly, which would eventually lead to a buildup in one place.

To deal with this, as our operations push data forward they also accept Tornado
Futures as a receipt.

    Upstream: Hey Downstream! Here is some data for you
    Downstream: Thanks Upstream!  Let me give you a Tornado future in return.
                Make sure you don't send me any more data until that future
                finishes.
    Upstream: Got it, Thanks!  I will pass this to the person who gave me the
              data that I just gave to you.

Under normal operation you don't need to think about Tornado futures at all
(many Python users aren't familiar with asynchronous programming) but it's nice
to know that the library will keep track of balancing out flow.  The code below
uses `@gen.coroutine` and `yield` common for Tornado coroutines.  This is
similar to the async/await syntax in Python 3.  Again, you can safely ignore it
if you're not familiar with asynchronous programming.

```python
@gen.coroutine
def write_to_database(data):
    with connect('my-database:1234/table') as db:
        yield db.write(data)

source = Stream()
(source.map(...)
       .accumulate(...)
       .sink(write_to_database))  # <- sink produces a Tornado future

for data in infinite_feed:
    yield source.emit(data)       # <- that future passes through everything
                                  #    and ends up here to be waited on
```

There are also a number of operations to help you buffer flow in the right
spots, control rate limiting, etc..

```python
source = Stream()
source.timed_window(interval=0.050)  # Capture all records of the last 50ms into batches
      .filter(len)                   # Remove empty batches
      .map(...)                      # Do work on each batch
      .buffer(10)                    # Allow ten batches to pile up here
      .sink(write_to_database)       # Potentially rate-limiting stage
```

I've written enough little utilities like `timed_window` and `buffer` to
discover both that in a full system you would want more of these, and that they
are easy to write.  Here is the definition of `timed_window`

```python
class timed_window(Stream):
    def __init__(self, interval, child, loop=None):
        self.interval = interval
        self.buffer = []
        self.last = gen.moment

        Stream.__init__(self, child, loop=loop)
        self.loop.add_callback(self.cb)

    def update(self, x, who=None):
        self.buffer.append(x)
        return self.last

    @gen.coroutine
    def cb(self):
        while True:
            L, self.buffer = self.buffer, []
            self.last = self.emit(L)
            yield self.last
            yield gen.sleep(self.interval)
```

If you are comfortable with Tornado coroutines or asyncio then my hope is that
this should feel natural.


Recursion and Feedback
----------------------

By connecting the sink of one stream to the emit function of another we can
create feedback loops.  Here is stream that produces the Fibonnacci sequence.
To stop it from overwhelming our local process we added in a rate limiting step:

```python
from streams import Stream
source = Stream()
s = source.sliding_window(2).map(sum)
L = s.sink_to_list()  # store result in a list

s.rate_limit(0.5).sink(source.emit)  # pipe output back to input

source.emit(0)  # seed with initial values
source.emit(1)
```

```python
>>> L
[1, 2, 3, 5]

>>> L  # wait a couple seconds, then check again
[1, 2, 3, 5, 8, 13, 21, 34]

>>> L  # wait a couple seconds, then check again
[1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
```

*Note: due to the time rate-limiting functionality this example relied on an
event loop running somewhere in another thread.  This is the case for example
in a Jupyter notebook, or if you have a Dask Client running.*


Things that this doesn't do
---------------------------

If you are familiar with streaming systems then you may say the following:

*Lets not get ahead of ourselves; there's way more to a good streaming
system than what is presented here.  You need to handle parallelism, fault
tolerance, out-of-order elements, event/processing times, etc..*

... and you would be entirely correct.  What is presented here is not in any
way a competitor to existing systems like Flink for production-level data
engineering problems.  There is a *lot* of logic that hasn't been built here
(and its good to remember that this project was built at night over a week).

Although some of those things, and in particular the distributed computing
bits, we may get for free.


Distributed computing
---------------------

So, during the day I work on [Dask](http://dask.pydata.org/en/latest/), a
Python library for parallel and distributed computing.  The core task
schedulers within Dask are more than capable of running these kinds of
real-time computations.  They handle far more complex real-time systems every
day including few-millisecond latencies, node failures, asynchronous
computation, etc..  People use these features today inside companies, but they
tend to roll their own system rather than use a high-level API (indeed, they
chose Dask because their system was complex enough or private enough that
rolling their own was a necessity).  Dask lacks any kind of high-level
streaming API today.

Fortunately, the system we described above can be modified fairly easily to use
a Dask Client to submit functions rather than run them locally.

```python
from dask.distributed import Client
client = Client()       # start Dask in the background

source.to_dask()
      .scatter()        # send data to a cluster
      .map(...)         # this happens on the cluster
      .accumulate(...)  # this happens on the cluster
      .gather()         # gather results back to local machine
      .sink(...)        # This happens locally
```


Other things that this doesn't do, but could with modest effort
---------------------------------------------------------------

There are a variety of ways that we could improve this with modest cost:

1.  **Streams of sequences**:  We can be more efficient if we pass not individual
    elements through a Stream, but rather lists of elements.  This will let us
    lose the microseconds of overhead that we have now per element and let us
    operate at pure Python (100ns) speeds.
2.  **Streams of NumPy arrays / Pandas dataframes**:  Rather than pass individual
    records we might pass bits of Pandas dataframes through the stream.  So for
    example rather than filtering elements we would filter out rows of the
    dataframe.  Rather than compute at Python speeds we can compute at C
    speeds.  We've built a lot of this logic before for dask.dataframe.  Doing
    this again is straightforward but somewhat time consuming.
3.  **Annotate elements**: we want to pass through event time, processing time, and
    presumably other metadata
4.  **Convenient Data IO utilities**:  We would need some convenient way to move
    data in and out of Kafka and other common continuous data streams.

None of these things are hard.  Many of them are afternoon or weekend projects
if anyone wants to pitch in.


Reasons I like this project
---------------------------

This was originally built strictly for educational purposes.  I (and hopefully
you) now know a bit more about streaming systems, so I'm calling it a success.
It wasn't designed to compete with existing streaming systems, but still there
are some aspects of it that I like quite a bit and want to highlight.

1.  **Lightweight setup:** You can import it and go without setting up any
    infrastructure.  It *can* run (in a limited way) on a Dask cluster or on an
    event loop, but it's also fully operational in your local Python thread.
    There is no magic in the common case.  Everything up until time-handling
    runs with tools that you learn in an introductory programming class.
2.  **Small and maintainable:** [The codebase](https://github.com/mrocklin/streams) is currently a few hundred lines.
    It is also, I claim, easy for other people to understand.  Here is the code
    for filter:

    ```python
    class filter(Stream):
        def __init__(self, predicate, child):
            self.predicate = predicate
            Stream.__init__(self, child)

        def update(self, x, who=None):
            if self.predicate(x):
                return self.emit(x)
    ```
3.  **Composable with Dask:** Handling distributed computing is tricky to do
    well.  Fortunately this project can offload much of that worry to Dask.
    The dividing line between the two systems is pretty clear and, I think,
    could lead to a decently powerful and maintainable system if we spend time
    here.
4.  **Low performance overhead:** Because this project is so simple it has
    overheads in the few-microseconds range when in a single process.
5.  **Pythonic:** All other streaming systems were originally designed for
    Java/Scala engineers.  While they have APIs that are clearly well thought
    through they are sometimes not ideal for Python users or common Python
    applications.


Future Work
-----------

This project needs both users and developers.

I find it fun and satisfying to work on and so encourage others to play around.
[The codebase](https://github.com/mrocklin/streams) is short and, I think,
easily digestible in an hour or two.

This project was built without a real use case (see the project's [examples
directory](https://github.com/mrocklin/streams/tree/master/examples) for a
basic Daskified web crawler).  It could use patient users with real-world use
cases to test-drive things and hopefully provide PRs adding necessary features.

I genuinely don't know if this project is worth pursuing.  This blogpost is a
test to see if people have sufficient interest to use and contribute to such a
library or if the best solution is to carry on with any of the fine solutions
that already exist.

    pip install git+https://github.com/mrocklin/streams
