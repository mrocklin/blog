---
layout: post
title: Characteristic Functions
tagline: 
category : work 
tags : [SymPy, Stats]
---
{% include JB/setup %}

In a recent post, [Characteristic Functions and scipy.stats](http://jpktd.blogspot.com/2012/12/characteristic-functions-and-scipystats.html), [Josef Perktold](https://github.com/josef-pkt) created functions for the [characteristic functions](http://en.wikipedia.org/wiki/Characteristic_function) of the [Normal](http://en.wikipedia.org/wiki/Normal_distribution) (easy) and [t](http://en.wikipedia.org/wiki/Student%27s_t-distribution) (hard) distributions.  The t-distribution is challenging because the solution involves special functions and has numerically challenging behavior around 0.

Lets see if SymPy can do this work symbolically.  Wikipedia says that the characteristic function $\phi$ of a random variable `X` is defined as follows

$$ \phi_X(t) = E(e^{itX}) $$

It is a function of `t` equal to the expectation of `exp(i*t*X)`.  Lets do this in SymPy

{% highlight python %}
>>> from sympy.stats import *
>>> mu = Symbol('mu', bounded=True)
>>> sigma = Symbol('sigma', positive=True, bounded=True)
>>> X = Normal('X', mu, sigma)
>>> t = Symbol('t', positive=True)

>>> simplify(E(exp(I*t*X)))
              2  2
             σ ⋅t 
     ⅈ⋅μ⋅t - ─────
               2  
   ℯ             
{% endhighlight %}


Wikipedia verifies that this is the correct answer.  I was actually pretty surprised that this worked as smoothly as it did.  SymPy stats wasn't designed to support characteristic functions natively. 

Here are some gists for the [Cauchy](https://gist.github.com/4186685) and [Student-T](https://gist.github.com/4186709) distributions.  Cauchy simplifies down pretty well but the Student-T characteristic function has a few special functions included.

Behavior near zero
------------------

Josef says that the behavior of the characteristic function of the t
distribution near zero for high degrees of freedom (the nu parameter) is
challenging to compute numerically.  Can SymPy handle this symbolically?

{% highlight python %}
>>> nu = Symbol('nu', positive=True, integer=True)
>>> X = StudentT('X', nu)
>>> t = Symbol('t', positive=True)
>>> simplify(E(exp(I*t*X)))
{% endhighlight %}

![](http://goo.gl/a6xcw)

The bold scripted I's are besseli functions.  We restrict this expression to a specific number of degrees of freedom, setting `nu = 50`

    >>> simplify(E(exp(I*t*X))).subs(nu, 50)  # replace nu with 50
             ⎛         ___  ⎞            ⎛        ___  ⎞
    ∞⋅besseli⎝-25, 5⋅╲╱ 2 ⋅t⎠ - ∞⋅besseli⎝25, 5⋅╲╱ 2 ⋅t⎠

Whoops, simple substitution at that number of degrees of freedom fails, giving us infinities.  What if we build the expression with 50 from the beginning?  This gives the integration routines a bit more information when they compute the expectation.

    >>> X = StudentT('X', 50)
    >>> simplify(E(exp(I*t*X)))
            ⎛              │     2  -ⅈ⋅π⎞           ⎛              │     2  ⅈ⋅π⎞
    ╭─╮3, 1 ⎜   1/2        │ 25⋅t ⋅ℯ    ⎟   ╭─╮3, 1 ⎜   1/2        │ 25⋅t ⋅ℯ   ⎟
    │╶┐     ⎜              │ ───────────⎟ + │╶┐     ⎜              │ ──────────⎟
    ╰─╯1, 3 ⎝25, 0, 1/2    │      2     ⎠   ╰─╯1, 3 ⎝25, 0, 1/2    │     2     ⎠
    ────────────────────────────────────────────────────────────────────────────
                            1240896803466478878720000⋅π                         


We find that the solution is in terms of meijer-g functions.  Can we evaluate this close to `t = 0`?

    >>> simplify(E(exp(I*t*X))).subs(t, 1e-6).evalf()
    0.999999999999479 + 1.56564942264937e-29⋅ⅈ

And finally can we plot it?

    >>> plot(re(simplify(E(exp(I*t*X)))), (t, 1e-7, 1e-3))

![]({{ BASE_PATH }}/images/student-t-characteristic-near-zero.png)
