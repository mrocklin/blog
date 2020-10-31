---
layout: post
title: Concerns about Saturn Messaging
tagline:
category: work
draft: true
tags: []
theme: twitter
---
{% include JB/setup %}

Backstory
---------

I was having a chat with Hugo Shi, co-founder of Saturn yesterday.
I have some concerns about how Saturn handles messaging around Dask.
Hugo asked me to be more specific both about my concerns and how things could
improve in order to help normalize relations a bit.  This post tries to do
that.

To summarize this post, Saturn does two things that I dislike:

1.  They **present themselves as an authority** in areas where they are not,
    often by lifting content or taking undue credit
2.  Saturn engages in **growth-hacky marketing behaviors** that,
    while unfortunately common among growth-oriented tech startups,
    isn't something that I personally want anywhere near Dask.

Fortunately, Saturn is also in a position to change these behaviors

1.  They're **starting to generate some of their own content**,
    and so can hopefully begin to develop a voice based on their own experience
2.  They've **shown good reactivity to feedback** about growth-hacky behaviors,
    but **need to shift this to be proactive / self-policing**

My hope is that this post serves as one example of a general question about how
OSS projects deal with new for-profit companies, and that it helps to normalize
relations with Saturn.


Bias and Disclaimer
-------------------

I am horribly biased.  Along with helping to maintain the Dask OSS community, I
also lead Coiled, a for-profit company based around Dask.  Saturn competes with
Coiled in that space, so you should not trust anything that I say.

Also, due to this bias, I would like as much as possible, to take off my Dask community leader hat.


Saturns wants to be perceived as a Dask/RAPIDS authority
--------------------------------------------------------

### Saturn copies content to be perceived as a Dask expert

Dask is highly successful.  Saturn wants to associate themselves with Dask.
To help with this they include pages like "What is Dask?" and "Dask vs Spark"
on their webpage (edit, the dask-vs-spark page was taken down recently).

This association makes it easier to attract clients and get VC funding.
(VCs *really* want to fund Dask companies right now.)
However Saturn doesn't have much Dask expertise today (to my knowledge),
and so they copy things.

Consider their "What is Dask?" page:

<img src="{{BASE_PATH}}/images/saturn/what-is-dask-1.png" width="100%">

<img src="{{BASE_PATH}}/images/saturn/what-is-dask-2.png" width="100%">

