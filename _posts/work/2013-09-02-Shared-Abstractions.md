---
layout: post
title:  Dictionaries v. Objects
tagline:  a story of shared abstractions
category : work 
tags : [Functional]
---
{% include JB/setup %}

Shannon Behrens recently published a [brief post](http://jjinux.blogspot.com/2013/08/python-dicts-vs-classes.html) on the use of dictionaries and objects to store named data.  He raised the following question:

**At what point do we transition from core data representations like `dicts` to custom data representations with custom classes**

Choices in data representation interests me quite a bit.  I think that the mechanisms we choose to store and share data strongly impact the longevity of the code that we write.

Let's borrow Shannon's book example to compare two common options of data representation

{% highlight python %}
" Book object "                                 " Plain Dictionary "

class Book(object):
    def __init__(self, authors, title, isbn):
        self.authors = authors
        self.title = title
        self.isbn = isbn
                                                book = {
book = Book(["Neil Gaiman"],                        "authors": ["Neil Gaiman"], 
            "American Gods",                        "title": "American Gods",
            "9780062113450")                        "isbn": "9780062113450"
                                                }
}
{% endhighlight %} 

Shannon advocates that you should "Keep it Simple" (left) for simple data structures but that, once things become more complex, you should transition to an object (right).

I think that most Python programmers would agree with this sentiment.  It's unclear (and thus interesting) exactly when this transition occurs though.  Personally I use core data structures (like `dict`) to represent almost all of my data.  I create new classes very rarely.  I support this practice because I believe in the power of shared abstractions.  I'll explain what I mean in a moment.


### Advantages of Objects

To start, lets state some of the virtues of objects (this is a very incomplete list.)

*   Historically they're just more commonly used for complex data.  It's important to maintain coding standards that existing programmers find comfortable.

*   The attribute syntax is a lot nicer

        book["authors"]      # 11 characters to get attribute, 4 of them awkward to type
        book.authors         #  8 characters to get attribute, all of them common 

*   We can add functionality/methods to the objects in a controlled namespace.  For example

        book.open()         .open clearly belongs to book
        open(book)          open conflicts with standard Python file open function

The attribute syntax note is convenient but not a game-changer.  The ability to associate a set of functions with the object (and reuse these functions on inherited classes) is really where objects shine.  To emulate this behavior with core data structures you need to respect namespaces

    import bookpy
    bookpy.open(book)

And culturally many of us (myself included) are pretty bad at this.


### Advantages of Dicts

There are some small advantages to using dicts like the following

*   Literal syntax, we can jump right in and write down dicts without setting up a class first.
*   Efficient implementation (dicts are *really* fast)

But, like the object attribute syntax these are merely convenient.  

The major reason to prefer core data structures is that they are an abstraction shared among all Python programmers.  As a result you can depend on standard code to just work on your data.

For example we can serialize our data into JSON if, for example, we wanted to serialize it and send it over the internet.

{% highlight python %}
>>> import json
>>> book = {
...     "authors": ["Neil Gaiman"],
...     "title": "American Gods",
...     "isbn": "9780062113450"
... }
>>> json.dumps(book)
'{"title": "American Gods", "isbn": "9780062113450", "authors": ["Neil Gaiman"]}'
{% endhighlight %} 

The `json` library fails to transform our `book` object however.

{% highlight python %}
>>> import json
>>> book = Book(["Neil Gaiman"], "American Gods", "9780062113450")
>>> json.dumps(book)
TypeError: <__main__.Book object at 0x10e4410> is not JSON serializable
{% endhighlight %} 

This is to be expected.  The `json` library developers have not seen our Book class.  No one has but us.

While we may not think we need `json` encoding it's likely that if our project succeeds then someone will want to send our objects over the internet.  The decision to make a custom class shuts our project off from the rest of the development ecosystem.

Custom classes inhibit interoperation with other libraries.  This limits growth out to unanticipated applications.  This is particularly tragic because our field thrives on connecting isolated components.  Shared abstractions serve as the connection links, like the regular bumps and divots in LEGO pieces.  Shared abstractions allow us to connect cool modules to create novel cool projects with ease.  Otherwise we're stuck hacking together missing technology (like a `Book.write_json` method) when perfectly adequate solutions (like `json.dumps`) already exist.

This example isn't restricted to JSON encoding, in general we're going to have to hack something together every time we want the Book objects to interact with foreign code.  This problem compounds as we begin to rely on more and more external projects.


### Custom Shared Abstractions

Sometimes building custom classes is worth it.  This is certainly the case when you have a large developer base that can all agree on exactly the interface they want to use.  LEGO piece bumps aren't the right fit for everyone.  If you have a large community you can establish other cool interfaces (like Lincoln Logs or Tinker Toys) but only if you have sufficient market power to do so.  No one buys the off-brand LEGOs that don't quite fit.

The `numpy.ndarray` object is a perfect example of a custom class that has become a shared abstraction for the entire scientific computing ecosystem.  Object orientation provided convenient syntax and intelligent method handling of `numpy.ndarrays` and `numpy.matrix`.  I think that these features were key to this module's wide adoption/success and a clear win for the object oriented crowd.  

In short, I think that new classes are really awesome but only in really rare cases.  They should be used sparingly.  If you're developing for the Librarian Developers of the World then by all means, make an awesome, fully featured book class; otherwise try sticking with core data structures.  You'll be happy later on as you leverage standard libraries for unanticipated applications.


### Best of Both Worlds (or, Fancy Solutions)

You can implement shared abstractions on top of custom classes.  For example you can implement the `iterable` abstraction by implementing an `__iter__` method on your class, allowing other foreign modules to leverage your custom data type without any trouble.  The `namedtuple` function in `collections` might be a good fit for the `book` application above.  

Also, it's worth noting that JavaScript handles this problem in a curious way.  Objects and dictionaries are equivalent.  It's an interesting direction and something I suspect we could hack together in Python as well.
