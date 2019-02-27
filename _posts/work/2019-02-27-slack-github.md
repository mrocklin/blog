---
layout: post
title: "Why I Avoid Slack"
author: Matthew Rocklin
draft: true
tags: []
theme: twitter
---
{% include JB/setup %}


I -hate- *strongly dislike* interacting on slack.  Actually, that's not fair,
Slack is a great tool, certainly the most polished of the chat tools.  What I
dislike is chat systems generally, especially as an open source
software maintainer.

I ask colleagues several times a day if we could move conversation from Slack
to GitHub and give a long explanation as to why.  In the spirit of Don't Repeat
Yourself (DRY) I'm writing this up as a blogpost.

Reasons I strongly dislike interacting on Slack:

1.  We need to engage people that aren't on our Slack system.
    This includes external collaborators that work for another institution.

    1.  External collaborators may have the *answers* that we need.  Having the
        conversation in a private place means that we can't ask them for help,
        or, if we do eventually need to ask them for help, we need to repeat
        the entire conversation that we've had privately, which wastes time.

    2.  External collaborators may have *questions or context* that we need.
        Again, we don't want to have to repeat our entire conversation to them.

    3.  External collaborators are much more likely to *buy in* to whatever we
        come up with if they were able to see the reasoning behind it and
        participate during that conversation.

    As we adopt community maintained open source software we have to recognize
    that the broader team we're working with extends beyond the borders of
    those people that have access to our Slack.  It is as if we only had
    meetings with half the team at a time.

2.  We want to record the conversation in case participants change in the
    future.

    Most development efforts change hands over time.  The original designers
    and developers move on to other projects and new people arrive.  These new
    developers ask questions about why something was done and there are one of
    two answers, depending on whether the conversation was on Slack or GitHub:

    -  **Slack**: We had a conversation about this a while ago and decided
        that it was the right course of action.
    -  **GitHub**: Go look at Issue #1234 and you'll be able to see the
       reasoning why, who had which opinions, and whether or not your concern
       was raised there.  If your concern wasn't raised there then we can
       easily pick up that thread of conversation on GitHub a year later
       (this happens all the time in OSS).

3.  We want to enable the silent majority of users to find answers to their
    bugs without asking maintainers individually.

    On Slack maintainers get asked the same questions daily.  We have people
    ask for "a few minutes of our time" every few minutes.  We strongly prefer
    to answer questions once in a place where future users can find the answer
    from a web search.  This includes people outside the company, but also
    people within the company.

4.  GitHub forces people to think more before they write.  It's a permanent
    historical record.  This is hard on question askers and on easy
    conversation, yes, but we're not here for easy conversation.  Asking people
    to spend a minute crafting comments generally results in a conversation
    that is higher functioning and much easier to review later.

5.  Slack is silo'ed to particular organizations.  It doesn't allow people to
    cross reference people or conversations.  OSS maintainers get invited to
    literally dozens of Slack organizations.  It is not feasible to manage
    dozens of Slack tabs and different siloed organziations.

    GitHub is public an conversations across different projects can easily
    cross reference each other.  This encourages collaboration between projects
    and avoids wheel reinvention.
