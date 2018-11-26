---
layout: post
title: "Joining NVidia"
category: work
tags: []
theme: twitter
---

{% include JB/setup %}

## Summary

I left employment at Anaconda Inc. last week.
I start employment at NVIDIA next month.
Surprisingly little will change.


## History

Four and a half years ago, Anaconda Inc (then Continuum Analytics) was kind
enough to hire me to work on open source software to help scale the PyData
ecosystem.

I spent most of that time developing [Dask](https://dask.org), a Python-native
library for scalable computing, as well as working with the broader Numeric
Python community to scale their workloads to multi-core and distributed
systems.


## Thank you Continuum/Anaconda

This has been a tremendously satisfying experience.  It has been intellectually
stimulating work, and I feel that I've had a positive social impact, both on
the numeric Python community (Python now feels like a reasonable place to do
scalable analytics) and more importantly on a number of humanitarian issues
that are important to me like climate change, human health, civic data
analysis, and so on.  I've also had the opportunity to engage with stakeholders
in other software projects, small companies, large companies, government
agencies, non-profit foundations and so forth; these interactions have helped
me to become more effective in advocating and integrating open source software
into the broader world.

Finally, this experience has been satisfying because I feel that I've helped
others to form a community.  There is a wonderful community of people who work
on and use Dask around the world within a great variety of different domains.
Seeing bonds form and ideas flow between these groups has been wonderful, and I
hope that these interactions will have cascading effects.  This group
accomplishes more than I ever could have both because many of them are better
programmers than I am, and because their range of perspectives provides much
better coverage of the space.  Somehow, I still seem to get credit for things
:)

Starting this process was only possible because I was employed to do it as a
full-time job, so thank you Continuum/Anaconda for the opportunity to pursue
this work.


## Change is good

I joined Anaconda after quitting a postdoc position that, while fine, gave me
none of the satisfaction above.  After quitting I realized

**"Hey, I should quit things more often!"**

It's good to change context and get a fresh perspective from time to time.
Changing jobs is a great way to do that, especially if the new job knows
something that you don't.


## Starting at NVIDIA

I'll be joining the AI Infrastructure division at NVIDIA, and the
[Rapids](https://rapids.ai/) group in particular.

Not much will change about my job and day-to-day activities.  I will continue
to focus on general open source Dask development and maintenance.  What will
change though is that hopefully we'll get several more people to start
developing and maintaining the project into the future.  NVIDIA is using Dask
to provide scalability within their data analytics tool suite, Rapids (more
down below), and so they want to ensure that the Dask project grows quickly.

We should expect the Dask+GPU experience will improve significantly (it's
usable now, but there's plenty of room for improvement), but we shouldn't
expect Dask to become GPU-specific.  This was one of the first concerns I
raised with NVIDIA management, and they quickly agreed that they didn't want to
go in that direction.  Their objective is to make it as easy as possible
for PyData-Dask-CPU users to become PyData-Dask-GPU users without noticing the
change, and as a result they seem fully committed to investing in an
improved Dask experience overall.


## What will Anaconda do?

Anaconda fully supports this move.  They're excited about the growth of the
project beyond their institution and the opportunities that this change brings
to the broader community.  Anaconda will continue to develop and support the
Dask project for the foreseeable future.

I'm looking forward to continuing interactions with the current core Dask
developers at Anaconda, who do more work on the project than I do these days.
Fortunately, because the OSS interactions at Anaconda have always been out in
the open there's actually very little change to how we operate as a larger
group except that, again, there will be more of us :)


## Why does NVIDIA want to invest in Dask?

NVIDIA wants to expand the adoption of GPUs in data science.
They believe that Dask can help them with that goal.

The rise of general purpose GPU computing and the recent explosion of deep
learning have driven interest in GPUs in recent years.
GPUs provide multiple orders of magnitude performance increases on many
computational problems *when they are used correctly*.  Unfortunately, using a
GPU correctly is a challenging task even for most computer scientists who are
trained in their use.  GPUs are generally not accessible today to the
majority of people doing computing who do not have extensive GPU programming
experience.

Deep learning libraries like Tensorflow, PyTorch, CuPy/Chainer, and Keras are
notable exceptions.  They provide high-level APIs that allow modestly skilled
Python programmers to use GPUs for the particular domain of array computing.
This approach of connecting a high-level API to efficient low-level code is a
familiar one in the Python ecosystem.  Most of our popular libraries do the
same.  We can probably repeat this experience for other applications.

[Rapids](https://rapids.ai/) is an initiative within NVIDIA to expand the use
of GPUs beyond just deep learning to broader data science applications.  They
want to create several new libraries that provide high-level Python APIs to
low-level GPU code.  They started with [cuDF](https://github.com/rapidsai/cudf)
a clone of a subset of the Pandas API, and are looking to do this with other
libraries as well.

To scale these libraries, they will use Dask.  Dask provides all of
necessary features for scaling (networking, resilience, scheduling, etc..)
without being opinionated on what kinds of computations are done on each node,
which makes it a nice fit when building out a new scalable computing stack.
Additionally, because Dask already has connections to many of the existing
Python libraries (Pandas, Scikit-Learn, etc..) it's easy to port a large subset
of that functionality over to Rapids.

Finally, Dask is a semi-successful example of transitioning a community to use
a new hardware architecture with minimal fuss (single-threaded -> parallel).
Presumably there is something to learn culturally as well as NVIDIA tries to
introduce GPUs to a broader set of high-level computing workflows.


## Future Work

Again, because Dask is already developed by people from many institutions (less
than half of the core committers work at Anaconda) most of the day-to-day
activities remain the same.  However, now that there are a few sizable
corporations making significant investments we may want to solidify some
community structures:

1.  We should start conversations around applying for NumFOCUS fiscal
    sponsorship, which will require us to formalize a variety of governance
    requirements that we should have done long ago (code of conduct, steering
    council, etc..)

2.  We may establish more communication mechanisms, including perhaps regular
    monthly meetings, a mailing list for project announcements, and so on.

3.  NVIDIA management and I will work on laying out a plan for near-term work
    on their end. This will probably occur a month or two after I start
    employment there.


## Hiring

Finally, both Anaconda and NVIDIA are currently hiring developers to work on
Dask.  Come join, there's plenty to do.

Edit: Anaconda Inc. has a [Dask-related job posting here](https://boards.greenhouse.io/anaconda/jobs/1396688).