It's nicely worded, and describes the project well, but it's ripped
[word-for-word from the Dask webpage](https://docs.dask.org/).
The images are ripped from YouTube videos from other Dask contributors.

*And if you're going to steal content, at least steal valid content.
The top image is ancient, and uses API that is no longer valid and will result
in user errors.*

At the bottom you may notice the text "Source: Dask".
So *technically* they're not plagiarizing, but I suspect that many readers read
that content and say "oh, Saturn knows what they're talking about" and don't
quite get down to that bottom line, or if they do they don't notice it.

When including other peoples' work, I recommend giving attribution up-front and
visually separating it so that no one can be confused about what is the work of
Saturn, and what is the work of others.  Or even better, Saturn should develop
their own voice, and describe Dask in their own words and how Saturn helps
support Dask with deployments.

Saturn used to also have a "Dask vs Spark" page,
which was similarly copied from Dask docs
but it appears to be taken down today.


### Saturn also claims to be an expert in RAPIDS

Consider this slide from the [Rapids Release Deck](https://docs.rapids.ai/overview/latest.pdf)

<img src="{{BASE_PATH}}/images/saturn/rapids.png" width="80%">

It describes how Dask and RAPIDS work together to provide a scale out / scale
up solution.  It was made by the Dask/RAPIDS developers, and represents a year
of very hard work by a sizable team.

Now consider this slide from Saturn:

<img src="{{BASE_PATH}}/images/saturn/scale-up-scale-out.png" width="80%">

It feels odd to see a company copy a slide about work they didn't do, and then
slap their logo on it to use with their advertising.

Saturn wants to be perceived as an authority on these topics.
I don't think that they are today, but I could be wrong, I don't know all of the individuals within the company or their skillsets.
If they *are* an authority, then they should generate their own content.
Fortunately, they're well on their way to doing that today, and I'm excited about the change.


### What Saturn does Well

I do think that Saturn is an authority on some things.  Hugo generally
knows how to make companies happy with Python.  When Julia joined Saturn she
started working with the Dask maintainers triaging and solving issues.  She has
learned a lot, does a great job handling users, and has been a pleasure
to work with.  I'm sure that she'll be an excellent asset to Saturn and to Dask going forward.
I'm also sure that other Saturn employees bring their own experience of which I am unaware.
I've indirectly heard positive things about James Lamb, but haven't interacted with him personally.
I apologize for not knowing you all better.

I also get the sense that Saturn has developed a good understanding of how to
deploy services like Jupyter and Dask on Kubernetes, as well as handle a lot of
the peripheral tasks like managing conda environments and web servers.

I would love to see Saturn present itself as a company that knows how to deploy things.
This seems more authentic.


### Good Marketing by Saturn

In the last few months Saturn has also started doing some good work.

They've done some [nice demo workloads on Dask vs Spark](https://www.saturncloud.io/s/supercharging-hyperparameter-tuning-with-dask/)
showing that they're able to use both to make a point about the strengths of Dask over Spark.
They've also started showing off some actual results with Saturn users, which is very cool

<img src="{{BASE_PATH}}/images/saturn/good-elsevier.png" width="70%">

This last effort is Saturn showing their own work, which is awesome.
Again, I welcome this messaging because it's built on the effort and expertise of the company itself.
Saturn seems to be generating some of their own content now, which should help to reduce tension.


Wacky marketing crap
--------------------

Many companies today engage in quasi-ethical growth-hacky crap.

This is unfortunately common in growth-oriented VC-funded startups,
but it's something that I personally don't want anywhere near the Dask project.
I find it to be dishonest.

So maybe take this as me using Saturn as an example of a larger problem.
Sorry to pick on you all here.


### "Created by Anaconda Founders"

Saturn claims to be created by founders of Anaconda.
This may be *technically* true, in that Hugo was there on day one, but really
Anaconda was led by Travis Oliphant and Peter Wang.
They are the ones who sweated day in and day out.  They are the ones who
wrangled investors.  They are the ones who hired people, fired people, dealt
with lawyers, insurance, sick employees, and so on.  It's a hard job.

There was also a group of engineers that were there on day one including
Francesc Alted, Bryan van den Ven, Mark Wiebe, and Hugo Shi (my history here is
spotty, so please forgive me if I dropped or added anyone).  Hugo was the one
based in NYC and so spent most of his time helping Anaconda clients in
financial services.
He was not at the helm of Anaconda.

People today often associate the term "founder" with "the person running the show".
Saturn's messaging isn't technically wrong, but it's certainly misleading.


### Stack Overflow

To my knowledge Saturn engineers have answered exactly one Dask question on Stack Overflow.

<img src="{{BASE_PATH}}/images/saturn/stack-overflow.png" width="80%">

There are 3027 questions in the [#dask
tag](https://stackoverflow.com/questions/tagged/dask) today.
Seeing someone come on and use a community resource to advertise their product
and then vanish feels off.

Also, look at the time stamps.
This question was answered 18 minutes after it was asked.
I suspect that it was planted.
I believe that community resources like Stack Overflow should not be used in corporate marketing.


### Twitter

Saturn engages in growth hacky methods in order to boost their Twitter
followers.  They follow/unfollow thousands of people hoping that they will follow them
back.

<img src="{{BASE_PATH}}/images/saturn/twitter.png" width="50%">

This makes them look bigger than they actually are.
I get that that's good for a company, but it's also misleading.


### LinkedIn

I have no idea how they got 12,000 LinkedIn followers, but I strongly suspect
that the were purchased (Saturn folks, please correct me if I'm wrong and I'll
happily remove this and issue an apology.)

<img src="{{BASE_PATH}}/images/saturn/linked-in.png" width="50%">

But worse, they also made the Dask group on LinkedIn.  This is managed
exclusively by Saturn employees, and seems to have turned into a morass of
advertisements.  In Saturn's defense, Hugo did offer to make me a manager at
one point and I declined, saying that if we were going to do this then it
should probably be managed by the community, rather than a company.

<img src="{{BASE_PATH}}/images/saturn/linked-in-dask-group.png" width="100%">

In general claiming a space like this isn't great, but if you're going to claim
it, then please at least curate it well.


### Unreciprocated Partnerships

Saturn claims to have partnered with some very impressive companies

<img src="{{BASE_PATH}}/images/saturn/partners.png" width="100%">

I suspect that actually these are one-way relationships, and signal that Saturn
uses these products rather than that they partner with these companies.

I think that most readers interpret "partnership" as a mutual relationship,
and so in seeing this kind of messaging assume that these companies have
endorsed Saturn when in fact they have not.


### Inventing Numpy and Scipy

Saturn used to claim that Saturn was founded by the creators of Numpy and Scipy
in their job listings.  I quote

> You will be an entry-level Data Scientist for Saturn Cloud, an exciting new venture founded by the creators of Anaconda, NumPy, and SciPy.

To Saturn's credit when Travis (the actual creator) reached out they took it down immediately.
Hugo also mentioned to me that he had no idea about this, and I'm sure that
that's true (Hugo and Travis are also good friends).

The concern here is that Saturn needed to be told that this kind of thing wasn't acceptable.
There doesn't seem to be an internal moral compass or policing system within Saturn messaging.
Technical companies deal with this all the time.
Marketing wants to be aggressive, while product/engineering usually brings them back to reality.
We've all experienced this struggle, and it's ok to get it wrong sometimes, but
from what I can see Saturn doesn't police itself.

Saturn was singularly focused on appearing to be an authority.


Other Dask Companies
--------------------

There are many Dask companies today:

-   **Anaconda:** the birthplace of Dask
-   **Quansight:** open source experts, created by Anaconda/Numpy/Scipy creator Travis Oliphant
-   **Coiled:** run by Dask maintainers, provides hosted and enterprise Dask deployments

as well as Dask-adjacent companies

-   **BlazingSQL:** RAPIDS experts and creators of the BlazingSQL system
-   **Prefect:** creators of prefect for workflow management, which deploys on Dask
-   **Metrostar:** for US government services

And a variety of other consulting companies which use Dask as part of their repertoire

-   **Quansight:** see above
-   **BeOpen:** mostly in the Xarray space
-   **Backtick:** data consultancy

In some sense we all compete with each other, but we collaborate and gain from each other far more.
This is a thriving OSS/Business community that I think does a great job of
serving their customers and the broader OSS community at the same time.
All of these companies think hard about striking a balance between corporate
profits and principled behavior.  All of them communicate well and hold
themselves to high standards.

Saturn is a bit of an outlier today, at least where its messaging is concerned.
They have a lot of potential and we'd all like to find a way to bring them into the fold.
To do this I think that they should stand on the merit of their own work,
and develop a more principled communication strategy.
