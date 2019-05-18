---
layout: post
title: The Role of a Maintainer
author: Matthew Rocklin
tags: [python,scipy]
theme: twitter
---
{% include JB/setup %}

What are the expectations and best practices for maintainers of open source software libraries?
How can we do this better?

This post frames the discussion and then follows with best practices based on my personal experience and opinions.  *I make no claim that these are correct.*


## Let us Assume External Responsibility

First, the most common answer to to this question is the following:

-  **Q:** *What are expectations on OSS maintainers?*
-  **A:** *Nothing at all.  They're volunteers.*

However, let's assume for a moment that these maintainers are paid to maintain
the project some modest amount, like 10 hours a week.

How can they best spend this time?


## What is a Maintainer?

Next, let's disambiguate the role of *developer*, *reviewer*, and *maintainer*

1.  **Developers** fix bugs and create features.  They write code and docs and
    generally are agents of change in a software project.  There are often many
    more developers than reviewers or maintainers.

2.  **Reviewers** are known experts in a part of a project and are called on to
    review the work of developers, mostly to make sure that the developers
    don't break anything, but also to point them to related work, ensure common
    development practices, and pass on institutional knowledge.  There are
    often more developers than reviewers, and more reviewers than maintainers.

3.  **Maintainers** are loosely aware of the entire project.
    They track ongoing work and make sure that it gets reviewed and merged in a
    timely manner.  They direct the orchestra of developers and reviewers,
    making sure that they connect to each other appropriately, often serving
    as dispatcher.

    Maintainers also have final responsibility.
    If no reviewer can be found for an important contribution, they review.
    If no developer can be found to fix an important bug, they develop.
    If something goes wrong, it's eventually the maintainer's fault.


## Best Practices

Now let's get into the best practices of a maintainer, again assuming the
context that they are paid to do this about 25% time for a moderately busy
software project (perhaps 10-50 issues/contributions per day).


### Timely Response

*"Welcome Bob!  Nice question.  I'm currently a bit busy right now, but I
think that if you look through [these notes]() that they might point you in the
right direction.  I should have time to check back here by Thursday."*

The maintainer is often the first person a new contributor meets.
Like a concierge or greeter at a hotel or restaurant, it's good to say "Hi"
when someone shows up, even if that's all you can say at that moment.

When someone is raising an issue or contributing a patch, try to give them a
response within 24 hours, *even if it's not a very helpful response*.  It's
scary to ask something in public, and much scarier to try write code and
contribute it to a project.  Acknowledging the contributor's question or work
helps them to relax and feel welcome.


### Answer Easy Questions Easily

*"Thanks for the question Bob.  I think that what you're looking for is
described in [these docs]().  Also, in the future we welcome these sorts of
questions on Stack Overflow."*

Answer simple questions quickly, and move on.

After answering, you might also direct new users and contributors to places
like Stack Overflow where they can ask questions in the future.


### Find Help for Hard Problems

*"Hey Alice, you're an expert on X, would you mind checking this out?"*

You probably have a small team of expert reviewers to ask for help for tricky
problems.  Get to know them well and use them.  It's not your job to solve
every problem, and you probably don't have time anyway.  It's your job to make
sure that the right reviewer sees the problem, and then track that it gets
resolved.

But also, don't *overuse* your reviewers.  Everyone has a tolerance for how
much they're willing to help.  You may have to spread things out a little.
Getting to know your reviewers personally and learning their interests can help
you to make decisions about when and where to use them.


### But follow up

*"Just checking in here.  It looks like Reviewer Alice has asked for X,
Developer Bob is this something that you have time to do?  Also it looks like
Developer Bob has a quesiton about Y.  Reviewer Alice do you have any
suggestions for Bob on this?"*

The reviewers you rely on are likely to swoop in, convey expertise, and then
disappear back to their normal lives.  Thank them for their help, and don't
rely on them to track the work to completion, that's your job.  You may have to
direct conversation a bit.

We often see the following timeline:

-  **Contributor:** "Hi! I made a patch for X!"
-  **Maintainer:** "Welcome!  Nice patch!  Hey Reviewer, you know X really well,
   could you take a look?"
