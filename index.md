---
layout: page
title: Working Notes 
tagline: from Matthew Rocklin
---
{% include JB/setup %}

## Posts

<ul class="posts">
  {% for post in site.posts %}
    {% if post.draft != true %}
    <li><span>{{ post.date | date_to_string }}</span> &raquo; <a href="{{ BASE_PATH }}{{ post.url }}">{{ post.title }}</a></li>
    {% endif %}
  {% endfor %}
</ul>
