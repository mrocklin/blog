---
layout: post
title: Admirable Traits of Tech Leads
tagline:
category: work
draft: true
tags: []
theme: twitter
---
{% include JB/setup %}


What is a technical lead?
-------------------------

Tech lead is a role for senior engineers that provides some of the leverage of
management, while avoiding most of the administrative burden.  It's a fun role.
This post talks about some positive behaviors to think about should you find
yourself in this role.

As the name suggests, tech leads *lead* larger technical efforts.
They work with a team, but typically don't formally manage anyone.
The team looks up to them and it's their job to steer the effort technically,
while typically only using the soft power of generally knowing what they're
doing.

It's a really fun role.  I spent most of my time as a tech lead while at Anaconda, and serve
in that capacity to some extent in OSS communities.  I wanted to share some of
the positive behaviors that I think make for a good tech lead.

So, what can a good tech lead do?


Tech lead behaviors
-------------------

-   **Solve Hard Problems**: as a start, you have to be an excellent developer.
    You're going to have to rescue your teammates from difficult bugs,
    and tackle the core bits of whatever you're building.

    But if you want to solve hard problems then stay a senior engineer.
    Technical leadership is about guiding rather than executing

-   **Avoid Hard Problems**: save your team time by pointing them towards
    simple solutions when they suffice.

    A team lead has to provide paths to solutions that the rest of the team can
    easily implement.  Finding easy solutions is hard.

    A team lead often has to say *"OK, I can see that your solution works well,
    but I wonder if we can make it simpler by doing X.  This will probably help
    down the line with future maintenance."*

-   **Avoid Technical Debt**: leading a large effort is like playing chess.
    You make individual moves, but you think ahead about the ramifications of
    those moves.

    If the team has to spend time dealing with, or paying down technical debt
    that that's your fault.  You should think about simple and extensible designs,
    so that your teammates can solve individual problems that robustly lead to
    an efficient solution.

-   **Break large problems down into small ones**: building something
    yourself is easy.  Breaking down a large thing into small things that many
    people can develop on at once in parallel is hard and requires thoughtful
    design.

-   **Scope problems for your team:** you don't have time to do all of the work
    yourself, but you may have time to describe how you would solve a
    particularly tricky part of a problem, or to craft a test for the behavior
    that you want.

    As you know, a lot of software development time is spent understanding
    design, and exploring wrong paths.  You're probably faster at this than
    your teammates, and so it's a highly productive activity for you.

-   **Know your team:** In order to properly scope and describe tasks for your
    teammates you need to know their technical capabilities and preferences
    pretty well.  This arises in two components:

    1.  You can match problems to teammates based on interest.  People do a
        better job on problems that excite them.

    2.  You can provide more or less detail based on their experience with
        these kinds of problems.

-   **Explain your thought process:** It's not enough to say "here is a test
    and a design, please implement it".  Remember that you're not in charge of
    anyone here.  Instead, you lead by providing explanation and context on why
    you think a certain path is best.

    -   **Bad:** Please use algorithm X here rather than Y.
    -   **Good:** I suspect that algorithm Y here will not perform well when we
        have many users.  I think that it's O(n^2), which is fine for the test
        cases that we have here, but given that we're expecting 10k
        simultaneous users and the cost here seems to be about 5us, this turns
        into `5us * 10k ** 2 = 10 minutes`

        Instead, I think that algorithm X might be a better fit.  It's a bit
        slower when we have very few users, but should scale much better.

    There are a couple of reasons for this.  First, keep in mind that you're
    not in charge.  Overly aggressive tech-leads are unpleasant to work with.

    Second, you're supposed to teach your understanding of the system onto
    your coworkers, and help them progress professionally.

-   **Advocate for teammates:** tech leads are unique in that they

    1.  have respect and clout in the company
    2.  have a lot of direct experience with individual engineers
    3.  aren't technically responsible for anyone

    As a result they are often the best source of information about who is
    doing well.  While you don't have direct budget authority to give raises or
    promotions, you do have *soft power* and can advocate for great teammates.

    On the reverse, you also know when someone isn't working out in the team.
    For managers it's *really hard* to fire someone.
    Many times the manager knows that it's not working out, but that's also
    somewhat their fault for not coaching/assigning the teammate well enough.
    Managers feel horrible and so tend to wait a long time before firing someone.
    A tech lead doesn't have this block, and so can more clearly make this
    assessment.  This usually makes the manager's job easier.

    A tech lead is like a cool aunt/uncle.  People say things to them that they
    wouldn't say to siblings or parents, and they're disconnected enough to
    easily give insightful feedback.

-   **Communicate directly to stakeholders:** a good tech lead
    can talk directly to other parts of the company (product, sales, marketing).
    They're also often called in to deal with important clients.

    Because of this, tech leads need to be able to turn on a certain level of
    professionalism, and also understand the non-technical needs of others.
    They need to understand why the work that they do is important to people.

-   **Listen, and have no ego:** because of this, tech leads need to listen,
    and have very little ego when it comes to technical work
    (I personally need to work on this).

    Rockstar developers tend to make poor tech-leads (but awesome senior engineers).

    Instead the best tech leads I know are able to tell you what course of
    action they think is best one minute, and then have their mind changed
    entirely the next minute.  This is often developed with age, or with
    experience working on technical projects where they are wrong (which
    happens often if you pay attention).

-   **Respect senior engineers:** Tech leads often work alongside other senior
    engineers who may have more experiene as developers, but don't care to
    direct the work of others.  It's important to remember that these people
    are often smarter than you, and seek their technical opinion.


OSS Maintainers make good Tech Leads
------------------------------------

The role of having a lot of technical context, trying to direct many others
along a shared technical vision, but not actually having authority over anyone
is a role familiar to many OSS maintainers.  There is excellent cross-over
between these two positions.
