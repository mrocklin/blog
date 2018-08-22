---
layout: post
title: Funding Dask
category: work
draft: true
tags: [Programming, Python, scipy, dask]
theme: twitter
---
{% include JB/setup %}

Motivation
----------

This blogpost details how Dask developers receive funding to work on the
project.  This fulfills three goals

1.  **Transparency**: as a growing project within the numeric Python ecosystem
    we want to be open about how we sustain development.
2.  **Model for other projects**: other projects seeking funding may find some
    insight into what did and did not work for us
2.  **Solicit more funding**: this lays out a few tried-and-true ways to engage
    with core Dask developers.  Other possible funding sources (grants,
    companies) may find that they fit one of these situations.  If so, please
    get in touch :)

Summary
-------

Dask is funded from a variety of sources, each with very different objectives
and different ways of working.  Briefly, these include the following:

1.  General grants from government agencies (DOD) and philanthropic
    organizations (Moore foundation)
2.  Support contracts with companies, largely finance
3.  Feature buildout contracts with companies, again, largely finance
4.  Co-authored grants with scientific collaborators
4.  Continuum Analytics, the main employer of many of the Dask developers
5.  Community developers, either working on their own time (nights and
    weekends) as part of their studies, or as part of their jobs.

I have most visibility into topics 1-4, and so will focus on those.


Broadly Scoped Grants
---------------------

The Dask project is fortunate enough to be the recipient of generous grants
from the Moore foundation and the Department of Defense.  These typically have
broad mandates like "support open science" and "improve parallel dataframes and
machine learning", generally leaving the decision of what to focus on
day-to-day to developers.  Open ended grants like this are both incredibly
useful and somewhat dangerous.

**Benefits**:

1.  These were critical to get the project started and to the point where other
    funding sources became viable
2.  These continue to fill in gaps that no other funding source is willing to
    target because the need is diffuse.  Some examples:
    1.  Testing infrastructure
    2.  Monitoring the #dask tag on Stack Overflow
    3.  Answering user issues on GitHub
    4.  Collaborating with other core libraries (NumPy, pandas, Scikit-Learn)
        on the general future of the ecosystem

**Cons**:

1.  `<subjective>` Software developers need active guidance to ensure that their
    project is useful to domain users.  General grants are fairly hands-off and
    so it becomes tricky to ensure that you are satisfying them.  Too much
    freedom can be a bad thing without active feedback mechanisms.`</subjective>`

In practice we maintain a relationship with program managers and frequently ask
ourselves *"is this activity something that my program manager would support?"*
to help us decide where to apply these funds.

These can be anywhere from hundreds of thousands to low millions generally over
a couple years.


Contracts with Industry
-----------------------

At the other end of the spectrum of specificity are contracts with industry.
These typically come in two varieties:

1.  **Long term support:** we monitor several private issue trackers and
    respond to those issues with higher priority than other general questions
2.  **Short-term feature buildout:** we build specific features on request

### Long term support

Most current industry contracts are for general support.  This takes the form
of a private GitHub issue tracker where companies that are using Dask file
issues and have them handled quickly.  This has been incredibly valuable on
both sides.

**For companies**, they get a fast turnaround time on bugs and performance
issues, which lets them roll over speedbumps in a few hours or days rather than
waiting for a typical release cycle.  Companies using Dask are generally
building out some internal system with it, and it's useful to roll over
blocking points in a day rather than waiting for some future release.
Additionally in some cases companies seem to be paying for access and
anonymity.  At least in the finance sector many companies are unable to share
what technologies they use publicly, so a private issue tracker and the
occasional phone call to core developers gives them much more access than they
would otherwise have to ask questions and share design thoughts.  I suspect
that a few of our clients value the occasional phone call or visit more than
the bug handling.

**For Dask developers and the community**, the companies generally encounter
and pay to fix bugs and performance issues long before scientific or academic
users would encounter them.  Companies just use software in more extreme
conditions (larger scale, older versions, faster service requirements).  From a
maintainer's perspective companies are also ideal users.  They understand that
they're paying for time and so usually do an excellent job of describing their
problem succinctly and providing all relevant details (and often times
solutions).

These tend to be smaller contracts.  I typically bill 5-10 hours a week to one
client or another.  These relationships have non-monetary value as well in
providing deep insight into how Dask gets used in hard situations and informing
future design.

