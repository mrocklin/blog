---
layout: post
title: So you want to contribute to open source
category: work
draft: true
tags: [Programming, Python, scipy]
theme: twitter
---
{% include JB/setup %}


Welcome new open source contributor!

I appreciated receiving the e-mail where you said you were excited about
getting into open source and were particularly interested in working on a
project that I maintain.  This post has a few thoughts on the topic.

First, please forgive me for sending you to this post rather than responding
with a personal e-mail.  Your situation is common today, so I thought I'd write
up thoughts in a public place, rather than respond personally.

This post has two parts:

1.  Some pragmatic steps on how to get started
2.  A personal recommendation to think twice about where you focus your time


### Look for good first issues on Github

Most open source software (OSS) projects have a "Good first issue" label on
their Github issue tracker.  Here is a screenshot of how to find the "good
first issue" label on the Pandas project:

<img src="{{BASE_PATH}}/images/good-first-issue.png">

*(note that this may be named something else like "Easy to fix")*

This contains a list of issues that are important, but also good introductions
for new contributors like yourself.  I recommend looking through that list to
see if something interests you.  The issue should include a clear description
of the problem, and some suggestions on how it might be resolved.  If you need
to ask questions, you can make an account on Github and ask them there.

It is very common for people to ask questions on Github.  We understand that
this may cause some anxiety your first time (I always find it really hard to
introduce myself to a new community), but a "Good first issue" issue is a safe
place to get started.  People expect newcomers to show up there.


### Read developer guidelines

Many projects will specify developer guidelines like how to check out a
codebase, run tests, write and style code, formulate a pull request, and so on.
This is usually in their documentation under a label like "Developer
guidelines", "Developer docs", or "Contributing".

If you do a web search for "pandas developer docs" then this page in the first
hit:
[pandas.pydata.org/pandas-docs/stable/contributing.html](https://pandas.pydata.org/pandas-docs/stable/contributing.html)

<img src="{{BASE_PATH}}/images/contributing-pandas.png">

These pages can be long, but they have a lot of good information.  Reading
through them is a good learning experience.


### But this may not be as fun as you think

Open source software is a field of great public interest today, but day-to-day
it may be more tedious than you expect.  Most OSS work is dull.  Maintainers
spend most of their time discussing grammatical rules for documentation,
discovering obscure compiler bugs, or handling e-mails.  They spend very little
time inventing cool algorithms.  You may notice this yourself as you look
through the issue list.  What fraction of them excite you?

I say this not to discourage you (indeed, please come help!) but just as a
warning.  Many people leave OSS pretty quickly.  This can be for many reasons,
but lack of interest is certainly one of them.

*The desire to maintain software is rarely enough to keep people engaged in
open source long term*


### So work on projects that are personal to you

You are more than a programmer.  You already have life experience and skills
that can benefit your programming, and you have life needs that programming can
enhance.

The people who stay with an OSS project are often people who need that project
for something else.

-  A musician may contribute to a composition or recording software that they use at work
-  A teacher may contribute to educational software to help their students
-  Community organizers may contribute to geospatial software to help them plan
   activities or understand local issues.

So my biggest piece of advice to you is not to try to contribute to a package
because it is popular or exciting, but rather wait until you run into a problem
with a piece of software that you use daily, and then contribute a fix to that
project.  It can be more rewarding to contribute to something that is already
in your life and as an active user you already have a ton of experience and
a place in the community.  You are much more likely to be successful
contributing to a project if you have been using it for a long time.