-  **Reviewer:** "Hi Contributor!  Great patch!  I found a bunch of things that
   were wrong with it, but I think that you can probably fix them easily!"
-  **Contributor:** "Oh yeah!  You're right, great, I've fixed everything you
   said!"
-  ...
-  *silence*

At this point, jump in again!

-  **Maintainer:** "OK, it looks like you've handled everything that the
   reviewer asked for.  Nice work!  Reviewer, anything else?  Otherwise, I plan
   to merge this shortly"

   "Also, I notice that your code didn't pass the linter.  Please check out
   this doc for how to run our auto-linter."
-  **Contributor:** "Done!"
-  **Maintainer:** "OK, merging. Thanks Contributor!"

This situation is nice, but not ideal from the maintainer's perspective.
Ideally the reviewer would finish things up, but often they don't.
In some cases it might even be *their job* to finish things up,
but even then, it's also *your job* to make sure that things finish up so if
they don't show up, then it's on the maintainer.

*All responsibility eventually falls back onto the maintainer.*


### Prioritize your time

*"It'd be great if you could provide a minimal example as described
[here](https://matthewrocklin.com/blog/work/2018/02/28/minimal-bug-reports).
Please let us know if you're able to manage this.  otherwise given time
constraints I'm not sure what we can do to help further."*

Some contributors are awesome and do everything right.
They ask questions with minimal reproducible examples.
They provide well-tested code.
Everything.  [They're awesome.](https://matthewrocklin.com/blog/work/2016/08/25/supporting-users)

Others aren't as awesome.
They ask for a lot of your time to help them solve problems that have
little to do with your software.
You probably can't solve every problem well, and working on their problems
steals important time away that you could be spending improving documentation
or process.

Politely thank misinformed users and direct them towards
standard documentation on expectations on asking questions and raising bug
reports like [Stack Overflow's MCVE](https://stackoverflow.com/help/mcve)
or possibly [this post on crafting minimal bug
reports](https://matthewrocklin.com/blog/work/2018/02/28/minimal-bug-reports)


### Get used to a lot of e-mail

*"Ah, the joy of e-mail filters"*

If you're tracking every conversation then you'll be getting hundreds of
e-mails a day.  You don't need to read all of these in depth (this would take
most of your 10 hours a week) but you probably should skim them.  Don't worry,
with practice you can do this quickly.

You certainly don't want this in your personal inbox, so you may want to invest
a bit of time in organizing e-mail filters and labels.
Personally I use GMail and with their filters and keyboard shortcuts I can
usually blast through e-mail pretty quickly.  (Hooray for j/k Vim-style bindings in GMail)

I check my Github inbox a few times a day.  It usually takes 20-30 minutes in
the morning (due to all of the people active when I'm asleep) and 10 minutes
during other times in the day.  I look forward to this time.  It's nice seeing
a lot of people being productive.

Mostly during this period I'm looking for anyone who is blocked, and if
necessary I respond with something to help unblock them.


### But check the issue tracker periodically

*"Whoops!  I totally dropped this!  Sorry!"*

You'll miss things.  People will force-push to Github (which triggers no alert)
or the last person to reply to an issue will be you with no response. There are
also just old issues and PRs that have slipped through and aren't coming up on
your e-mail.

So every day or two, it's good to go through all issues and PRs that have a
glimmer of life in them and check in.  Often you'll find that someone has done
work and the reviewer has left, or that the developer has just left.  Now is a
good time to ask a gentle message

*Just checking in, what's the status here?*

Sometimes they'll be busy at work and will come back in a couple days.
Sometimes they'll need a push in the right direction.
Sometimes they'll disappear completely, and you have to decide whether to
finish the work or let it linger.


### Weekends

*"Now that I'm done with work for the week, I can finally finish up this PR.
Wait, where did everybody go?"*

This is hard, but a lot of the developers aren't contributing as part of
their day job, and so they work primarily on the weekends.  If they only work
on the weekends and you only respond during the week then we're going to have
very long iteration cycles, which is frustrating for everyone and unlikely to
result in successful work.

Personally I spend a bit of time in the morning and evening doing light
maintenance.  That's a personal choice though.


### Don't let reviewers drag things out too long

*"Can you just add one more thing?"*

Developers want to get their work in quickly.
Reviewers sometimes want to ask lots of questions, make small suggestions,
and sometimes have very long conversations.
At some point you need to step in and ask for a definitive set of necessary changes.
This gives the developer a sense of finality, a light at the end of the tunnel.

Very long review periods are a common anti-behavior today, they are destructive to
attracting new developers and contribute to reviewer burnout.  A reviewer
should ideally iterate once or twice with a developer with in-depth comments
and then we should be done.  This breaks down in a few ways:

1.  **The Slow Rollout:** The reviewer provides a few small suggestions, waits
    for changes, then provides a few more, and so on, resulting in many
    iterations.
2.  **Serial Reviewers:** After one reviewer finishes up, a second reviewer
    arrives with their own set of requested changes.
3.  **Reviewer Disagreement:** The two reviewers provide different suggestions and the contributor makes
    changes and undoes those changes based on who spoke last.
4.  **Endless Discussion:** The reviewers then engage in very long and detailed
    technical conversation, scaring away the original contributor.

This is reviewer breakdown, and it's up to the maintainer to identify that
it's happening, step in and say the following:

*OK, I think that what we have is a sufficient start.  I recommend that we
merge what we have here and continue the rest of this conversation in a
separate issue*


### Thank Developers

*"I appreciate all your work here.  In particular I'm really happy about these tests!"*

They look up to you.
A small amount of praise from you can make their day and encourage them to
continue contributing to open source.

Also, as with normal life, if you can call out some specific thing that they
did well it becomes more personal.


### Encourage Excellent Developers to Review, and Allow Excellent Reviewers to Maintain

*"Hey Bob, this new work is similar to work that you've done before.  Any
interest in taking a look?"*

Over time you will notice that a repeat contributor returns to the project
frequently, often to work on a particular topic.  When a new contribution
arrives in that part of the code, you might intentionally invite the repeat
contributor to review that work.  You might invite them to become a reviewer.

Similarly, when you find that a skilled reviewer frequently handles issues on
their own, you should find ways to give them ownership over that section of the
code.  Defer to their judgement.  Make sure that they have commit rights and
the ability to publish new packages (if the code is separate enough to allow
for that).  You should clear the way for them to become a maintainer.

To be clear, I wouldn't encourage everyone.  Even very good developers can be
bad reviewers or maintainers.  Bad reviewers can be unwelcoming and destructive
to the process in a variety of ways.  This activity requires social skills
that aren't universally held, regardless of programming skill.


### Take a Vacation (But Tell Someone)

*"I'd like to checking out for a week.  Alice, would you mind keeping an eye on
things?"*

Maintaining a project with a few peers is wonderful because it's easier for
people to take breaks and attend to their mental health.  However, it's
important to make people aware of your absence during vacations or illness.
A quick word to a colleague about an absence, expected or otherwise, can help
to keep things running smoothly.

*Many* OSS projects today have a single core maintainer.  This is hard on them
and hard on the project (solo-maintainers tend to quickly become gruff).
This post is designed with this problem in mind.
Hopefully as we develop a vocabulary and conversation around the administrative
sides of maintenance it will become easier to identify and encourage these
behaviors in new maintainers.


## Summary

*"Thanks for taking the time"*

Maintaining a project is not about being a great developer or a clever
reviewer.  It's about enabling others, removing road-blocks before they arise,
and identifying and resolving difficult social situations.  It has much more to
do with logistics, coordination, and social behaviors than it has to do with
algorithms and version control.

I have to admit, I'm not great at this, but I'm trying to become better.
Maintaining a software project is a learned skill and takes effort.
The reward can be significant though.

A well maintained project is pleasant to work on and attracts a productive team
of friendly developers and reviewers that support each other.  It's also a
great way to learn more about how people use your software project than you
ever could while writing code.  The activity of maintaining software gives you
enough exposure to see where the project is headed and what's possible going
forward.
