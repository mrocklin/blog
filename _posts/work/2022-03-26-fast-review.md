---
layout: post
title: Small Scope and Fast Review
tagline: The secret to happy devs
category: work
tags: []
theme: twitter
---
{% include JB/setup %}

This is a [fast blogpost](https://matthewrocklin.com/blog/work/2019/06/25/write-short-blogposts) please excuse the brevity.

Summary
-------

-   A fast review and merge cycle is incredibly valuable
-   When reviewing, consider highlighting which comments are obligatory because
    they stop some regression, and which are merely commendable because they
    would add some enhancement
-   Don't forget that better is the enemy of good, especially when prioritizing
    against all of the other work that can get done.


Example
-------

As an OSS developer I use many projects, and when I see a simple problem in a project that I can fix quickly, I like to fix it.
For a trivial example, maybe I decide to add a type annotation to a function:


```diff
-def ensure_bytes(s):
+def ensure_bytes(s) -> bytes:
     """Turn string or bytes to bytes

     >>> ensure_bytes('123')
    b"123"
```

Awesome.  This takes me less than two minutes to make the fix and open a pull
request.  I can fire this off and proceed with my normal work.

## Critical review

On review, someone might helpfully mention that I actually made a mistake, and
that this function can also return `None` in some cases.  They make the
following suggestion:

```diff
-def ensure_bytes(s):
+def ensure_bytes(s) -> bytes | None:
     """Turn string or bytes to bytes

     >>> ensure_bytes('123')
    b"123"
```

This is great!  They helped me to understand the problem better, and avoid
doing something harmful to the project.  The back-and-forth here takes a few
minutes, and pushing a new commit takes a few minutes, but I'm still happy to
do this, and I learned something along the way.  I'm not thrilled about
stopping my normal work to do this, but it makes total sense.  We need to
make sure that things are correct.

## Non-critical review

Another reviewer then arrives and suggests that I also type the inputs, and
change the docstring to reflect the ambiguous typing.

```diff
-def ensure_bytes(s):
+def ensure_bytes(s: str | bytes | None) -> bytes | None:
     """Turn string or bytes to bytes

     Except if the input is none, in which case it passes through

     >>> ensure_bytes('123')
    b"123"
```

This is a good idea!  Someone should do this!  However, I don't think that it
necessarily has to be me.  Also, I'm off doing other work, and this is becoming
more of a distraction.

Maybe I do this anyway (it's not hard) but I'm probably less likely to come back here in the future.

## Distinguish between critical bugs and nice-to-have enhancements

It's great to make suggestions on PRs for enhancements or how things might be
improved.  However, we should always remember to mark them as optional for PR
authors.

We can always come back and add the enhancements ourselves after their
improvements are already in.

## Prioritize ruthlessly

However, when we switch out of review mode, and into authoring mode, we might
realize that the enhancements aren't actually as important as what we were
planning to work on.  If they're not something that we're likely to prioritize
ourselves, then we definitely shouldn't have been requiring someone else to do
this work for us.

This is especially true in a professional context, where time is in short
supply.  Many of us come from a volunteer context, where working on code and
reviewing is a free thing that we ourselves donate or that we do for fun.
However, in a professional context this is often not true, and the
back-and-forth on a PR has very concrete costs (easily rising into the
thousands of dollars).  At work we prioritize with our teams to make sure that
we're using our time wisely, but we often forget about this prioritization
process when we enter review mode.


## Parable

Imagine that you need to travel from home into the city.  It's a long distance but
a beautiful day outside, and so you decide to walk.  You're moving quickly so
that you can get there and back before sunset.

You start walking swiftly towards your goal, but along the way you spot a piece
of trash.  You're a good citizen and so you pick up that trash so that you can
put it in the bin the next time you see one.

As you approach a trash bin to put the trash away someone stops you and points
out that this bin was actually for recycling.  They helpfully point you to the
trash bin across the road.  You thank the good citizen for stopping you from
making a mistake, and bring the trash to the appropriate place.

A few folks around the trash bin notice that you're cleaning up the streets,
and point you to more trash that you can pick up.  That's fine, you're happy to
help out, and so you pick up some more trash to clean up.  They get excited
about this and point you down a side road that needs even more cleaning.

You're not feeling great about this, you need to get to town and back, and
daylight is running out.  These kind folks are well meaning, but they've
mistaken your intent as "clean up the streets" rather than "get to town".
You calmly explain to them that you're not actually here to clean up the
streets, explain that you're headed to town to get medicine for your family,
and that you really must be off.  Now that you've explained your context they
fully understand your situation and indeed encourage you on your way, perhaps
even pointing you to a bus line that you didn't know existed.


## Summary

As we as OSS developers shift to doing professional open source maintenance we
need to shift how we think a little.  Open source is amazing at having strong
impact, and at collaboration, but often lacks the focus or direction of
professional software engineering shops.  We should think about how we bring
the focus of professional work into our open source development practices.

A great and ubiquitous example of this is PR review, which is a common source
of scope creep, and often in directions that are not primary foci of the team.

Fast PRs also feel great, we should do more of those, if we can keep them safe.


*Total write time: 21 minutes*

*Total edit and publish time: 2 minutes*
