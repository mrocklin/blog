---
layout: post
title: Public Institutions and Open Source Software
category: work
tags: [Programming, Python, scipy, dask]
theme: twitter
---

{% include JB/setup %}

As general purpose open source software displaces domain-specific all-in-one
solutions, many institutions are re-assessing how they build and maintain
software to support their users.  This is true across for-profit enterprises,
government agencies, universities, and home-grown communities.

While this shift brings opportunities for growth and efficiency, it also raises
questions and challenges about how these institutions should best serve their
communities as they grow increasingly dependent on software developed and
controlled outside of their organization.

-  How do they ensure that this software will persist for many years?
-  How do they influence this software to better serve the needs of their users?
-  How do they transition users from previous all-in-one solutions to a new
   open source platform?
-  How do they continue to employ their existing employees who have historically
   maintained software in this field?
-  If they have a mandate to support this field, what is the best role for them
   to play, and how can they justify their efforts to the groups that control
   their budget?

This blogpost investigates this situation from the perspective of **large
organizations that serve the public good**, such as government funding agencies
or research institutes like the National Science Foundation, NASA, DoD, and so
on.  I hope to write separately about this topic from both enterprise and
community perspectives in the future.

This blogpost provides context, describes a few common approaches and their
outcomes, and draws some general conclusions.


### Example

To make this concrete, place yourself in the following situation:

You manage a software engineering department within a domain specific
institution (like NASA).  Your group produces the defacto standard software
suite that almost all scientists in your domain use; or at least that used to
be true.  Today, a growing number of scientists use general-purpose software
stacks, like Scientific Python or R-Stats, that are maintained by a much wider
community outside of your institution.  While the software solution that your
group maintains is still very much in use today, you think that it is unlikely
that it will continue to be relevant in five-to-ten years.

What should you do?  How should your institution change its funding and
employment model to reflect this new context, where the software they depend on
is relevant to many other institutions as well?


## Common approaches that sometimes end poorly

We list a few common approaches, and some challenges or potential outcomes.

1.  **Open your existing stack for community development**

    You've heard that by placing your code and development cycle on Github that
    your software will be adopted by other groups and that you'll be able to
    share maintenance costs.  You don't consider your software to be
    intellectual property so you go ahead and hope for the best.

    **Positive Outcome**: Your existing user-base may appreciate this and some
    of them may start submitting bugs and even patches.

    **Negative Outcome**: Your software stack is already quite specific to your
    domain.  It's unlikely that you will see the same response as a general
    purpose project like Jupyter, Pandas, or Spark.

    Additionally, maintaining an open development model is hard.  You have to
    record all of your conversations and decision-making online.  When people
    from other domains come with ideas you will have to choose between
    supporting them and supporting your own mission, which will frequently
    come into conflict.

    In practice your engineers will start ignoring external users, and as a
    result your external users will stay away.

2.  **Start a new general purpose open source framework**

    **Positive**: If your project becomes widely adopted then you both get some
    additional development help, but perhaps more importantly your institution
    gains reputation as an interesting place to work.  This helps tremendously
    with hiring.

    **Negative**: This is likely well beyond the mandate of your institution.

    Additionally, it's difficult to produce general purpose software that
    attracts a broad audience.  This is for both technical and administrative
    reasons:

    1.  You need to have feedback from domains outside of your own.  Lets say
        you're NASA and you want to make a new image processing tool.  You need
        to talk to satellite engineers (which you have), and also
        microscopists, medical researchers, astronomers, ecologists, machine
        learning researchers, and so on.  It's unlikely that your institution
        has enough exposure outside of your domain to design general purpose
        software successfully.  Even very good software usually fails to
        attract a community.

    2.  If you succeeded in a good general purpose design you would also have
        to employ people to support users from all of those domains, and this
        is probably outside of your mandate.

3.  **Pull open source tools into your organization, but don't engage externally**.

    You're happy to use open source tools but don't see a need to engage
    external communities.  You'll pull tools inside of your organization and
    then manage and distribute them internally as usual.

    **Positive**: You get the best of software today, but also get to manage
    the experience internally, giving you the control that your organization
    needs.  This is well within the comfort zone of both your legal and IT
    departments.

    **Negative**: As the outside world changes you will struggle to integrate
    these changes with your internal processes.  Eventually your version of the
    software will diverge and become an internal fork that you have to
    maintain.  This locks you into current-day functionality and puts you on
    the hook to integrate critical patches as they arise.  Additionally you
    miss out on opportunities to move the software in directions that your
    organization would find valuable.

3.  **Get out of the business of maintaining software entirely.**
    Your institution may no longer be strictly needed in this role.

    The open source communities seem to have a decent pipeline to support
    users, lets just divert our userbase to them and focus on other efforts.

    **Positive**: You reduce operating budget and can allocate your people to
    other problems.

    **Negative**: This causes an upset to your employees, your user community,
    and to the maintainers of the open source software projects that are being
    asked to absorb your userbase.  The maintainers are likely to burn-out from
    having to support so many people and so your users will be a bit lost.
    Additionally the open source software probably doesn't do all of the things
    that the old software does and your existing users aren't experts at the
    new software stack.

    Everyone needs help getting to know each other, and your institution is
    uniquely positioned to facilitate this.


