---
layout: post
title: Cloud Lock-in and Open Standards
category: work
tags: [Programming, Python, scipy, dask]
theme: twitter
---

{% include JB/setup %}
*This post is from conversations with [Peter Wang](https://github.com/pzwang),
[Yuvi Panda](https://github.com/yuvipanda), and several others.  Yuvi expresses
his own views on this topic [on his
blog](http://words.yuvi.in/post/oss-in-the-cloud/).*


### Summary

When moving to the cloud we should be mindful to avoid vendor lock-in by
adopting open standards.


### Adoption of cloud computing

Cloud computing is taking over both for-profit enterprises and
public/scientific institutions.  The Cloud is cheap, flexible, requires little
up-front investment, and enables greater collaboration.  Cloud vendors like
Amazon Web Services (AWS), Google Cloud Platform (GCP), and Microsoft Azure
compete to create stable, easy to use platforms to serve the needs of a variety
of institutions, both big and small.  This presents both a great opportunity
for society, but also a risk of future lock-in at a large scale.


### Cloud vendors build services to lock in users

Some of the competition between cloud vendors is about providing lower costs,
higher availability, improved scaling, and so on, that are strictly a benefit
for consumers.  This is great.

However some of the competition is in the form of services that are specialized
to a particular commercial cloud, like Amazon Lambda, Google Tensor Processing
Units (TPUs), or Azure Notebooks.  These services are valuable to enterprise
and public institutions alike, but they lock users in long-term.  If you build
your system around one of these systems then moving to a different cloud in the
future becomes expensive.  This stickiness to your current cloud "locks you in"
to using that particular cloud, even if policies change in the future in
ways that you dislike.

This is OK, lock-in is a standard business practice.  We shouldn't fault these
commercial companies for making good business decisions.  However, it's
something that we should keep in mind as we invest public effort in these
technologies.


### Open standards counter lock-in technologies

One way to counter lock-in is to promote the adoption of open standard
technologies that are shared among cloud platforms.  If these open standard
technologies become popular enough then cloud platforms *must* offer them
alongside their proprietary technologies in order to stay competitive, removing
one of their options for lock-in.


### Examples with Kubernetes and Parquet

For example, consider Kubernetes, a popular resource manager for clusters.
While Kubernetes was originally promoted by Google, it was developed in the
open by a broader community, gained global adoption, and is now available
across all three major commercial clouds.  Today if you write your
infrastructure on Kubernetes you can move your distributed services between
clouds easily, or can move your system onto an on-premises cluster if that
becomes necessary.  You retain the freedom to move around in the future with
low cost.

Consider also the open Parquet data format.  If you store your data in Parquet
then you can move that data between any cloud's storage system easily, or can
move that data to your in-house hardware without going through a painful
database export process.

Technologies like Kubernetes and Parquet displace proprietary technologies like
Amazon's Elastic Container Service (ECS), which locks users into AWS, or
Google's BigQuery which keeps users on GCP with data gravity.  This is fine,
Amazon and Google can still compete for users with any of their other excellent
services, but they've been pushed up the stack a bit, away from technologies
that are infrastructural and towards technologies that are more about
convenience and high-level usability.


### What we can do

Wide adoption of open standard infrastructure protects us from the control of
cloud vendors.

If you are a public institution considering the cloud then please consider the
services that you plan to adopt, and their potential to lock your institutions
in the long run.  These services may still make sense, but you should probably
have a conversation with your team and do it mindfully.  You might consider
developing a plan to extract yourself from that cloud in the future and see how
your decisions affect the cost of that plan.

If you are an open source developer then please consider investing your effort
around open standards instead of around proprietary tooling.  By focusing our
effort on open standards we provide public institutions with viable options for
a safe cloud.
