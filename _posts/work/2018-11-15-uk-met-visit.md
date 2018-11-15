---
layout: post
title: Anatomy of an OSS Institutional Visit
category: work
draft: true
tags: [Programming, Python, scipy, dask]
theme: twitter
---
{% include JB/setup %}

I recently visited the UK Meteorology office, a moderately large organization
that serves the weather and climate forecasting needs of the UK (and several
other nations).  I was there with other open source colleagues including [Joe
Hamman](https://joehamman.com/) and
[Ryan May](https://dopplershift.github.io/) from
open source tools like
[Dask](https://dask.org),
[Xarray](https://xarray.pydata.org),
[JupyterHub](https://jupyterhub.readthedocs.io/en/stable/),
[MetPy](https://unidata.github.io/MetPy/latest/),
[Cartopy](https://scitools.org.uk/cartopy/docs/v0.16/),
and the broader [Pangeo community](https://pangeo.io).

This visit was like many other visits I've had over the years that are centered
around showing open source tooling to large institutions, so I thought I'd
write about it in hopes that it helps other people in this situation in the
future.

My goals for these visits are the following:

1.  Teach the institution about software projects and approaches that may help
    them to have a more positive impact on the world
2.  Engage them in those software projects and hopefully spread around the
    maintenance and feature development burden a bit


## Step 1: Meet allies on the ground

We were invited by early adopters within the institution, both within the UK
Met office's [Informatics Lab](https://www.informaticslab.co.uk/) a research /
incubation group within the broader organization, and the Analysis,
Visualization, and Data group (AVD) who serve 500 analysts at the office with
their suite of open source tooling.

Both of these groups are forward thinking, already use and appreciate the tools
that we were talking about, and hope to use us to evangelize what they've
already been saying throughout the company.  They need outside experts to
provide external validation within the company; that's our job.

The goals for the early adopters are the following:

1.  Reinforce the message they've already been saying internally, that these
    tools and approaches can improve operations within the institution
2.  Discuss specific challenges that they've been having with the software
    directly with maintainers
3.  Design future approaches within their more forward thinking groups

So our visit was split between meeting a variety of groups within the
institution (analysts, IT, ...) and talking shop.


## Step 2: Talk to IT

One of our first visits was a discussion with a cross-department team of people
architecting a variety of data processing systems throughout the company.  [Joe
Hamman](https://joehamman.com/) and I gave a quick talk about Dask, XArray, and the
Pangeo community.  Because this was more of an IT-focused group I went
first, answered the standard onslaught of IT-related questions about Dask, and
established credibility.  Then Joe took over and demonstrated the practical
relevance of the approach from their users' perspective.

We've done this tag-team approach a number of times and its always effective.
Having a technical person speak to technical concerns while also having a
scientist demonstrating organizational value seems to establish credibility
across a wide range of people.

However it's still important to tailor the message to the group at hand.
IT-focused groups like this one are usually quite conservative about adding new
technology, and they have a constant pressure of users asking them for things
that will generally cause problems.  We chose to start with low-level technical
details because it lets them engage with the problem at a level that they can
meaningfully test and assess the situation.


## Step 3: Give a talk to a broader audience

Our early-adopter allies had also arranged a tech-talk with a wider audience
across the office.  This was part of a normal lecture series, so we had a large
crowd, along with a video recording within the institution for future viewers.
The audience this time was a combination of analysts (users of our software),
some IT, and an executive or two.

Joe and I gave essentially the same talk, but this time we reversed the order,
focusing first on the scientific objectives, and then following up with a more
brief summary on how the software accomplishes this.  A pretty constant message
in this talk was ...

> other institutions like yours already do this and are seeing transformative change

We provided social proof by showing that lots of other popular projects
and developer communities integrate with these tools, and that many large
government organizations (peers to the UK met office) are already adopting
these tools and seeing efficiency gains.

Our goals for this section are the following:

1.  Encourage the users within the audience to apply pressure to their
    management/IT to make it easier for them to integrate these tools to their
    everyday workflow
2.  Convince management that this is a good approach.

    This means two things for them:

    1.  These methods are well established outside of the institution,
        and not just something that their engineers are enamored with short-term
    2.  These methods can enable transformative change within the organization


## Step 4: Talk to many smaller groups

After we gave the talk to the larger audience we met with many smaller groups.
These were groups that managed the HPC systems, were in charge of storing data
on the cloud, ran periodic data processing pipelines, etc..  Doing this after
the major talk is useful, because people arrive with a pretty good sense of
what the software does, and how it might help them.  Conversations then become
more specific quickly.


## Step 5: Engage with possible maintainers

During this process I had the good fortune to work with [Peter
Killick](https://github.com/dkillick) and [Bill
Little](https://github.com/bjlittle) who had done a bit of work on Dask in the
past and were interested in doing more.  Before coming to the office we found a
bug that was of relevance to them, but also involved learning some more Dask
skills.  We worked on it off and on during the visit and it was great to get to
know them better and hopefully they're more likely to fix issues that arise in
the future with more familiarity.


## Step 6: Make technical plans

There was good conversation around the future relationship between
[Xarray](https://xarray.pydata.org) and
[Iris](https://scitools.org.uk/iris/docs/latest/) two similar packages that
could play better together, the popular
[Cartopy](https://scitools.org.uk/cartopy/) library ([Ryan
May](http://dopplershift.github.io/) was visiting at the same time),
and some very early stage prototypes of a library for unstructured meshes.


## Step 7: Have a good time

It turns out that the Southwest corner of England is full of fine pubs, and
even better walking.  I'm thankful to [Phil Elson](https://pelson.github.io/)
and Jo Camp for hosting me over the weekend where we succeeded in chatting
about things other than work.

<img src="{{ BASE_PATH }}/images/sw-england.jpg" width="50%">

<img src="{{ BASE_PATH }}/images/uk-met-pub.jpg" width="50%">
