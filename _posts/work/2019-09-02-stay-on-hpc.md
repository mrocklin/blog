---
layout: post
title: Reasons to keep your on-site HPC center
tagline: and avoid the cloud
category: work
draft: true
tags: []
theme: twitter
---
{% include JB/setup %}

Scientific institutions today are considering how to balance their current HPC
infrastructure with a possible transition to commerical cloud.

This transition is partially motivated by data science users,
who find that HPC policies make their workflows difficult.
This frustration is reasonable.
HPC systems weren't designed around these use cases,
but there are steps we can take to adapt HPC centers for data science use.

But should we bother?
Why might an institution choose to adopt cloud,
and why might they choose to stay with in-house HPC resources?
Some colleagues of mine recently published
[an opinion paper supporting a move to cloud](https://arxiv.org/abs/1908.03356?),
so I thought I would respond with some arguments in the other direction.

*To be clear, I support a move to cloud in many cases, as they would support
staying on in-house HPC.  There is no single right answer.*

With that prelude out of the way, here are some reasons:

1.  **You already have an in-house HPC center** so you might as well use it.
    Adopting a technology is easy, but changing the behaviors of an institution
    is a multi-year effort that is going to be more intense than you expect.
    Even very nimble for-profit companies have a hard time at this, and if you
    have an in-house HPC center, then you are probably an organization with
    considerable inertia.

2.  **Your data may be generated in-house** if you're running
    simulations or making local observations then you might have data
    generation on-premises.  If these datasets are likely to be reused many
    times by an entire field then *please* place them onto the cloud (this is
    what it is best at), however if your users are each creating their own
    large datasets that have only ephemeral value, then it may not make sense
    to publish these to the cloud, so you will want to support in-house
    computation instead.

    To recap:

    1.  A few long-lived datasets serve a large community: Cloud
    2.  Everyone makes their own short-lived datasets: In-house

3.  **Hiring**: the cloud is a new technology. Actually, it's a whole new suite
    of new technologies, and people who understand these well are in high demand
    by well-paying employers.  If you have difficulty meeting market rates,
    then please verify that you'll be able to hire or retrain experienced
    people before making this decision.

4.  **User familiarity**: In some ways HPC systems are more familiar to scientific
    users today than cloud environments.  For example when you move to the
    cloud you often lose things like POSIX file systems, file formats like HDF,
    and more.  In the long run this is fine, there are excellent alternatives
    to these technologies, but a lot of user code will have to change a bit.

5.  **Lockin**:  The clouds will sell you products that are highly productive,
    but will make it difficult for you to leave them in the future.  They will
    make it very easy to adopt tooling that differentiates them from other
    vendors and that you will, in time, rely upon heavily so that your public
    institution becomes a little bit of a captive.  This happens with on-site
    HPC machines and software too, but it's a bit more prevalent in the cloud.

    Arguably, it's good for government funded public institutions to maintain
    some level of independence from commercial cloud.
