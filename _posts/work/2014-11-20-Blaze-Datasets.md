---
layout: post
title: Blaze Datasets
tagline: Often the hardest thing is finding what you already have
category : work
draft: true
tags : [scipy, Python, Programming]
---
{% include JB/setup %}

**tl;dr** Blaze isn't just tables.  Full databases and collections of datasets
are first class variables.

This post was composed using Blaze version 0.6.6.  You can follow along with
the following conda command.

    conda install -c blaze blaze=0.6.6

Motivating problem - Intuitive HDF5 File Navigation
---------------------------------------------------

We want to understand the contents of a [set of HDF5
files](http://mirador.gsfc.nasa.gov/cgi-bin/mirador/granlist.pl?page=1&location=(-90,-180),(90,180)&dataSet=OMAERO&version=003&allversion=003&startTime=2014-11-05T00:00:01Z&endTime=2014-11-05T23:59:59Z&keyword=OMAERO&longname=OMI/Aura%20Multi-wavelength%20Aerosol%20Optical%20Depth%20and%20Single%20Scattering%20Albedo%201-orbit%20L2%20Swath%2013x24%20km&CGISESSID=958493efa9d8a96c5ba2d0b4d69c986d&prodpg=http://mirador.gsfc.nasa.gov/collections/OMAERO__003.shtml)
encoding meteorological data.  As is common in HDF5 files, this data is a highly
nested collection of arrays.

Typically we navigate these files in Python with `h5py` or `pytables`.

{% highlight Python %}
>>> import h5py
>>> f = h5py.File('OMI-Aura_L2-OMAERO_2014m1105t2304-o54838_v003-2014m1106t215558.he5')
<HDF5 file "OMI-Aura_L2-OMAERO_2014m1105t2304-o54838_v003-2014m1106t215558.he5" (mode r+)>
{% endhighlight %}

HDF5 files organize datasets with an internal file system.  The `h5py` library
provides access to this organization through successive calls to `.keys()` and
item access.

{% highlight Python %}
>>> f.keys()
['HDFEOS', 'HDFEOS INFORMATION']

>>> f['/HDFEOS'].keys()
['ADDITIONAL', 'SWATHS']

>>> f['/HDFEOS/SWATHS'].keys()
...

>>> f['/HDFEOS/SWATHS/ColumnAmountAerosol/Data Fields/TerrainPressure'][:]
array([[1013, 1013, 1013, ..., 1013, 1013, 1013],
       [1013, 1013, 1013, ..., 1013, 1013, 1013],
       [1013, 1013, 1013, ..., 1013, 1013, 1013],
       ...,
       [1010,  992,  986, ..., 1013, 1013, 1013],
       [ 999,  983,  988, ..., 1013, 1013, 1013],
       [1006,  983,  993, ..., 1013, 1013, 1013]], dtype=int16)
{% endhighlight %}


This process requires a long and awkward conversation between programmer and
interpreter.  This process can be improved.

Blaze improves the discovery experience both in HDF5 files and in other collections
of datasets like SQL Databases, Mongo Databases, etc..  These types are now
first class citizens in Blaze.  By treating collections of arrays/tables as
first class datasets we allow users to both explore and compute on these larger
structures in the same workflow.


Historically Blaze only supported Tables
----------------------------------------

In Blaze v0.6 we only supported Tables.  It was typical to specify a table with
a URI.  This URI often included both

1.  The location of the database/file/server
2.  A table name within that database/file/server

### Example

{% highlight Python %}
>>> iris = Table('sqlite:////my.db::iris')  # protocol://database::table-name
>>> iris
    sepal_length  sepal_width  petal_length  petal_width      species
0            5.1          3.5           1.4          0.2  Iris-setosa
1            4.9          3.0           1.4          0.2  Iris-setosa
2            4.7          3.2           1.3          0.2  Iris-setosa
3            4.6          3.1           1.5          0.2  Iris-setosa
4            5.0          3.6           1.4          0.2  Iris-setosa
...
{% endhighlight %}


Expanding data types
--------------------

Now Blaze expressions support tables, arrays, nested data structures, etc..
Anything falling into the [datashape](http://datashape.pydata.org/) model.
As a pleasant side effect Blaze navigates collections of datasets (like
databases or HDF5 files) in the same manner as it navigates fields in a table
or array.  There is no fundamental difference between a numpy array and a SQL
database.

{% highlight Python %}
>>> # iris = Table('sqlite:///my.db::iris')  # protocol://database::table-name
>>> db = Data('sqlite:///my.db')

>>> db
Data:
Engine(sqlite:////home/mrocklin/workspace/blaze/blaze/examples/data/iris.db)
DataShape:  {
  iris: var * {
    sepal_length: ?float64,
    sepal_width: ?float64,
    petal_length: ?float64,
    petal_width: ?float64,
    species: ?string
  ...
{% endhighlight %}

The `db` expression points to a SQLAlchemy engine.  We print the engine
alongside a truncated datashape showing the metadata of the tables in that
database.  Note that the datashape maps table names to datashapes of those
tables, in this case a variable length collection of records with fields for
measurements of flowers.

As always Blaze leverages SQLAlchemy reflection to discover this metadata.
Blaze isn't doing any of the work (SQLAlchemy is) instead it exposes this
metadata in a pleasant way.  We leverage SQLAlchemy because it robustly
supports a very wide array of databases ranging from `sqlite` up to `impala`
and because it supports both inspection and general computation.

We seamlessly transition from exploration to computation.  Blaze doesn't pull
data into local memory, instead it generates SQLAlchemy which generates SQL,
which executes on the foreign database; the (much smaller) result is pulled
back and rendered nicely using Pandas.

{% highlight Python %}
>>> by(db.iris.species, smallest=db.iris.sepal_length.min(),
...                      biggest=db.iris.sepal_length.max())
           species  biggest  smallest
0      Iris-setosa      5.8       4.3
1  Iris-versicolor      7.0       4.9
2   Iris-virginica      7.9       4.9
{% endhighlight %}


This is more interesting on a larger database
---------------------------------------------

Improved metadata discovery on SQL databases overlaps somewhat with the
excellent work done by `yhat` on
[db.py](http://blog.yhathq.com/posts/introducing-db-py.html).  We steal their
example, the Lahman Baseball statistics database as an example of a richer
database with a greater variety of tables.

{% highlight Python %}
>>> lahman = Data('sqlite:///baseball-archive-2012.sqlite')
>>> lahman.dshape # lets ask for the entire datashape

dshape("""{
  battingpost: var * {
    yearID: ?int32,
    round: ?string,
    playerID: ?string,
    teamID: ?string,
    lgID: ?string,
    G: ?int32,
    AB: ?int32,
    R: ?int32,
    H: ?int32,
    2B: ?int32,
    3B: ?int32,
    HR: ?int32,
    RBI: ?int32,
    SB: ?int32,
    CS: ?int32,
    BB: ?int32,
    SO: ?int32,
    IBB: ?int32,
    HBP: ?int32,
    SH: ?int32,
    SF: ?int32,
    GIDP: ?int32
    },
  awardsmanagers: var * {
    managerID: ?string,
    awardID: ?string,
    yearID: ?int32,
    lgID: ?string,
    tie: ?string,
    notes: ?string
    },
  hofold: var * {
    hofID: ?string,
    yearid: ?int32,
    votedBy: ?string,
    ballots: ?int32,
    votes: ?int32,
    inducted: ?string,
    category: ?string
    },
  salaries: var * {
    yearID: ?int32,
    teamID: ?string,
    lgID: ?string,
    playerID: ?string,
    salary: ?float64
    },
  pitchingpost: var * {
    playerID: ?string,
    yearID: ?int32,
    round: ?string,
    teamID: ?string,
    lgID: ?string,
    W: ?int32,
    L: ?int32,
    G: ?int32,
    GS: ?int32,
    CG: ?int32,
    SHO: ?int32,
    SV: ?int32,
    IPouts: ?int32,
    H: ?int32,
    ER: ?int32,
    HR: ?int32,
    BB: ?int32,
    SO: ?int32,
    BAOpp: ?float64,
    ERA: ?float64,
    IBB: ?int32,
    WP: ?int32,
    HBP: ?int32,
    BK: ?int32,
    BFP: ?int32,
    GF: ?int32,
    R: ?int32,
    SH: ?int32,
    SF: ?int32,
    GIDP: ?int32
    },
  managers: var * {
    managerID: ?string,
    yearID: ?int32,
    teamID: ?string,
    lgID: ?string,
    inseason: ?int32,
    G: ?int32,
    W: ?int32,
    L: ?int32,
    rank: ?int32,
    plyrMgr: ?string
    },
  teams: var * {
    yearID: ?int32,
    lgID: ?string,
    teamID: ?string,
    franchID: ?string,
    divID: ?string,
    Rank: ?int32,
    G: ?int32,
    Ghome: ?int32,
    W: ?int32,
    L: ?int32,
    DivWin: ?string,
    WCWin: ?string,
    LgWin: ?string,
    WSWin: ?string,
    R: ?int32,
    AB: ?int32,
    H: ?int32,
    2B: ?int32,
    3B: ?int32,
    HR: ?int32,
    BB: ?int32,
    SO: ?int32,
    SB: ?int32,
    CS: ?int32,
    HBP: ?int32,
    SF: ?int32,
    RA: ?int32,
    ER: ?int32,
    ERA: ?float64,
    CG: ?int32,
    SHO: ?int32,
    SV: ?int32,
    IPouts: ?int32,
    HA: ?int32,
    HRA: ?int32,
    BBA: ?int32,
    SOA: ?int32,
    E: ?int32,
    DP: ?int32,
    FP: ?float64,
    name: ?string,
    park: ?string,
    attendance: ?int32,
    BPF: ?int32,
    PPF: ?int32,
    teamIDBR: ?string,
    teamIDlahman45: ?string,
    teamIDretro: ?string
    },
  teamshalf: var * {
    yearID: ?int32,
    lgID: ?string,
    teamID: ?string,
    Half: ?string,
    divID: ?string,
    DivWin: ?string,
    Rank: ?int32,
    G: ?int32,
    W: ?int32,
    L: ?int32
    },
  fieldingpost: var * {
    playerID: ?string,
    yearID: ?int32,
    teamID: ?string,
    lgID: ?string,
    round: ?string,
    POS: ?string,
    G: ?int32,
    GS: ?int32,
    InnOuts: ?int32,
    PO: ?int32,
    A: ?int32,
    E: ?int32,
    DP: ?int32,
    TP: ?int32,
    PB: ?int32,
    SB: ?int32,
    CS: ?int32
    },
  master: var * {
    lahmanID: ?int32,
    playerID: ?string,
    managerID: ?string,
    hofID: ?string,
    birthYear: ?int32,
    birthMonth: ?int32,
    birthDay: ?int32,
    birthCountry: ?string,
    birthState: ?string,
    birthCity: ?string,
    deathYear: ?int32,
    deathMonth: ?int32,
    deathDay: ?int32,
    deathCountry: ?string,
    deathState: ?string,
    deathCity: ?string,
    nameFirst: ?string,
    nameLast: ?string,
    nameNote: ?string,
    nameGiven: ?string,
    nameNick: ?string,
    weight: ?int32,
    height: ?float64,
    bats: ?string,
    throws: ?string,
    debut: ?string,
    finalGame: ?string,
    college: ?string,
    lahman40ID: ?string,
    lahman45ID: ?string,
    retroID: ?string,
    holtzID: ?string,
    bbrefID: ?string
    },
  fieldingof: var * {
    playerID: ?string,
    yearID: ?int32,
    stint: ?int32,
    Glf: ?int32,
    Gcf: ?int32,
    Grf: ?int32
    },
  pitching: var * {
    playerID: ?string,
    yearID: ?int32,
    stint: ?int32,
    teamID: ?string,
    lgID: ?string,
    W: ?int32,
    L: ?int32,
    G: ?int32,
    GS: ?int32,
    CG: ?int32,
    SHO: ?int32,
    SV: ?int32,
    IPouts: ?int32,
    H: ?int32,
    ER: ?int32,
    HR: ?int32,
    BB: ?int32,
    SO: ?int32,
    BAOpp: ?float64,
    ERA: ?float64,
    IBB: ?int32,
    WP: ?int32,
    HBP: ?int32,
    BK: ?int32,
    BFP: ?int32,
    GF: ?int32,
    R: ?int32,
    SH: ?int32,
    SF: ?int32,
    GIDP: ?int32
    },
  managershalf: var * {
    managerID: ?string,
    yearID: ?int32,
    teamID: ?string,
    lgID: ?string,
    inseason: ?int32,
    half: ?int32,
    G: ?int32,
    W: ?int32,
    L: ?int32,
    rank: ?int32
    },
  appearances: var * {
    yearID: ?int32,
    teamID: ?string,
    lgID: ?string,
    playerID: ?string,
    G_all: ?int32,
    G_batting: ?int32,
    G_defense: ?int32,
    G_p: ?int32,
    G_c: ?int32,
    G_1b: ?int32,
    G_2b: ?int32,
    G_3b: ?int32,
    G_ss: ?int32,
    G_lf: ?int32,
    G_cf: ?int32,
    G_rf: ?int32,
    G_of: ?int32,
    G_dh: ?int32,
    G_ph: ?int32,
    G_pr: ?int32
    },
  halloffame: var * {
    hofID: ?string,
    yearid: ?int32,
    votedBy: ?string,
    ballots: ?int32,
    needed: ?int32,
    votes: ?int32,
    inducted: ?string,
    category: ?string
    },
  awardsplayers: var * {
    playerID: ?string,
    awardID: ?string,
    yearID: ?int32,
    lgID: ?string,
    tie: ?string,
    notes: ?string
    },
  schoolsplayers: var * {
    playerID: ?string,
    schoolID: ?string,
    yearMin: ?int32,
    yearMax: ?int32
    },
  schools: var * {
    schoolID: ?string,
    schoolName: ?string,
    schoolCity: ?string,
    schoolState: ?string,
    schoolNick: ?string
    },
  teamsfranchises: var * {
    franchID: ?string,
    franchName: ?string,
    active: ?string,
    NAassoc: ?string
    },
  allstarfull: var * {
    playerID: ?string,
    yearID: ?int32,
    gameNum: ?int32,
    gameID: ?string,
    teamID: ?string,
    lgID: ?string,
    GP: ?int32,
    startingPos: ?int32
    },
  tmp_batting: var * {
    playerID: ?string,
    yearID: ?int32,
    stint: ?int32,
    teamID: ?string,
    lgID: ?string,
    G: ?int32,
    G_batting: ?int32,
    AB: ?int32,
    R: ?int32,
    H: ?int32,
    2B: ?int32,
    3B: ?int32,
    HR: ?int32,
    RBI: ?int32,
    SB: ?int32,
    CS: ?int32,
    BB: ?int32,
    SO: ?int32,
    IBB: ?int32,
    HBP: ?int32,
    SH: ?int32,
    SF: ?int32,
    GIDP: ?int32,
    G_old: ?int32
    },
  seriespost: var * {
    yearID: ?int32,
    round: ?string,
    teamIDwinner: ?string,
    lgIDwinner: ?string,
    teamIDloser: ?string,
    lgIDloser: ?string,
    wins: ?int32,
    losses: ?int32,
    ties: ?int32
    },
  awardssharemanagers: var * {
    awardID: ?string,
    yearID: ?int32,
    lgID: ?string,
    managerID: ?string,
    pointsWon: ?int32,
    pointsMax: ?int32,
    votesFirst: ?int32
    },
  awardsshareplayers: var * {
    awardID: ?string,
    yearID: ?int32,
    lgID: ?string,
    playerID: ?string,
    pointsWon: ?float64,
    pointsMax: ?int32,
    votesFirst: ?float64
    },
  fielding: var * {
    playerID: ?string,
    yearID: ?int32,
    stint: ?int32,
    teamID: ?string,
    lgID: ?string,
    POS: ?string,
    G: ?int32,
    GS: ?int32,
    InnOuts: ?int32,
    PO: ?int32,
    A: ?int32,
    E: ?int32,
    DP: ?int32,
    PB: ?int32,
    WP: ?int32,
    SB: ?int32,
    CS: ?int32,
    ZR: ?float64
    }
  }""")
{% endhighlight %}

Seeing all at once the tables in the database, the columns in those tables, and
the types of those columns provides a clear and comprehensive overview of our
data.  We use standard Blaze expressions to navigate more deeply.  Things like
auto-complete work fine.

{% highlight Python %}
>>> lahman.<tab>
lahman.allstarfull          lahman.fieldingpost         lahman.pitchingpost
lahman.appearances          lahman.fields               lahman.relabel
lahman.awardsmanagers       lahman.halloffame           lahman.salaries
lahman.awardsplayers        lahman.hofold               lahman.schema
lahman.awardssharemanagers  lahman.isidentical          lahman.schools
lahman.awardsshareplayers   lahman.like                 lahman.schoolsplayers
lahman.battingpost          lahman.managers             lahman.seriespost
lahman.data                 lahman.managershalf         lahman.teams
lahman.dshape               lahman.map                  lahman.teamsfranchises
lahman.fielding             lahman.master               lahman.teamshalf
lahman.fieldingof           lahman.pitching             lahman.tmp_batting
{% endhighlight %}

And we finish by a fun multi-table computation, computing the average salary by team name and year

{% highlight Python %}
>>> j = join(lahman.teams, lahman.salaries, ['yearID', 'teamID', 'lgID'])
>>> by(j[['name', 'yearID']], average_salary=j.salary.mean())
                    name  yearID  average_salary
0         Anaheim Angels    1997  1004370.064516
1         Anaheim Angels    1998  1214147.058824
2         Anaheim Angels    1999  1384704.150000
3         Anaheim Angels    2000  1715472.233333
4         Anaheim Angels    2001  1584505.566667
5         Anaheim Angels    2002  2204345.250000
6         Anaheim Angels    2003  2927098.777778
7         Anaheim Angels    2004  3723506.185185
8   Arizona Diamondbacks    1998   898527.777778
9   Arizona Diamondbacks    1999  2020705.852941
...
{% endhighlight %}

Looks good, we compute and store to CSV file with `into`

{% highlight Python %}
>>> into('salaries.csv',
...      by(j[['name', 'yearID']], total_salary=j.salary.mean()))
{% endhighlight %}


Beyond SQL
----------

SQL databases aren't alone, many systems hold collections of sets of datasets.
Blaze provides this navigation over Mongo databases, [Blaze
servers](http://blaze.pydata.org/docs/latest/server.html), HDF5 files, or even
just dictionaries of pandas DataFrames or CSV files.

{% highlight Python %}
>>> d = {'accounts 1': CSV('accounts_1.csv'),
...      'accounts 2': CSV('accounts_2.csv')}

>>> accounts = Data(d)

>>> accounts.dshape
dshape("""{
  accounts 1: var * {id: ?int64, name: string, amount: ?int64},
  accounts 2: var * {id: ?int64, name: string, amount: ?int64}
  }""")
{% endhighlight %}


Finish up `h5py` example
------------------------

To conclude we revisit our motivating problem, HDF5 file navigation.

### Raw H5Py

{% highlight Python %}
>>> import h5py
>>> f = h5py.File('OMI-Aura_L2-OMAERO_2014m1105t2304-o54838_v003-2014m1106t215558.he5')
>>> f
<HDF5 file "OMI-Aura_L2-OMAERO_2014m1105t2304-o54838_v003-2014m1106t215558.he5" (mode r+)>

>>> f.keys()
['HDFEOS', 'HDFEOS INFORMATION']
>>> f['/HDFEOS'].keys()
['ADDITIONAL', 'SWATHS']
...
{% endhighlight %}

### H5Py with Blaze expressions

{% highlight Python %}
>>> from blaze import Data
>>> d = Data(f)
>>> d
Data:       <HDF5 file "OMI-Aura_L2-OMAERO_2014m1105t2304-o54838_v003-2014m1106t215558.he5" (mode r+)>
DataShape:  {
  HDFEOS: {
    ADDITIONAL: {FILE_ATTRIBUTES: {}},
    SWATHS: {
      ColumnAmountAerosol: {
        Data Fields: {
          AerosolIndexUV: 1643 * 60 * int16,
  ...
{% endhighlight %}

By default we see the data and a truncated datashape.  We ask for the datashape
explicitly to see the full picture.

{% highlight Python %}
>>> d.dshape
dshape("""{
  HDFEOS: {
    ADDITIONAL: {FILE_ATTRIBUTES: {}},
    SWATHS: {
      ColumnAmountAerosol: {
        Data Fields: {
          AerosolIndexUV: 1643 * 60 * int16,
          AerosolIndexVIS: 1643 * 60 * int16,
          AerosolModelMW: 1643 * 60 * uint16,
          AerosolModelsPassedThreshold: 1643 * 60 * 10 * uint16,
          AerosolOpticalThicknessMW: 1643 * 60 * 14 * int16,
          AerosolOpticalThicknessMWPrecision: 1643 * 60 * int16,
          AerosolOpticalThicknessNUV: 1643 * 60 * 2 * int16,
          AerosolOpticalThicknessPassedThreshold: 1643 * 60 * 10 * 9 * int16,
          AerosolOpticalThicknessPassedThresholdMean: 1643 * 60 * 9 * int16,
          AerosolOpticalThicknessPassedThresholdStd: 1643 * 60 * 9 * int16,
          CloudFlags: 1643 * 60 * uint8,
          CloudPressure: 1643 * 60 * int16,
          EffectiveCloudFraction: 1643 * 60 * int8,
          InstrumentConfigurationId: 1643 * uint8,
          MeasurementQualityFlags: 1643 * uint8,
          NumberOfModelsPassedThreshold: 1643 * 60 * uint8,
          ProcessingQualityFlagsMW: 1643 * 60 * uint16,
          ProcessingQualityFlagsNUV: 1643 * 60 * uint16,
          RootMeanSquareErrorOfFitPassedThreshold: 1643 * 60 * 10 * int16,
          SingleScatteringAlbedoMW: 1643 * 60 * 14 * int16,
          SingleScatteringAlbedoMWPrecision: 1643 * 60 * int16,
          SingleScatteringAlbedoNUV: 1643 * 60 * 2 * int16,
          SingleScatteringAlbedoPassedThreshold: 1643 * 60 * 10 * 9 * int16,
          SingleScatteringAlbedoPassedThresholdMean: 1643 * 60 * 9 * int16,
          SingleScatteringAlbedoPassedThresholdStd: 1643 * 60 * 9 * int16,
          SmallPixelRadiancePointerUV: 1643 * 2 * int16,
          SmallPixelRadiancePointerVIS: 1643 * 2 * int16,
          SmallPixelRadianceUV: 6783 * 60 * float32,
          SmallPixelRadianceVIS: 6786 * 60 * float32,
          SmallPixelWavelengthUV: 6783 * 60 * uint16,
          SmallPixelWavelengthVIS: 6786 * 60 * uint16,
          TerrainPressure: 1643 * 60 * int16,
          TerrainReflectivity: 1643 * 60 * 9 * int16,
          XTrackQualityFlags: 1643 * 60 * uint8
          },
        Geolocation Fields: {
          GroundPixelQualityFlags: 1643 * 60 * uint16,
          Latitude: 1643 * 60 * float32,
          Longitude: 1643 * 60 * float32,
          OrbitPhase: 1643 * float32,
          SolarAzimuthAngle: 1643 * 60 * float32,
          SolarZenithAngle: 1643 * 60 * float32,
          SpacecraftAltitude: 1643 * float32,
          SpacecraftLatitude: 1643 * float32,
          SpacecraftLongitude: 1643 * float32,
          TerrainHeight: 1643 * 60 * int16,
          Time: 1643 * float64,
          ViewingAzimuthAngle: 1643 * 60 * float32,
          ViewingZenithAngle: 1643 * 60 * float32
          }
        }
      }
    },
  HDFEOS INFORMATION: {
    ArchiveMetadata.0: string[65535, 'A'],
    CoreMetadata.0: string[65535, 'A'],
    StructMetadata.0: string[32000, 'A']
    }
  }""")
{% endhighlight %}

The full structure of this dataset becomes apparent.  Moreover we can quickly
navigate this structure to obtain relevant information.

{% highlight Python %}
>>> d.HDFEOS.SWATHS.ColumnAmountAerosol.Geolocation_Fields.Latitude
array([[-67., -67., -67., ..., -61., -60., -60.],
       [-67., -67., -67., ..., -61., -60., -60.],
       [-67., -67., -68., ..., -61., -61., -60.],
       ...,
       [ 69.,  70.,  71., ...,  85.,  84.,  84.],
       [ 69.,  70.,  71., ...,  85.,  85.,  84.],
       [ 69.,  70.,  71., ...,  85.,  85.,  84.]], dtype=float32)

>>> d.HDFEOS.SWATHS.ColumnAmountAerosol.Geolocation_Fields.Longitude
array([[  46.,   43.,   40., ...,   -3.,   -5.,   -7.],
       [  46.,   43.,   40., ...,   -3.,   -5.,   -7.],
       [  46.,   43.,   40., ...,   -4.,   -5.,   -7.],
       ...,
       [ 123.,  124.,  124., ..., -141., -131., -121.],
       [ 123.,  124.,  124., ..., -141., -130., -120.],
       [ 123.,  123.,  124., ..., -140., -130., -119.]], dtype=float32)

>>> d.HDFEOS.SWATHS.ColumnAmountAerosol.Data_Fields.TerrainPressure
array([[1013, 1013, 1013, ..., 1013, 1013, 1013],
       [1013, 1013, 1013, ..., 1013, 1013, 1013],
       [1013, 1013, 1013, ..., 1013, 1013, 1013],
       ...,
       [1010,  992,  986, ..., 1013, 1013, 1013],
       [ 999,  983,  988, ..., 1013, 1013, 1013],
       [1006,  983,  993, ..., 1013, 1013, 1013]], dtype=int16)
{% endhighlight %}


Final Thoughts
--------------

*Often the hardest thing is finding what you already have.*

Discovery and exploration are just as important as computation.  By extending
the Blaze's expression system to collections of datasets we create a smooth
user experience from first introductions to data all the way to analytic
queries and saving results.
