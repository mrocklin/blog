---
layout: post
title: Supporting Users in Open Source
category: work
tags: [Programming, scipy, Python]
theme: twitter
---
{% include JB/setup %}

What are the social expectations of open source developers to help users
understand their projects?  What are the social expectations of users when
asking for help?

As part of developing Dask, an open source library with growing adoption, I
directly interact with users over GitHub issues for bug reports, StackOverflow
for usage questions, a mailing list and live Gitter chat for community
conversation.  Dask is blessed with awesome users.  These are researchers
doing very cool work of high impact and with novel use cases.  They report
bugs and usage questions with such skill that it's clear that they are
*Veteran Users* of open source projects.


Veteran Users are Heroes
------------------------

It's not easy being a veteran user.  It takes a *lot* of time to distill a bug
down to a reproducible example, or a question into an
[MCVE](http://stackoverflow.com/help/mcve), or to read all of the documentation
to make sure that a conceptual question definitely isn't answered in the docs.
And yet this effort really shines through and it's incredibly valuable to
making open source software better.  These distilled reports are arguably more
important than fixing the actual bug or writing the actual documentation.

Bugs occur in the wild, in code that is half related to the developer's library
(like Pandas or Dask) and half related to the user's application.  The veteran
user works hard to pull away all of their code and data, creating a gem of an
example that is trivial to understand and run anywhere that still shows off the
problem.

This way the veteran user can show up with their problem to the development
team and say "here is something that you will quickly understand to be a
problem."  On the developer side this is incredibly valuable.  They learn of a
relevant bug and immediately understand what's going on, without having to
download someone else's data or understand their domain.  This switches from
merely convenient to strictly necessary when the developers deal with 10+ such
reports a day.


Novice Users need help too
--------------------------

However there are a lot of novice users out there.  We have all been novice
users once, and even if we are veterans today we are probably still novices at
something else.  Knowing what to do and how to ask for help is hard.  Having
the guts to walk into a chat room where people will quickly see that you're a
novice is even harder.  It's like using public transit in a deeply foreign
language.  Respect is warranted here.

I categorize novice users into two groups:

1.  Experienced technical novices, who are very experienced in their field and
    technical things generally, but who don't yet have a thorough
    understanding of open source culture and how to ask questions smoothly.
    They're entirely capable of behaving like a veteran user if pointed in the
    right directions.
2.  Novice technical novices, who don't yet have the ability to distill their
    problems into the digestible nuggets that open source developers expect.

In the first case of technically experienced novices, I've found that being
direct works surprisingly well.  I used to be apologetic in asking people to
submit [MCVE](http://stackoverflow.com/help/mcve)s.  Today I'm more blunt but
surprisingly I find that this group doesn't seem to mind.  I suspect that this
group is accustomed to operating in situations where other people's time is
very costly.

The second case of novice novice users are more challenging for individual
developers to handle one-by-one, both because novices are more common, and
because solving their problems often requires more time commitment.  Instead
open source communities often depend on broadcast and crowd-sourced solutions,
like documentation, StackOverflow, or meetups and user groups.  For example in
Dask [we strongly point people towards StackOverflow](http://dask.readthedocs.io/en/latest/support.html#where-to-ask-for-help)
in order to build up a knowledge-base of question-answer pairs.  Pandas has
done this well; almost every Pandas question you Google leads to a
StackOverflow post, handling 90% of the traffic and improving the lives of
thousands.  Many projects simply don't have the human capital to hand-hold
individuals through using the library.

In a few projects there are enough generous and experienced users that they're
able to field questions from individual users.  SymPy is a good example here.
I learned open source programming within SymPy.  Their community was broad
enough that they were able to hold my hand as I learned Git, testing,
communication practices and all of the other soft skills that we need to be
effective in writing great software.  The support structure of SymPy is
something that I've never experienced anywhere else.


My Apologies
------------

I've found myself becoming increasingly impolite when people ask me for certain
kinds of extended help with their code.  I've been trying to track down why
this is and I think that it comes from a mismatch of social contracts.

Large parts of technical society have an (entirely reasonable) belief that open
source developers are available to answer questions about how we use their
project.  This was probably true in popular culture, where our stereotypical
image of an open source developer was working out of their basement long into
the night on things that relatively few enthusiasts bothered with.  They were
happy to engage and had the free time in which to do it.

In some ways things have changed a lot.  We now have paid professionals
building software that is used by thousands or millions of users.  These
professionals easily charge consulting fees of hundreds of dollars per hour for
exactly the kind of assistance that people show up expecting for free under the
previous model.  These developers have to answer for how they spend their time
when they're at work, and when they're not at work they now have families and
kids that deserve just as much attention as their open source users.

Both of these cultures, the creative do-it-yourself basement culture and the
more corporate culture, are important to the wonderful surge we've seen in open
source software.  How do we balance them?  Should developers, like doctors or
lawyers perform pro-bono work as part of their profession?  Should grants
specifically include paid time for community engagement and outreach?  Should
users, as part of receiving help feel an obligation to improve documentation or
stick around and help others?


Solutions?
----------

I'm not sure what to do here.  I feel an obligation to remain connected with
users from a broad set of applications, even those that companies or grants
haven't decided to fund.  However at the same time I don't know how to say
*"I'm sorry, I simply don't have the time to help you with your problem."* in a
way that feels at all compassionate.

I think that people should still ask questions.  I think that we need to foster
an environment in which developers can say "Sorry. Busy." more easily.  I think
that we as a community need better resources to teach novice users to become
veteran users.