### Feature Buildout

Occasionally companies pay us money to build specific larger features.  This
tends to be a larger initial project, followed on by a slow-burn contract like
what is described above.

So far no one has wanted any significant feature set to be built privately.
Everyone has been entirely happy with contributing to open source.


### Consulting

Many of Continuum's general clients care far more about solving problems than
about building out technology.  Sometimes client-facing-developers within
Continuum use Dask just because it fits a client's problem well.  Often this
leads to a small bugfix or feature improvement.


Grants with Scientific Collaborators
------------------------------------

As Dask has grown, a variety of scientific collaborators have asked to
co-author grant applications that have a mix of scientific and technological
work.  For example *"Lets use Dask to scale out Python's array libraries
to analyze large scale climate simulations"*.

Together with scientific collaborators we identify both a scientific problem
and the technological hurdles that we need to overcome to solve that problem.
This pushes the project forward, creates a tight feedback cycle with a core set
of scientific users, and accomplishes novel scientific goals at the same time.

These grants tend to be from the same sources as before, government and
philanthropic organizations, but now we open up possibilities with more
agencies that generally expect academic collaborators like the US National
Science Foundation (NSF) and National Institutes of Health (NIH).

These tend to be in the hundreds of thousands to low millions of dollars, split
among a few institutions and spanning a couple of years.  We have a few of
these in flight, though none have yet landed.


Continuum Analytics
-------------------

Most of the core Dask developers are employed by Continuum Analytics, a
for-profit company within the open source numeric Python ecosystem (although
half of the Continuum-paid Dask developers had commit-rights on Dask before
Continuum hired them).

In addition to facilitating the contracts and grants listed above, Continuum
also funds Dask development through a couple of mechanisms:

1.  Continuum's **community innovation** group uses profit from the consulting
    side of the company to fund projects that improve the health and
    competitiveness of the Anaconda Python stack generally.
2.  Continuum's **Anaconda platform** group sometimes needs things that fall
    within our scope and funds the work directly.


### Community Innovation

When your company pays Continuum money, some fraction of that goes towards
improving the ecosystem.  Continuum is probably the entity that is the most
financially vested in the long-term health of the Python data-science
ecosystem.  As a result even entirely greedy actions are often for the general
good.  Dask, as a decent solution to parallelize the existing Python stack for "Big
Data", benefits from this.

### Anaconda Platform

Continuum also sells the Anaconda Platform, proprietary software to help manage
data science teams.  Sometimes problems arise in the platform that are well
suited to the open source developer teams.  For example the
[fastparquet](http://fastparquet.readthedocs.io/en/latest/) reader for the
Apache Parquet file format was funded by the platform.

### Stability, and funding source of last resort

Continuum-paid Dask developers prefer to bill to clients or grants when
possible.  However client and grant work can be sporadic or sometimes tasks
arise that are important, but do not fall under the scope of any paid project.
In these cases having the backing of a solid company provides security both for
the project and for the developers.


General Thoughts
================

Mixing is Good
--------------

The mix of funding sources above is good for a few reasons:

1.  It makes us robust to the whims of a particular funding source.
    Any of Continuum/DoD/Finance/Philanthropy can fail and Dask will continue
    to grow and evolve.
2.  The mix of both specific and general funding sources helps us to both grow
    and maintain the project in a healthy balance
3.  It is satisfying to see the kickstart from general grants incite follow-on
    grants from other agencies, showing a path to sustainability from public
    sources

Funding Open Source
-------------------

I've enjoyed thinking about funding Dask over the last year.

Thinking about how to sell a software project, either to a morally ambiguous
finance company or to an altruistic philanthropic organization, forces you to
acknowledge the needs of others, which in turn connects you to the greater
world and helps you to prioritize your software development.  I find myself
thinking less about beautiful software, and more about software that is of use
to others.

Additionally as the open source software community considers sustainability
this practice of seeking out funding will be, I think, increasingly critical.
I would not have expected this to be part of my job two years ago, however it
has been very rewarding and somewhat fruitful.  I encourage others to think
about how to make their software useful to people willing to pay for its
development.

There is a lot of money out there for general software development *if* you can
connect your software to active and ongoing applications.  Performing this
connection to applications is critical both to securing funding and to ensuring
that you work on relevant solutions.


