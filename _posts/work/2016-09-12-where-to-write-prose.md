---
layout: post
title: Where to Write Prose?
category: work
tags: [Programming, Python, scipy]
theme: twitter
---
{% include JB/setup %}

*Code is only as good as its prose.*

Like many programmers I spend more time writing prose than code.  This is
great; writing clean prose focuses my thoughts during design and disseminates
understanding so that people see how a project can benefit them.

However, I'm now confused about how and where I should write and publish prose.
When communicating to users there are generally three options:

1.  Blogposts
2.  Documentation

Given that my time is finite I need to strike some balance between these two
activities.  I used to blog frequently, then I switched to documentation, and I
think I'm probably about to swing back a bit.  Here's why:


Blogposts
---------

Blogposts excel at generating interest, informing people of new functionality,
and providing workable examples that people can copy and modify.  I used to
blog about Dask (my current software project) pretty regularly here on my blog
and continuously got positive feedback from it.

However, blogging about evolving software also generates debt.  Such blogs grow
stale and inaccurate and so when they're the only source of information about a
project users grow confused as things they try no longer work, and they're
stuck without a clear place to turn.  Basing core understanding on blogs can be
a frustrating experience.


Documentation
-------------

So I switched from writing blogposts to spending a lot of time writing
technical documentation.  This was a positive move.  User comprehension seemed
to increase, the questions I was fielding were of a far higher level than
before.

Documentation gets updated as features mature.  New pages assimilate cleanly
and obsolete pages get cleaned up.  Documentation is generally more densely
linked than linear blogs, and readers tend to explore more deeply within the
website.  Comparing the Google Analytics results for my blog and my documentation
show significantly increased engagement, both with longer page views as well as
longer chains of navigation throughout the site.  Documentation seems to engage
readers more strongly than do blogs (at least more strongly than my blog).

However, documentation doesn't get in front of people the same way Blogs do.
No one subscribes to receive documentation updates.  Doc pages for new
features rarely end up on Reddit or Hacker News.  The way people pass around
blog links encourages Google to point people there way more often than to doc
pages.  There is no way for interested users to keep up with the latest news
except by subscribing to fairly dry release e-mails.

Blogposts are way sexier.  This feels a little shallow if you're not into sales
and marketing, but lets remember that software dies without users and that
users are busy people who have to be stimulated into taking the time to learn
new things.


Current Plan
------------

I still intend to focus 80% of my time on documentation, especially for new or
in-flux features that haven't had a decent amount of time for users to provide
feedback.

However I hope to blog more about concepts or timely experiences that have to
do with development, but probably not about the features I'm developing just
this minute.  For example, right now I'm building a Mesos-powered Scheduler
for Dask.distributed.  I'll probably write about the experiences of a
developer meeting Mesos for the first time, but I probably won't
include a how-to of using Dask with Mesos.

I also hope to find some way to polish existing doc pages into blogposts once
they have proven to be fairly stable.  This mostly involves finding a
meaningful and reproducible example to work through.


Feedback
--------

I would love to hear how other projects handle this tension between timely and
timeless documentation.
