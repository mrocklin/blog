---
layout: post
title: What Every Engineer Should Know About Sales
category: work
tags: []
theme: twitter
---

{% include JB/setup %}

-  **Engineer:** *Hey Boss, what should I know to more effectively sell our product?*
-  **Boss:** *Resist the urge to answer technical questions*

I had this brief conversation years ago at an industry conference.
This advice has proven invaluable over the years in many contexts
(including beyond corporate sales)
and I've re-shared it countless times,
so I thought I'd write it up.

Sales is About Listening
------------------------

My then boss (Peter Wang) expanded on his main point

*Resist the urge to answer technical questions*

To go on to say that as engineers,
we always want to show off how something works.
This is either out of a need to show that we are knowledgable,
or just because we like to geek out.

But we often go too deeply too quickly into a solution
before we fully understand the potential customers' problem.
This is almost always a waste of everyone's time.

So when a customer asks a technical question,
it's often better to follow up with a question to better understand their situation.
Here is a small example interaction

### Bad.  Engineer talks first

-   **Customer:** Is your database product fast?
-   **Bad Engineer:** Yes!  Our combination of advanced algorithms and cluster
    computing let us scale to very large datasets.
    Let me tell you about our GPU accelerated join algorithms.
-   *Bad Engineer continues on for a while until customer excuses himself awkwardly*


### Good.  Engineer listens first

-   **Customer:** Is your database product fast?
-   **Good Engiineer:** Yes, in many ways, but I'm curious, why do you care
    about speed?  I see that you work at an insurance company.  Is this for
    analytics?
-   **Customer:** No actually.  While we do do lots of analytics, our main need
    right now is to host queries for our website.
-   **Good Engineer:** Ah, so you're looking for something like a key-value
    database with query times under, say, 20ms?
-   **Customer:** Oh yes, anything under 50ms would be fine really.
-   **Good Engineer:** OK great.  Yes, we can definitely help you with that.  I
    normally talk about our GPU accelerated analytics database, but that's
    actually not a good fit for your use case.  Instead, let me show you our
    transactionial database product.  I'm less familiar here, but I'm confident
    that your use case fits right in here.

Selling is much less about telling people what your product solves,
and is much more about listening to what problems other people have.
By listening you learn a lot about their situation.
This gives you a lot of insight into what they care about,
and helps you to match them to solutions more effectively.


Pain Points
-----------

Our goal is to discover a customers' pain point,
and then translate it into technical terms.

For example their pain point might be that they've been tasked with
making the website faster because customers were dropping off due to long wait
times.

They've tried to translate this pain point into a set of technical features
for which they are now on the lookout.  Their guess about what they need
may be incorrect, and it's useful to go check things if you can do so quickly.
For example maybe they don't need to invest in a new database product,
but instead they just need a progress bar, or better CSS on their webpage.

If you can discover their pain point then
you're much better equipped to solve their problem effectively.
If you identify a good product fit at this stage then selling is easy.
If you don't then you've avoided a long and fruitless sales process.
