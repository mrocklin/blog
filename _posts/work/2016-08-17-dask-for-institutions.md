---
layout: post
title: Dask for Institutions
draft: true
category: work
tags: [Programming, scipy, Python, dask]
theme: twitter
---
{% include JB/setup %}

tl;dr
-----



Instititions use software differently than individuals.  Over the last few
months I've had dozens of conversations about using Dask within larger
organizations, like universities, research labs, private companies, and
non-profit learning systems.  This post provides a very coarse summary of those
conversations and extracts common questions.  I'll then try to answer those
questions.

*Note: some of this post will be necessarily vague at points.  Some companies
prefer privacy.  All details here are either in public Dask issues or have come
up with enough institutions (say at least five, one of them public) that I'm
comfortable listing the problem here.*


### Common story

Institition X, a university/research lab/company/... has many
scientists/analysts/modelers who develop models and analyze data with Python,
the PyData stack like NumPy/Pandas/SKLearn, and a large amount of custom code.
These models/data sometimes grow to be large enough to need a moderately large
amount of parallel computing.

Fortunately, Institution X has an in-house cluster acquired for exactly this
purpose of accelerating modeling and analysis of large computations and
datasets.  Users can submit jobs to the cluster using a job scheduler like
SGE/LSF/Mesos/Other.

However the cluster is still under-utilized and the users are still asking for
help with parallel computing.  Either users aren't comfortable using the
SGE/LSF/Mesos/Other interface or the interaction times aren't good enough for
the interactive use that users appreciate.

There was an internal effort to build a more interactive and Pythonic system on
top of SGE/LSF/Mesos/Other but it's not particularly mature and definitely
isn't something that Institution X wants to pursue.  It turned out to be a
harder problem than expected to design/build/maintain such a system in house.
They'd love to find an open source solution that was well featured and
maintained by a community.

The Dask.distributed scheduler looks like it's 90% of the system that
Institution X needs.  However there are a few open questions:

*  How do we integrate dask.distributed with SGE/LSF/Mesos/Other?
*  How can we grow and shrink the cluster dynamically based on use?
*  How do users manage software environments on the workers?
*  How secure is the distributed scheduler?
*  Dask is resilient to worker failure, how about scheduler failure?
*  What happens if ``dask-worker``s are in two different data centers?  Can we
   scale in an asymmetric way?
*  How do we handle multiple concurrent users and priorities?
*  How does this compare with Spark?

So for the rest of this post I'm going to answer these questions.  As usual,
not all answers will be of the form "Yes Dask can solve all of your problems"
but will instead get into what's possible today and how we might solve this
problem in the future.


### How do we integrate dask.distributed with SGE/LSF/Mesos/Other?

It's not difficult to deploy dask.distributed at scale within an existing
cluster using a tool like SGE/LSF/Mesos/Other.  In many cases there is already
a researcher within the institution doing this manually by running
`dask-scheduler` on some static node in the cluster and launching `dask-worker`
a few hundred times with their job scheduler and a small job script.

The goal now is how to formalize this process for the individual version of
SGE/LSF/Mesos/Other used within the institution while also developing and
maintaining a standard Pythonic interface so that all of these tools can be
maintained cheaply by Dask developers into the forseeable future.  In some
cases Institution X is happy to pay for the development of a convenient "start
dask on my job scheduler" tool, but they are less excited about paying to
maintain it forever.

We want Python users to be able to say something like the following:

```python
from dask.distributed import Executor, SGECluster

c = SGECluster(nworkers=200, **options)
e = Executor(c)
```

and have this same interface be standardized across different job schedulers.


### How can we grow and shrink the cluster dynamically based on use?

Alternatively, we could have a single dask.distributed deployment running 24/7
that scales itself up and down depending on current load.  Again, this is
entirely possible today if you want to do it manually (you can add and remove
workers on the fly) but we should add some signals to the scheduler like "I'm
under duress, please add workers" or "I've been idling for a while, please
reclaim some workers" and connect these signals to a manager that talks to the
job schduler.


### How do users manage software environments on the workers?

Today Dask assumes that all users and workers share the exact same software
environment.  There are some small tools to send updated `.py` and `.egg` files
to the workers but that's it.

Generally Dask trusts that the full software environment will be handled by
something else.  This might be a network file system (NFS) mount on traditional
cluster setups, or it might be handled by moving conda environments around by
some other tool like [knit](http://knit.readthedocs.io/en/latest/) for YARN
deployments or something more custom.  Continuum for example sells [proprietary
software](https://docs.continuum.io/anaconda-cluster/) that does this.

Getting the standard software environment setup generally isn't such a big deal
for institutions.  They typically have some system in place to handle this
already.  Where things become interesting is when users want to use
drastically different environments from the system environment, like using Python
2 vs Python 3 or installing a bleeding-edge scikit-learn version.  They may
also want to change the software environment many times in a single session.

The best solution I can think of here is to pass around fully downloaded conda
environments using the dask.distributed network (it's good at moving large
binary blobs throughout the network) and then teaching the `dask-worker`s to
bootstrap themselves within this environment.  We should be able to tear
everything down and restart things within a small number of seconds.  This
requires some work; first to make relocatable conda binaries (which is usually
fine but is not always fool-proof) and then to help the dask-workers learn to
bootstrap themselves.

Somewhat related, Hussain Sultan of Capital One recently contributed a
``dask-submit`` command to run scripts on the cluster:
http://distributed.readthedocs.io/en/latest/submitting-applications.html


### How secure is the distributed scheduler?

Dask.distributed is incredibly insecure.  It allows anyone with network access
to the scheduler to execute arbitrary code in an unprotected environment.  Data
is sent in the clear.  Any malicious actor can both steal your secrets and then
cripple your cluster.

However, this is entirely the norm.  Security is usually handled by other
services.

As with software environments we generally rely on other technologies like
Docker to isolate workers from destroying their surrounding environment and
network access controls to protect data access.

Because we're on Tornado, a serious networking library and web framework there
are some things we can do easily like enabling SSL, authentication, etc..
However I hesitate to jump into providing "just a little bit of security"
without going all the way for fear of providing a false sense of security.

In short, I have no plans to work on this without a lot of encouragement.  Even
then I would strongly recommend that institutions couple Dask with tools
intended for security.  I believe that is common practice for many other
distributed systems as well.


### Dask is resilient to worker failure, how about scheduler failure?

Workers can come and go.  Clients can come and go.  The state in the scheduler
is currently irreplacable and no attempt is made to back it up.  There are a
few things you could imagine here:

1.  Log state and recent events to some persistent storage so that state can be
    recovered in case of loss
2.  Having a hot failover node that gets a copy of every action that the
    scheduler takes
3.  Have multiple peer schedulers operate simultaneously in a way that they can
    pick up slack from lost peers
4.  Have clients remember what they have submitted and resubmit when a
    scheduler comes back online

To be clear, none of these solutions exist.  Option 4 is currently the most
feasible.  Option 2 or 3 would probably be necessary if Dask were to ever run
as critical infrastructure in a giant institution.  We're not there yet.

As of [recent work](https://github.com/dask/distributed/pull/413) spurred on by
Stefan Van der walt at UC Berkeley BIDS the scheduler can now die and come back
and everyone will reconnect, but the state of the computations in flight is
entirely lost.



