---
layout: post
title: "Why I Avoid Slack"
author: Matthew Rocklin
tags: []
theme: twitter
---
{% include JB/setup %}


I avoid interacting on Slack, especially for technical conversations around
open source software.  Instead, I encourage colleagues to have technical and
design conversations on GitHub, or some other system that is public, permanent,
searchable, and cross-referenceable.  In the spirit of Don't Repeat Yourself
(DRY) I'm writing up these thoughts as a blogpost.

Slack is a great tool.  Slack is a great way for colleagues within an
institution or group to communicate real-time with chat, voice, or video.
Slack is probably the most polished of the enterprise chat tools, and today is
something that probably most companies and collaborations should use.

However internal real-time chat systems are, I think, bad for productivity
generally, especially for public open source software maintenance.  Real-time
chat systems make everyone feel productive (it's fun to have a face-paced
technical conversation with colleagues), but do relatively little for long-term
community consensus building, particularly when the users and developers of a
project span a variety of institutions and a long range of time.

Here are some more reasons in-depth why I prefer conversation on GitHub rather
than Slack.  I prefer GitHub because I want to ...

1.  **Engage collaborators** that aren't on our Slack

    1.  External collaborators may have the *answers* that we need.  Having the
        conversation in a private place means that we can't ask them for their
        help, or, if we do eventually need to ask them for help, we need to
        summarize the entire conversation that we've had privately, which
        wastes time.

        Individual open source maintainers often don't know the answers that
        people ask, but they do know how to redirect to someone who does.
        More often than not, that person is in another institution.  If you ask
        your question on GitHub this redirection is easy.

    2.  External collaborators may have *questions or context* that we need.
        Their questions and experience can help us create a better product than
        we're capable of producing with only our in-house expertise.

        Most important problems are useful across many organizations, while
        solutions built within one organization are often overly-specific to
        the needs of that organization.  By getting broader context, OSS has a
        much higher likelihood of success.

    3.  External collaborators are much more likely to *buy in* to whatever we
        come up with if they were able to see the reasoning behind it and
        participate during that conversation.

        <img src="https://imgs.xkcd.com/comics/standards.png" width="70%">

        If you open the design process to the creators of the
        previous 14 standards, the 15th standard has a much higher probability
        of actually being used.

    As we adopt community maintained open source software, the team we work
    with extends beyond our institution, and beyond the people who listen in to
    all of our institution's Slack conversations.

2.  **Record the conversation** in case participants change in the future.

    Most development efforts change hands over time.  We may work on this
    project today, but next month some of us will probably move on to other
    projects and new people will arrive.  These new developers ask questions
    about why something was done and there are one of two answers, depending on
    whether the conversation was on Slack or GitHub:

    -  **Slack**: We had a conversation about this a while ago and decided
        that it was the right course of action.  Just go with it.

    -  **GitHub**: Go look at Issue #1234 and you'll be able to see the
       reasoning why, who had which opinions, and whether or not your concern
       was raised there.  If your concern wasn't raised there then we can
       easily pick up that thread of conversation on GitHub a year later
       (this happens all the time in long running OSS projects).

    Even in the same group we often find that people repeat the same
    conversations.  If there is an obvious place for that conversation, and you
    need to scroll through previous comments, then it's far less likely that
    people will have to repeat themselves.

3.  **Serve the silent majority** of users who search the web for answers to
    their questions or bugs.

    On Slack, maintainers get asked the same questions daily.  We have people
    ask for "a few minutes of our time" every few minutes.  We strongly prefer
    to answer questions once in a place where future users can find the answer
    from a web search.  This includes people outside the company, but also
    people within the company.

    Maintainers are much happier devoting a lot of time to craft a high quality
    answer to questions if those questions and answers can help others in the
    future.  I personally spend a lot of time crafting answers on Stack
    Overflow, while I usally ignore questions on chat systems.  Want a good
    ansewr?  Pose a [good
    question](https://matthewrocklin.com/blog/work/2018/02/28/minimal-bug-reports)
    in a public place.

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

Slack is the easy choice.  It's so much easier just to open up a one-on-one
conversation with someone, chat with them for a bit, get your answer, and feel
like you've had a productive experience.  It feels good, but is rarely the
correct choice long term, especially when you add up how many times that same
conversation occurs.  Putting in a bit more effort and starting (or
continuing!) a well-posed conversation in a public issue tracker like GitHub is
likely better for your project and for your teammates long term.

I still love Slack for inter-personal contact.  It's great for chatting with
teammates, checking in to see how people are doing emotionally, or sharing
pictures about our lives.  Professionally I think it's also a good place for
internal teams to do daily check-ins and sometimes to arrange short-term
priorities.  Slack has many great uses, but I think that in-depth technical
conversation and long-term planning aren't among them.
