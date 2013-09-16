---
layout: post
title:  How I Test Python
tagline:  a few of my favorite tools
category : work 
tags : [Python]
---
{% include JB/setup %}

For my recent projects [`itertoolz`](http://github.com/pytoolz/itertoolz/) and [`functoolz`](http://github.com/pytoolz/functoolz) I've decided to simultaneously support Python 2.x and 3.x with a single codebase.  This is after a number of other projects (including SymPy) have demonstrated the feasibility of this approach.  

I thought I'd share how I now set up my testing environment for these projects as they include a few of my favorite utilities.

`nosetests`
-----------

First, `nosetests`.  I think most readers of my blog (both of you) are familiar with `nosetests` so I'll be brief here.  Nosetests reads through my directory, finds all files named `test_X.py`, runs all functions they contain named `test_X()`, and reports all encountered assertion errors.  

It's a simple solution that does exactly one thing and does it well.

`conttest`
----------

Lesser known is the `conttest` tool, written by [@eigenhombre](http://github.com/eigenhombre/).  `conttest` allows me to run my tests every time I save a file in my workspace.  Actually it allows me to run any command on the command line each time my directory changes.  It can be composed with nosetests like so 

    conttest nosetests

I run this in a separate window and keep an eye on it to make sure I don't introduce errors each time I save.  This only works with files for which the tests are cheap (as most good tests are).  Actually I usually use it as follows

    conttest "clear && nosetests --with-doctest"

I really respect conttest because it actually has nothing to do with testing.  It, like nosetests, does one and only one thing well without reaching for more.  It composes well with other tools, like nosetests, to great effect.

Conttest is available on the PyPI and so is pip/easy_installable

    pip install conttest

`conda`
-------

The combined Python 2.x 3.x (I'm calling this Python "twenty-three") source code means that I need to simultaneously run two testing systems, one running 2.7 and one running 3.3.  I manage this with conda.  First, I create two environments; this only needs to be done once on each system

    conda create -n py33 python=3.3 anaconda
    conda create -n py27 python=2.7 anaconda

This takes a while to set up but does a wonderful job creating two completely independent, self-consistent, and fully dependable virtual environments.  I can switch to either with

    source activate py33  # Use Python 3.3
    source activate py27  # Use Python 2.7

All Together
------------

So when I start work I set up something like this

    # Terminal 1
    source activate py33
    conttest "clear && nosetests --with-doctest"
    
    # Terminal 2
    source activate py27
    conttest "clear && nosetests --with-doctest"

    # Terminal 3
    # Do actual work
