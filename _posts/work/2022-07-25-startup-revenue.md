---
layout: post
title: Startup Revenue
tagline:
category: work
tags: []
theme: twitter
---
{% include JB/setup %}

VC funded startups are weird.
They (rightly) care more about valuation than about revenue.
Valuation depends on revenue, but only on very certain kinds of revenue.

The simplified version of this is that there are two kinds of revenue:

1.  **Services (bad)** one-off consulting work that is easy to get but has little to do with making a scalable business
2.  **Recurring Product Revenue (good)** annually recurring revenue with little to no marginal cost and great scalability

I agree with this assessment, but I think that it over-simplifies things a bit.
This blog goes through a variety of different kinds of revenue that I think are
different kinds of good and bad.  Throughout these examples I draw from on my
single experience selling open source software in the data infrastructure space.


## Consulting Services

*Customer: Please join my team and help us use your software to solve our problem*

-   Not Scalable
-   Not Dependable
-   Maybe informs future product development

I think that this activity is actually great when you're starting out.
There's no better way to understand customer pain points than figuring out what
they're willing to pay for and working closely with them.

Of course, one needs to be careful that we're learning from this experience,
rather than just chasing money (although that's ok too if you're doing it
intentionally).

Typically these contracts are hourly.  I've seen rates anywhere from *$150/hr* to
*$1000/hr*.


## Funded Development

*Customer: I love your software.  Can I pay you to add a feature?*

-   Not scalable
-   Not dependable
-   Supports product development

This work is probably great.  Someone cares enough about your software to pay
you to improve it.  They don't want you mucking about in their systems
(awesome) but do want to prioritize things on your roadmap a bit.  This can be
either good signal (customers pointing you in the right direction) or
distracting (customers pointing you in a bad direction).  Additionally, because
this work isn't very dependable it's hard to build a team around it (at least
not a team that needs to be dependably employed)

Typically these are one-off fixed-price contracts.  I've seen contracts from
*$50,000* to *$1,000,000*.



## Support

*Customer: I want insurance that things won't break*

-   Pretty Scalable
-   Pretty Dependable
-   Kinda supports product development

Once your software is endemic within an organization they're going to want
someone to be on the hook for it.  We do this by providing a private issue
tracker, SLAs on critical bugs, and a person to talk to from time to time.  We
also offer things that no one uses like indemnity insurance.

The beautiful thing here is that if your software works perfectly then this is
free to provide.  Your software doesn't work perfectly, so this isn't free, but
fortunately all of these customers typically ask for the same things, so it
scales pretty well.  It's also pretty dependable, so it's easy to hire people
and rest assured that you can continue to employ them.

For enterprise customers these are typically anywhere from *$100,000* to
*$1,000,000*, at least at the Series Seed/A size.  Multi-million dollar deals of
this nature are doable between larger companies.  I typically have to convince
business people that this is ARR, despite the fact that it's definitely
annually recurring revenue.


## Product (hard to deploy)

*Customer: I want your product, but need it in my environment, like Cloudera*

-   Pretty Scalable
-   Very Dependable
-   Supports product development (but painfully)

Hooray product revenue!  This is the first thing that you don't have to
convince VCs to count as ARR.  It might actually still be a pain in the butt
though.

Products are often hard to deploy within customer settings.  Big customers have
lots of custom systems that are hard to work with, and you'll be asked to work
with them.  That's ok, you can hire a team that just does this work and you can
charge for their time.  There are other challenges, like supporting old
versions of the software, getting clear bug reports on your software when you
may not have permissions to touch that software directly, etc..

Fortunatley though, the world has also improved since the days of Cloudera.
Technologies like Kubernetes and "on-prem cloud" reduce (but don't eliminate)
this pain.


## Product (cloud SaaS)

*Customer: I want your product, and don't mind if you see my data, like Snowflake*

-   Very Scalable
-   Dependable
-   Supports product development (and joyfully)

Hooray product revenue attached to a system over which you have full visibility!
Cloud SaaS is considered to be the highest velocity approach because once it
works it's easy to scale out to lots of customers with low effort.  Of course,
it may be *really* hard to get to that point.  You'll have to get good at
convincing customers that your internal systems are safe.  This will be easy in
some sectors (SMBs, non-sensitive industries) but harder in others (Large
Enterprise, finance, government, etc.).


## Summary

Money is good.  Dependability is good.  Learning is good.

All of these activities are good in some ways and bad in others.  Rather than
say services are bad and product is good we should be asking questions about
how scalable, dependable, high margin, and in line with your product
development they are.