## Common approaches that sometimes end well

We now discuss a few concrete things to help where your institution is likely
uniquely positioned to play a critical role:

1.  **Maintain the existing stack**

    It's likely that the existing all-in-one stack will still be used for years
    by current researchers and automated systems.  You're not off the hook to
    provide maintenance.  However you might want to communicate an end-of-life
    to your userbase though saying that new feature requests are unlikely to be
    implemented and that support will expire in a few years time (or whatever
    is appropriate for your domain)

2.  **Develop learning materials to help users transition to the new stack**

    Your institution uniquely understands the needs of your user community.
    There are common analyses, visualizations, storage formats, and so on that
    are common among your users and are easy with the all-in-one solution, but
    which take effort with the new system.

    You can build teaching materials like blogposts, how-to guides, and online
    tutorials that assist the non-early-adopters to transition more smoothly.
    You can provide in-person teaching at conferences and meetings common to
    your community.  It's likely that the open source ecosystem that you're
    transitioning to already has materials that you can copy-and-modify for
    your domain.

    Assist users in reporting bugs, and filter these to reduce burden on
    the upstream OSS projects.  It's likely that your users will express
    problems in a way that is particular to their domain, but which doesn't
    make sense to maintainers.

    -  User says: *Satellite mission MODIS data doesn't load properly*
    -  Developer wants to hear: *GeoTIFF loader fails when given S3 route*

    Your engineers can help to filter and translate these requests into
    technical terms appropriate for the upstream project.  The people
    previously working on the all-in-one solution have a unique combination of
    technical and domain experience that is essential to mediate these
    interactions.

3.  **Contribute code upstream either to mainline packages or new subpackages**

    After you've spent some time developing training materials and assisting
    users to transition you'll have a much better sense of what needs to be
    fixed upstream, or what small new packages might be helpful.  You'll also
    have much more experience interacting with the upstream development
    community so that you get a sense of how they operate and they'll better
    understand your needs.  Now is a good time to start contributing actual
    code, either into the package itself if sufficiently general purpose, or
    into a spinoff project that is small in scope and focuses on your domain.

    It's very tempting to jump directly to this step and create new software,
    but waiting a while and focusing on teaching can often yield more
    long-lasting results.

4.  **Enable employees to spend time maintaining upstream projects and ensure that this time counts towards their career advancement**

    By this time you will have a few employees who have taken on a maintenance
    role within the upstream projects.  You should explicitly give them time
    within the work schedule to continue these activities.  The work that they
    do may not be explicitly within scope for your institution, but having them
    active within the core of a project makes sure that the mission of your
    institution will be well represented in the future of the open source
    project.

    These people will often do this work on their own at home or on the side in
    personal time if you don't step in.  Your institution should make it clear
    to them that it values these activities and that they are good for the
    employee's career within your institution.  Besides ensuring that your
    institution's perspective is represented within the core of the upstream
    projects you're also improving retention of a core employee.

5.  **Co-write grant proposals with maintainers of the core project**

    If your institution provides or applies for external funding, consider
    writing up a grant proposal that has your institution and the OSS project
    collaborating for a few years.  You focus on your domain and leave the OSS
    project maintainers to handle some of the gritty technical details that you
    anticipate will arise.  Most of those details are hopefully things that are
    general purpose and that they wanted to fix anyway.  It's usually pretty
    easy to find a set of features that both parties would be very happy to see
    completed.

    Many OSS maintainers work at an institution that allows them to accept
    grant funding (at least as a sub-contractor under your award), but may not
    have access to the same domain-specific funding channels to which your
    institution has access.  If they don't work at an institution for which
    accepting a grant sub-award is reasonable (maybe they work at a bank) then
    they might consider accepting the award through a non-profit foundation
    like [NumFOCUS](https://numfocus.org/).


## Summary

As primary development of software moves from inside the institution to
outside, a cultural shift occurs.  The institution transitions from leading
development and being fully in charge of its own destiny to playing a support
role in a larger ecosystem.  They can first help to lead their their user
community through this transition, and through that develop the experience and
relationships to act effectively within the broader ecosystem.

From this process they often find roles within the ecosystem that are critical.
Large public institutions are some of the only organizations with the public
mandate and long time horizon to maintain public software over decade-long time
scales.  They have a crucial role to play both in domain specific software
packages that directly overlap with their mandate and also with more general
purpose packages on which their domain depends indirectly.  Finding their new
role and learning to engage with external organizations is a skill that they'll
need to re-learn as they engage with an entirely new set of partners.

This growth requires time and patience at several levels of the organization.
At the end of the day many people within the institution will have to
collaborate with people outside while still staying within the mandate and
career track of the institution itself.
