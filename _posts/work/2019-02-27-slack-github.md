---
layout: post
title: "Why I Avoid Slack"
author: Matthew Rocklin
tags: []
theme: twitter
---
{% include JB/setup %}


I ~~hate~~  *strongly dislike* interacting on Slack, specifically for technical
conversations around open source software.

Actually, that's not fair, Slack is a great tool.  Slack is a great way for
colleagues within an institution or group to communicate real-time with chat,
voice, or video.  Slack is certainly the most polished of the enterprise chat
tools, and today is something that probably most companies and collaborations
should use.

What I dislike is chat systems generally, especially as an open source software
maintainer.  My belief is that chat systems aren't well suited to developing or
maintaining open source software projects whose users and developers span a
variety of institutions.

I ask colleagues several times a day if we could move conversation from Slack
to GitHub and give a long explanation as to why.  In the spirit of Don't Repeat
Yourself (DRY) I'm writing this up as a blogpost.

I strongly dislike interacting on Slack because I want to  because I want to ...

1.  **Engage collaborators** that aren't on our Slack

    1.  External collaborators may have the *answers* that we need.  Having the
        conversation in a private place means that we can't ask them for help,
        or, if we do eventually need to ask them for help, we need to repeat
        the entire conversation that we've had privately, which wastes time.

    2.  External collaborators may have *questions or context* that we need.
        Their questions and experience can help us create a better product than
        we're capable of producing with only our in-house expertise.

    3.  External collaborators are much more likely to *buy in* to whatever we
        come up with if they were able to see the reasoning behind it and
        participate during that conversation.

    As we adopt community maintained open source software we have to recognize
    that the broader team we're working with extends beyond the borders of
    those people that have access to our Slack.

2.  **Record the conversation** in case participants change in the future.

    Most development efforts change hands over time.  We may work on this
    project today, but next month some of us will probably move on to other
    projects and new people will arrive.  These new developers ask questions
    about why something was done and there are one of two answers, depending on
    whether the conversation was on Slack or GitHub:

    -  **Slack**: We had a conversation about this a while ago and decided
        that it was the right course of action.
    -  **GitHub**: Go look at Issue #1234 and you'll be able to see the
       reasoning why, who had which opinions, and whether or not your concern
       was raised there.  If your concern wasn't raised there then we can
       easily pick up that thread of conversation on GitHub a year later
       (this happens all the time in OSS).

3.  **Serve the silent majority** of users who search the web for answers to
    their questions or bugs.

    On Slack, maintainers get asked the same questions daily.  We have people
    ask for "a few minutes of our time" every few minutes.  We strongly prefer
    to answer questions once in a place where future users can find the answer
    from a web search.  This includes people outside the company, but also
    people within the company.

    Maintainers are much happier devoting a lot of time to craft a high quality
    answer to questions if those questions and answers can help others in the
    future.

4.  **Encourage thoughtful discourse**.
    Because GitHub is a permanent record it forces people to think more before
    they write.  This is hard on casual conversation, yes, but we're not here
    for casual conversation.  Asking people to spend a minute crafting comments
    generally results in a conversation that is higher functioning, more
    concise, and much easier to review later.

5.  **Cross reference issues**.
    Slack is siloed.  It doesn't allow people to cross reference people or
    conversations across Slacks.  OSS maintainers get invited to literally
    dozens of Slack organizations.  It is not feasible to manage dozens of
    Slack tabs and different siloed organziations.

    GitHub is public and conversations across different projects can easily
    cross reference each other.  This encourages collaboration between projects
    and avoids wheel-reinvention.

I still love Slack for inter-personal contact.  It's great for chatting
with teammates, checking in to see how people are doing emotionally, or sharing
pictures about our lives.  Professionally I think it's also a good place for
internal teams to do daily check-ins and sometimes to arrange short-term
priorities.  Slack has many great uses, but I think that in-depth technical
conversation and long-term planning aren't among them.
