---
layout: post
title:  Dictionaries v. Objects
tagline:  a story of shared abstractions
category : work 
tags : [Functional]
draft: true
---
{% include JB/setup %}

Shannon Behrens recently published a [brief post](http://jjinux.blogspot.com/2013/08/python-dicts-vs-classes.html) on the use of dictionaries and objects to store named data.  In his example he used book data as an example to compare the two

{% highlight python %}
books = [{
    "authors": ["Neil Gaiman"],
    "title": "American Gods",
    "isbn": "9780062113450"
}]
{% endhighlight %} 

He states that dictionaries are preferable for simple data in order to keep things simple but that one should transition to objects when things get more complicated.  It's unclear when this transition occurs though.  In general I agree that we should keep data structures simple and use dicts when dicts suffice.  However I also think that dicts can go very far and that one should avoid using objects for these simple sorts of one-off data collections.

### Advantages of Objects

First, lets state some of the virtues of objects (this is a very incomplete list.)

*   Historically they're just more commonly used.  Familiarity and maintaining standards is a good thing.

*   The attribute syntax is nicer

        book["authors"]      # 11 characters to get attribute, 4 of them awkward to type
        book.authors         #  8 characters to get attribute, all of them common 

*   We can add functionality/methods to the objects in a controlled namespace.  For example

        book.open()         .open clearly belongs to book
        open(book)          open conflicts with standard Python file open function

### Disadvantages of Objects

Really I'm just going to name one, but it's a big one.  Actually, I think that this is a really big deal.  Custom classes often fail to implement a *shared abstraction*.  That is, no one else's code knows how to interoperate with your custom Book class.  A brief example demonstrates this point.

Suppose that want to send our book data over the internet.  To send the book data we serialize it to a JSON string

{% highlight python %}
>>> import json
>>> book = {
...     "authors": ["Neil Gaiman"],
...     "title": "American Gods",
...     "isbn": "9780062113450"
... }
>>> json.dumps(book)
'{"title": "American Gods", "isbn": "9780062113450", "authors": ["Neil Gaiman"]}'

>>> book = Book(...)
>>> json.dumps(book)
TypeError: <__main__.Book object at 0x10e4410> is not JSON serializable
{% endhighlight %} 

What happened here?  The `json` library did not know how to serialize our object of the Book class.  That's reasonable, the makers of the `json` library had never seen our Book class before.  If we look at the docs for the JSON encoder we find that it supports all standard types and offers instructions on how to extend support to custom types.

    >>> help(json.JSONEncoder)
    Extensible JSON <http://json.org> encoder for Python data structures.

    Supports the following objects and types by default:

    +-------------------+---------------+
    | Python            | JSON          |
    +-------------------+---------------+
    | list, tuple       | array         |
    +-------------------+---------------+
    | str, unicode      | string        |
    +-------------------+---------------+
    | int, long, float  | number        |
    +-------------------+---------------+
    | True              | true          |
    +-------------------+---------------+
    | False             | false         |
    +-------------------+---------------+
    | None              | null          |
    +-------------------+---------------+

    To extend this to recognize other objects, subclass and implement a
    ``.default()`` method with another method that returns a serializable
    object for ``o`` if possible, otherwise it should call the superclass
    implementation (to raise ``TypeError``).

So as long as we stick to the standard Python types we can depend on the `json` library to work flawlessly.  If we want to use a custom class *and* use `json` then we have to do some extra work.  I tried subclassing `json.JSONEncoder` for the example but gave up pretty quickly.

This example isn't restricted to JSON encoding, in general we're going to have to hack something together every time we want the Book objects to interact with foreign code.  This problem compounds as we begin to rely on more and more external projects.


### Custom Shared Abstractions

Of course, sometimes building custom classes is worth it.  This is certainly the case when you have a large developer base that can all agree on exactly the interface they want to define.  The `numpy.ndarray` object is a perfect example of a custom class that has become a shared abstraction for the entire scientific computing ecosystem.

Object orientation provides convenient syntax and intelligent method handling of `numpy.ndarrays` and `matrices`.  I think that these features were key to this module's wide adoption/success and a clear win for the object oriented crowd.  

Object Oriented programming has come under fire in the last few years.  That's certainly not my intention here.  Classes have a number of virtues but they can also be overused.  In particular we need to be aware that they limit interoperation with unanticipated external code.

In short, if you have a community of book developers then you should get together and come up with (and agree on!) a shared Book class; otherwise you should endeavor to stick with core types so that you can leverage the powerful standard libraries.


### Final notes 

Thanks to Shannon for bringing up this topic.  I especially appreciate the concise nature of his post.  I'd love to read other pithy posts in the future.

Also, commenters to his post brought up the `namedtuple` function, a great compromise.
