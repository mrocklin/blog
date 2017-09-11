---
layout: post
title: Fast GeoSpatial Analysis in Python
category: work
draft: true
tags: [Programming, Python, scipy, dask, pangeo]
theme: twitter
---
{% include JB/setup %}

*This work is supported by [Anaconda Inc.](http://anaconda.com)
and the NASA TODO program*

*This work is a collaboration with [Joris Van den Bossche](https://github.com/jorisvandenbossche/).  This blogpost builds on [Joris's EuroSciPy talk](https://www.youtube.com/watch?v=bWsA2R707BM) ([slides](https://jorisvandenbossche.github.io/talks/2017_EuroScipy_geopandas/#1)) on the same topic*

Summary
-------

We briefly describe Python's GeoSpatial stack and the role of the GeoPandas
library within that stack.  We then discuss two efforts to accelerate
GeoPandas:

1.  Accelerating GeoPandas with C/Cython
2.  Parallelizing GeoPandas with Dask for multi-core and distributed computing

We give performance comparisons and end with work that still has to be done.

This work is not yet appropriate for general use, but may be appropriate for
early adopters and developers.

Background
----------

The [Shapely User Manual](https://toblerity.org/shapely/manual.html) begins
with the following passage on the utility of geospatial analysis to our society.

> Deterministic spatial analysis is an important component of computational
> approaches to problems in agriculture, ecology, epidemiology, sociology, and
> many other fields. What is the surveyed perimeter/area ratio of these patches
> of animal habitat? Which properties in this town intersect with the 50-year
> flood contour from this new flooding model? What are the extents of findspots
> for ancient ceramic wares with maker’s marks “A” and “B”, and where do the
> extents overlap? What’s the path from home to office that best skirts
> identified zones of location based spam? These are just a few of the possible
> questions addressable using non-statistical spatial analysis, and more
> specifically, computational geometry.

Shapely is one library within Python's GeoSpatial stack, which is currently
composed of the following tools:

1.  [Shapely](https://toblerity.org/shapely/manual.html):
    Manages shapes like points, linestrings, and polygons.
    Wraps the GEOS C++ library
2.  [Fiona](https://toblerity.org/fiona/manual.html):
    Handles data ingestion.  Wraps the GDAL library
3.  [Rasterio](https://mapbox.github.io/rasterio/):
    Handles raster data like satelite imagery
4.  [GeoPandas](http://geopandas.org/):
    Extends Pandas with a column of shapely geometries to
    intuitively query tables of geospatially annotated data.

In this post we focus on GeoPandas, a geospatial extension of Pandas which
helps to manages tabular data that is annotated with geometry information like
points, paths, and polygons.

### GeoPandas Example

For example GeoPandas makes it easy to load and plot the [Police Districts of
Chicago](https://data.cityofchicago.org/Public-Safety/Boundaries-Police-Districts/4dt9-88ua).

```python
import geopandas as gpd
df = gpd.read_file('PoliceDistrict.shp').to_crs({'init' :'epsg:4326'})
df.head()
```

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>DIST_LABEL</th>
      <th>DIST_NUM</th>
      <th>geometry</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>18TH</td>
      <td>18</td>
      <td>POLYGON ((-87.63068325424541 41.92622745706693...</td>
    </tr>
    <tr>
      <th>1</th>
      <td>13TH</td>
      <td>13</td>
      <td>POLYGON ((-87.65742450915607 41.90350864672136...</td>
    </tr>
    <tr>
      <th>2</th>
      <td>11TH</td>
      <td>11</td>
      <td>POLYGON ((-87.70678940136517 41.90283191610752...</td>
    </tr>
    <tr>
      <th>3</th>
      <td>15TH</td>
      <td>15</td>
      <td>POLYGON ((-87.74597835675543 41.90235233186277...</td>
    </tr>
    <tr>
      <th>4</th>
      <td>12TH</td>
      <td>12</td>
      <td>POLYGON ((-87.64110578953293 41.88906960010015...</td>
    </tr>
  </tbody>
</table>

```python
df.plot(color='black')
```
<img src="{{BASE_PATH}}/images/chicago-police-districts.png">

Municipal data like this for cities around the world is becoming increasingly
more common.  Cities are now doing a wonderful job of publishing data in the
open, which provides transparency and an opportunity for citizens to help
analyze, understand, and improve their communities..  Here are a few fun
geospatially-aware datasets that you might find interesting:

1.  [Chicago Crimes from 2001 to present (one week ago)](https://data.cityofchicago.org/Public-Safety/Crimes-2001-to-present/ijzp-q8t2)
2.  [Paris Velib (bikeshare) in real time](https://opendata.paris.fr/explore/dataset/stations-velib-disponibilites-en-temps-reel/export/)
3.  [Bike lanes in New Orleans](http://portal-nolagis.opendata.arcgis.com/datasets/bike-lanes)
4.  [New Orleans Police Department incidents involving the use of force](https://data.nola.gov/Public-Safety-and-Preparedness/NOPD-Use-of-Force-Incidents/9mnw-mbde)

Performance
-----------

Unfortunately GeoPandas can be slow, which limits interactive exploration on
larger datasets.  The first dataset mentioned above, crimes in Chicago, has
roughly seven million entries and is several gigabytes in memory.  Analyzing
this sort of dataset interactively with GeoPandas today is not feasible.

<img src="{{BASE_PATH}}/images/geopandas-shapely-1.svg"
     width="50%"
     align="right">

This slow performance is because of how GeoPandas is designed today.  Today
GeoPandas is a Pandas dataframe with a special `object`-dtype column that
stores Shapely geometries.  Shapely geometries are Python objects that provide
a Python interface and reference to GEOS Geometry objects in C.  GeoPandas
operations are really just Python for loops over shapely calls so the following
calls are roughly equivalent:

    df.geometry.distance(some_point)  # this line is the same as the line below
    [geom.distance(p) for geom in df.geometry]

Where each `geom` object in this iteration is an individual Shapely object.
This is inefficient for two reasons:

1.  Iterating through these Python objects can be quite slow relative to iterating through those same objects in C.
2.  Shapely Python objects can take up a significant amount of RAM relative to
    the GEOS Geometry objects that they wrap.

In Joris's recent [EuroSciPy talk](https://www.youtube.com/watch?v=bWsA2R707BM)
he compares performance to [PostGIS](http://postgis.net/), the standard
geospatial plugin for the popular PostgreSQL database ([original notebook](https://github.com/jorisvandenbossche/talks/blob/master/2017_EuroScipy_geopandas/geopandas_postgis_comparison.ipynb) with the comparison).  He finds that while
GeoPandas can often be as expressive as PostGIS it is also much slower.  Here
is his benchmark query against the NYC census data.

#### PostGIS Query
```sql
-- What is the population and racial make-up of the neighborhoods of Manhattan?
SELECT
  neighborhoods.name AS neighborhood_name, Sum(census.popn_total) AS population,
  100.0 * Sum(census.popn_white) / NULLIF(Sum(census.popn_total),0) AS white_pct,
  100.0 * Sum(census.popn_black) / NULLIF(Sum(census.popn_total),0) AS black_pct
FROM nyc_neighborhoods AS neighborhoods
JOIN nyc_census_blocks AS census
ON ST_Intersects(neighborhoods.geom, census.geom)
GROUP BY neighborhoods.name
ORDER BY white_pct DESC;
```

#### GeoPandas Code

```python
res = geopandas.sjoin(nyc_neighborhoods, nyc_census_blocks, op='intersects')
res = res.groupby('NAME')[['POPN_TOTAL', 'POPN_WHITE', 'POPN_BLACK']].sum()
res['POPN_BLACK'] = res['POPN_BLACK'] / res['POPN_TOTAL'] * 100
res['POPN_WHITE'] = res['POPN_WHITE'] / res['POPN_TOTAL'] * 100
res.sort_values('POPN_WHITE', ascending=False)
```

Example from [Boundless tutorial](http://workshops.boundlessgeo.com/postgis-intro/) (CC BY SA)

He observes the following performance comparison.

<img src="{{BASE_PATH}}/images/timings_sjoin.png">

Fortunately, we can improve upon this both by accelerating GeoPandas with
Cython, and then by parallelizing it with Dask.

Cythonizing GeoPandas
---------------------

Currently the slowdown in GeoPandas is because we iterate over every Shapely
object in Python, rather than calling the underlying C library GEOS directly.

So instead of using a Pandas `object`-dtype column that *holds shapely objects*
like the following image:

<img src="{{BASE_PATH}}/images/geopandas-shapely-1.svg"
     width="49%">

We instead store a NumPy array of *direct pointers to the GEOS objects*.


<img src="{{BASE_PATH}}/images/geopandas-shapely-2.svg"
     width="49%">

This allows us to store data more efficiently, and also requires us to now
write our loops over these geometries in C or Cython.  When we perform bulk
vectorized operations on many GEOS pointers at once like in the
`df.geometry.distance(some_point)` example above we can now drop down to Cython
or C to write these loops directly, which provides a significant speedup.

As an example, we include Cython code to compute distance between a GeoSeries
and an individual shapely object below:

```python
cdef GEOSGeometry *left_geom
cdef GEOSGeometry *right_geom = some_point.__geom__  # a geometry pointer

with nogil:
    for idx in xrange(n):
        left_geom = <GEOSGeometry *> arr[idx]
        if left_geom != NULL:
            distance = GEOSDistance_r(handle, left_geom, some_point.__geom)
        else:
            distance = NaN
```

For more complex operations, like spatial joins, we tend to use C rather than
Cython just for future development ease.  In both cases we use Cython to
connect the C code back to Python.

#### Results

These operations now run at full C speed, and so we get back to exactly the
performance of PostGIS.

<img src="{{BASE_PATH}}/images/timings_sjoin_all.png">

This is not surprising because PostGIS is using the same GEOS library
internally.  In fact, nearly *all* open source GIS libraries all depend on
GEOS.  These algorithms are not particularly complex, so it is not surprising
that everyone has implemented them more or less exactly the same.

This is great.  The Python GIS stack now has a full-speed library that operates
as fast as any other open GIS system is likely to manage.

Problems
--------

However, this is still a work in progress, and there is still plenty of work
to do.

First, we need for Pandas to track our arrays of GEOS pointers differently from
how it tracks a normal integer array.  This is both for usability reasons, like
we want to render them differently and don't want users to be able to perform
numeric operations like sum and mean on these arrays, and also for stability
reasons, because we need to track these pointers and release their allocated
GEOSGeometry objects from memory at the appropriate times. Currently, this
goal is pursued by creating a new block type, the GeometryBlock ('blocks' are
the internal building blocks of pandas that hold the data of the different columns).
This will require some changes to Pandas itself to enable custom block types
(see [this issue](https://github.com/pandas-dev/pandas/issues/17144) on the pandas
issue tracker).

Second, data ingestion is still quite slow.  This relies not on GEOS, but on
GDAL/OGR, which is handled in Python today by Fiona.  Fiona is more optimized
for consistency and usability rather than raw speed.  Previously when GeoPandas
was slow this made sense because no one was operating on particularly large
datasets.  However now we observe that data loading is often several times more
expensive than all of our manipulations so this will probably need some effort
in the future.

Third, there are some algorithms within GeoPandas that we haven't yet
Cythonized.  This includes both particular features like overlay and dissolve
operations as well as small components like GeoJSON output.

Finally as with any rewrite on a codebase that is not exhaustively tested
(we're trying to improve testing as we do this) there are probably several bugs
that we won't detect until some patient and forgiving user runs into them
first.

Still though, all linear geospatial operations work well and are thoroughly
tested.  Also spatial joins (a backbone of many geospatial operations) are up
and running at full speed.  If you work in a non-production environment then
Cythonized GeoPandas may be worth your time to investigate.

You can track future progress on this effort at
[geopandas/geopandas #473](https://github.com/geopandas/geopandas/issues/473)
which includes installation instructions.


Parallelism with Dask
---------------------

Cythonizing can give us speedups in the 10x-100x range.  We can probably get
another 2-3x by parallelizing with Dask on single multi-core machines, or use
Dask to scale out onto clusters.  In order to do this we need to figure out how
to split apart geospatial data in a way that most geospatial algorithms can be
efficiently parallelized.  We will do this by partitioning our data spatially
into different regions.  There is a rudimentary
[dask-geopandas](https://github.com/mrocklin/dask-geopandas) library available
on GitHub which implements this approach.

Just as dask.array organizes many NumPy arrays along a grid

<img src="{{BASE_PATH}}/images/dask-array-black-text.svg" width="60%">

and dask.dataframe organizes many Pandas dataframes along a linear index

<img src="{{BASE_PATH}}/images/dask-dataframe.svg" width="30%">

Dask-geopandas organizes many GeoPandas dataframes along spatial regions.  In
the example below we might partition data in the city of New York along its
different boroughs.  Data for each borough would be handled separately by a
different thread or, in a distributed situation, might live on a different
machine.

<img src="{{BASE_PATH}}/images/nyc-boroughs.svg" width="50%">

This gives us two advantages:

1.  Even without geospatial partitioning, we can use many cores (or many
    machines) to accelerate simple operations.
2.  For spatially aware operations, like spatial joins or subselections we can
    engage only those parts of the parallel dataframe that we know are relevant
    for various parts of the computation.

TODO: example

Problems
--------

The dask-geopandas project is just a prototype at the moment.  It will easily
break for non-trivial applications (and indeed many trivial ones).  It was
designed to see how hard it would be to implement some of the trickier
operations like spatial joins, repartitioning, and overlays.  This is why, for
example, it supports a fully distributed spatial join, but lacks simple
operations like series addition.

There are other longer term problems as well.  For example geo-spatial
serialization is not particularly fast.  We currently use the standard
"well known binary" WKB format common in other geospatial applications but have
found it to be fairly slow, which bogs down inter-process parallelism.
Similarly distributed and spatially partitioned data stores don't seem to be
common (or at least I haven't run across them yet).

Still though, these seem surmountable and generally this process has been easy
so far.  I suspect that we can build an intuitive and performant parallel GIS
analytics system with modest effort.


Conclusion
----------

With established technologies in the PyData space like Cython and Dask we've
been able to accelerate and scale GeoPandas operations above and beyond
industry standards.  However this work is still experimental and not ready for
production use.  This work is a bit of a side project for both Joris and
Matthew and they would welcome effort from other experienced open source
developers.  We believe that this project can have a large social impact and
are enthusiastic about pursuing it in the future.  We hope that you share our
enthusiasm.
