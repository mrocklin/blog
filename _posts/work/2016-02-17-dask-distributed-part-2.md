---
layout: post
title: Dask DataFrames on HDFS
draft: true
category : work
tags : [Programming, scipy, Python, dask]
theme: twitter
---
{% include JB/setup %}

[Last post](http://matthewrocklin.com/blog/work/2016/02/17/dask-distributed-part1)
we used Dask+distributed on a cluster to analyze GitHub data stored as JSON on
S3.  Today we use Dask+distributed and dask.dataframe to analyze the NYC Taxi
dataset stored as CSV on HDFS.

<table>
<thead>
  <tr>
    <th></th>
    <th>Last post</th>
    <th>This post</th>
  </tr>
</thead>
<tbody>
  <tr>
    <th>Dataset</th>
    <td>GitHub</td>
    <td>NYC Taxi</td>
  </tr>
  <tr>
    <th>Format</th>
    <td>JSON</td>
    <td>CSV</td>
  </tr>
  <tr>
    <th>Location</th>
    <td>S3</td>
    <td>HDFS</td>
  </tr>
  <tr>
    <th>Collection</th>
    <td>dask.bag</td>
    <td>dask.dataframe</td>
  </tr>
</tbody>
</table>

*A video version of this blogpost is available
[here](https://www.youtube.com/watch?v=8Y5hyHU8kwU).*




NYCTaxi Data on HDFS
--------------------

The New York City Taxi and Limousine Commission [makes
public](http://www.nyc.gov/html/tlc/html/about/trip_record_data.shtml) a record
of all taxi trips taken by Yellow Cabs within the city.  This is a nice model
dataset for computational tabular data because it's large enough to be annoying
while also deep enough to be broadly appealing.  It's about 20GB on disk and
about 60GB in memory as a Pandas DataFrame.

For interactive analytics it's convenient to load the entire dataset into
memory.  One way to get this much memory is with a cluster on EC2.

### Setup

We set up a cluster with HDFS on EC2 with eight workers and one head node.
Each node is an `m3.2xlarge` with 8 cores and 30 GB of RAM.

### Load onto HDFS

We download and dump the NYCTaxi data from the head node.

```python
$ wget https://storage.googleapis.com/tlc-trip-data/2015/yellow_tripdata_2015-{01..12}.csv
$ hdfs dfs -mkdir /nyctaxi
$ hdfs dfs -mkdir /nyctaxi/2015
$ hdfs dfs -put yellow*.csv /nyctaxi/2015/
```

HDFS stores these CSV files as 128 MB blocks of bytes distributed throughout
the cluster.


Distributed DataFrames
----------------------

We connect to the scheduler and create a dask dataframe from the dataset on
HDFS.

```python
>>> from distributed import Executor, hdfs, progress
>>> e = Executor('127.0.0.1:8786')
>>> e
<Executor: scheduler=127.0.0.1:8786 workers=8 threads=64>

>>> df = hdfs.read_csv('/nyctaxi/2015/*.csv',
...            parse_dates=['tpep_pickup_datetime', 'tpep_dropoff_datetime'])
```

The `hdfs.read_csv` function takes a location on HDFS, any keyword arguments
you would pass to `pandas.read_csv` and creates a dask dataframe object.  Dask
dataframes faithfully implement a subset of the Pandas API, but operate in
parallel either off disk or on a distributed cluster.

We ask the scheduler to instantiate the dataset in memory with the `e.persist`
method.  This causes each worker node to read blocks of data from HDFS and
apply the `pandas.read_csv` function to each block accordingly.  This creates
many small Pandas dataframes spread throughout the memory of our cluster.  The
resulting dask dataframe keeps track of these many small Pandas dataframes and
triggers computations on them when appropriate.

```python
>>> df = e.persist(df)
```

The full process takes about a minute to load and parse (more on performance
later on).  Afterwards we can perform simple computations at interactive
speeds.

```python
>>> %time df.head()
CPU times: user 8 ms, sys: 0 ns, total: 8 ms
Wall time: 29.7 ms
```

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>VendorID</th>
      <th>tpep_pickup_datetime</th>
      <th>tpep_dropoff_datetime</th>
      <th>passenger_count</th>
      <th>trip_distance</th>
      <th>pickup_longitude</th>
      <th>pickup_latitude</th>
      <th>RateCodeID</th>
      <th>store_and_fwd_flag</th>
      <th>dropoff_longitude</th>
      <th>dropoff_latitude</th>
      <th>payment_type</th>
      <th>fare_amount</th>
      <th>extra</th>
      <th>mta_tax</th>
      <th>tip_amount</th>
      <th>tolls_amount</th>
      <th>improvement_surcharge</th>
      <th>total_amount</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2</td>
      <td>2015-01-15 19:05:39</td>
      <td>2015-01-15 19:23:42</td>
      <td>1</td>
      <td>1.59</td>
      <td>-73.993896</td>
      <td>40.750111</td>
      <td>1</td>
      <td>N</td>
      <td>-73.974785</td>
      <td>40.750618</td>
      <td>1</td>
      <td>12.0</td>
      <td>1.0</td>
      <td>0.5</td>
      <td>3.25</td>
      <td>0</td>
      <td>0.3</td>
      <td>17.05</td>
    </tr>
    <tr>
      <th>1</th>
      <td>1</td>
      <td>2015-01-10 20:33:38</td>
      <td>2015-01-10 20:53:28</td>
      <td>1</td>
      <td>3.30</td>
      <td>-74.001648</td>
      <td>40.724243</td>
      <td>1</td>
      <td>N</td>
      <td>-73.994415</td>
      <td>40.759109</td>
      <td>1</td>
      <td>14.5</td>
      <td>0.5</td>
      <td>0.5</td>
      <td>2.00</td>
      <td>0</td>
      <td>0.3</td>
      <td>17.80</td>
    </tr>
    <tr>
      <th>2</th>
      <td>1</td>
      <td>2015-01-10 20:33:38</td>
      <td>2015-01-10 20:43:41</td>
      <td>1</td>
      <td>1.80</td>
      <td>-73.963341</td>
      <td>40.802788</td>
      <td>1</td>
      <td>N</td>
      <td>-73.951820</td>
      <td>40.824413</td>
      <td>2</td>
      <td>9.5</td>
      <td>0.5</td>
      <td>0.5</td>
      <td>0.00</td>
      <td>0</td>
      <td>0.3</td>
      <td>10.80</td>
    </tr>
    <tr>
      <th>3</th>
      <td>1</td>
      <td>2015-01-10 20:33:39</td>
      <td>2015-01-10 20:35:31</td>
      <td>1</td>
      <td>0.50</td>
      <td>-74.009087</td>
      <td>40.713818</td>
      <td>1</td>
      <td>N</td>
      <td>-74.004326</td>
      <td>40.719986</td>
      <td>2</td>
      <td>3.5</td>
      <td>0.5</td>
      <td>0.5</td>
      <td>0.00</td>
      <td>0</td>
      <td>0.3</td>
      <td>4.80</td>
    </tr>
    <tr>
      <th>4</th>
      <td>1</td>
      <td>2015-01-10 20:33:39</td>
      <td>2015-01-10 20:52:58</td>
      <td>1</td>
      <td>3.00</td>
      <td>-73.971176</td>
      <td>40.762428</td>
      <td>1</td>
      <td>N</td>
      <td>-74.004181</td>
      <td>40.742653</td>
      <td>2</td>
      <td>15.0</td>
      <td>0.5</td>
      <td>0.5</td>
      <td>0.00</td>
      <td>0</td>
      <td>0.3</td>
      <td>16.30</td>
    </tr>
  </tbody>
</table>

```python
>>> %time len(df)
CPU times: user 20 ms, sys: 0 ns, total: 20 ms
Wall time: 207 ms

146112989
```

So at the simple end of the scale we see that computations happen at a speed
which, for a human, appears to be instantaneous.

Additionally, we get to rely on all of the Pandas magic to parse CSV files,
sniff for names and dtypes, and handle all of the complexity that comes with
real data.

```python
>>> df.dtypes
VendorID                          int64
tpep_pickup_datetime     datetime64[ns]
tpep_dropoff_datetime    datetime64[ns]
passenger_count                   int64
trip_distance                   float64
pickup_longitude                float64
pickup_latitude                 float64
RateCodeID                        int64
store_and_fwd_flag               object
dropoff_longitude               float64
dropoff_latitude                float64
payment_type                      int64
fare_amount                     float64
extra                           float64
mta_tax                         float64
tip_amount                      float64
tolls_amount                    float64
improvement_surcharge           float64
total_amount\r                  float64
dtype: object
```



Analyze Tip Fractions
---------------------

In an effort to demonstrate the abilities of dask.dataframe we answer a
simple question of our data, *How do people tip?*.  The 2015 NYCTaxi data is
quite good about breaking down the total cost of each ride into the fare
amount, tip amount, and various taxes and fees.  In particular this lets us
measure the percentage that each rider decided to pay in tip.

```python
>>> df[['fare_amount', 'tip_amount', 'payment_type']].head()
```

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>fare_amount</th>
      <th>tip_amount</th>
      <th>payment_type</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>12.0</td>
      <td>3.25</td>
      <td>1</td>
    </tr>
    <tr>
      <th>1</th>
      <td>14.5</td>
      <td>2.00</td>
      <td>1</td>
    </tr>
    <tr>
      <th>2</th>
      <td>9.5</td>
      <td>0.00</td>
      <td>2</td>
    </tr>
    <tr>
      <th>3</th>
      <td>3.5</td>
      <td>0.00</td>
      <td>2</td>
    </tr>
    <tr>
      <th>4</th>
      <td>15.0</td>
      <td>0.00</td>
      <td>2</td>
    </tr>
  </tbody>
</table>

In the first two lines we see evidence supporting the 15% standard common in
many parts of the US.  The following three lines interestingly show zero tip.
Judging only by these first five lines (a very small sample) we see a strong
correlation here with the payment type.  I'll leave hypothesizing the reasons
for that to the reader.  Instead, we'll focus on the tip fraction, the ratio of
tip amount to fare amount.

We can easily divide the `tip_amount` column by the `fare_amount` column and
look at averages binned by various times.  When first doing we find that there
are several rides with a fare amount of zero, which confuses the results.

```python
>>> (df.fare_amount == 0).sum().compute()
43938
```

So we filter out these bad rows and then assign a new column, `tip_fraction`:

```python
>>> df2 = df[df.fare_amount > 0]
>>> df2 = df2.assign(tip_fraction=(df2.tip_amount / df2.fare_amount))
```

Next we choose to groupby the pickup datetime column in order to see how the
average tip fraction changes by day of week and by hour.  The groupby and
datetime API of Pandas makes these operations trivial.

```python
>>> dayofweek = df2.groupby(df2.tpep_pickup_datetime.dt.dayofweek).tip_fraction.mean()
>>> hour = df2.groupby(df2.tpep_pickup_datetime.dt.hour).tip_fraction.mean()
```

Finally we compute the results.  Grouping by day-of-week doesn't show anything
too striking to my eye:

```python
>>> dayofweek.compute()
tpep_pickup_datetime
0    0.148737
1    0.152547
2    0.153601
3    0.159282
4    0.153412
5    0.140647
6    0.158863
Name: tip_fraction, dtype: float64
```

But grouping by hour shows that late night and early morning riders are more
likely to tip extravagantly:

```python
>>> hour.compute()
tpep_pickup_datetime
0     0.173191
1     0.182161
2     0.189611
3     0.172473
4     0.194004
5     0.146677
6     0.148386
7     0.144444
8     0.152115
9     0.142903
10    0.138142
11    0.138234
12    0.133805
13    0.138647
14    0.139104
15    0.133041
16    0.136687
17    0.145544
18    0.149922
19    0.176985
20    0.157329
21    0.161524
22    0.162253
23    0.162159
Name: tip_fraction, dtype: float64
```

These computations take around 20-30 seconds which, while not bad, can be
improved (see below).  We plot this with matplotlib and see a nice trough
during business hours with a low around 13.3% at 12pm and a surge in the early
morning with a peak of 19.4% at 4am:

<img src="http://matthewrocklin.com/blog/images/nyctaxi-2015-hourly-tips.png">


Performance
-----------

Lets dive into a few operations that run at different time scales.  This gives
a good understanding of the strengths and limits of the scheduler.

```python
>>> %time df.head()
CPU times: user 8 ms, sys: 0 ns, total: 8 ms
Wall time: 29.7 ms

>>> %time len(df)
CPU times: user 20 ms, sys: 0 ns, total: 20 ms
Wall time: 207 ms

>>> %time df.passenger_count.sum().compute()
CPU times: user 40 ms, sys: 4 ms, total: 44 ms
Wall time: 2.01 s
```

The head computation is very fast.  The 30ms duration is about the time between
two frames in a film; to a human eye this is completely fluid.  In our last
post we talked about how low we could bring latency.  Last time we were bound
by transcontinental latencies of 200ms.  This time, because we're on the
network, we can get down to 30ms.  We're only able to be this fast because we
touch only a single data element, the first partition.

The length computation takes 200 ms.  This computation takes longer because we
touch every individual partition of the data, of which there are 178.  The
scheduler incurs about 1ms of overhead per partition, add a bit of latency
and you get the 200ms total.

The third computation, the sum, is quite surprising.  Computing the sum should
cost about the same as computing the length.  In-memory sums are fast.  In the
video version of this post I ponder the reasons.  Now I think I've narrowed
down the performance bottleneck here to the fact that Pandas functions take a
surprisingly long time to serialize (see issue
[#12021](https://github.com/pydata/pandas/issues/12021)) which is something I
think I can work around in the near future.

Finally, these numbers are only fast because we've already done all of the hard
work of loading data from HDFS and parsing it from CSV into many Pandas
DataFrames.  If you recall, this process took about a minute, which, if we do
the math, comes out to about 350MB/s total bandwidth.

    23GB / 60s ~= 350 MB/s

This is about as fast as you could load data on a single nice hard drive if the
data was encoded efficiently, rather than as CSV.  Pandas CSV runs at around
50 MB/s when parsing datetimes, so we're getting around a 7x speedup, which
makes sense given our number of nodes (read_csv does not release the GIL well.)


Conclusion
----------

We used dask+distributed on a cluster to read CSV data from HDFS
into a dask dataframe.  We then used dask.dataframe, which looks identical to
the Pandas dataframe, to manipulate our distributed dataset intuitively and
efficiently.

We looked a bit at the performance characteristics of simple computations and
noticed a performance flaw.


What doesn't work
-----------------

*   Dask dataframe implements a *subset* of Pandas functionality, not all of it.
    I have found it surprisingly difficult to specify a self-consistent set of
    functionality that satisfies most problems and is clear to users.  It seems
    that every Pandas user depends on a few odd corners of the library.  This
    makes it difficult to set and meet expectations.

*   If you want to use threads, you'll need Pandas 0.18.0 which, at the time of
    this writing, was still in release candidate stage.  This Pandas release
    fixes some important GIL related issues.

*   The performance degradation mentioned in the performance section is
    significant.  Summing a column of a 60GB dataset should complete in far
    less than 2s.  I have a good idea on how to resolve this though and am
    optimistic that this will accelerate several computations within this post,
    including the final groupby on pickup datetime.

*   We use the [hdfs3 library](http://hdfs3.readthedocs.org/en/latest/) to read
    data from HDFS.  This library seems to work great but is new and could use
    more active users to flush out bug reports.


Links
-----

*   [dask](https://dask.pydata.org/en/latest/), the original project
*   [distributed](https://distributed.readthedocs.org/en/latest/), the
    distributed memory scheduler powering the cluster computing
*   [dask.dataframe](http://dask.pydata.org/en/latest/dataframe.html), the user
    API we've used in this post.
