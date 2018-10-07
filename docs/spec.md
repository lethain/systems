## Language specification

This file specifies the language used for describing systems in `systems`.
There are three primary kinds of objects to specify:

* `stocks` hold values, and
* `flows` transition values from one stock to another.
* finally, `formula` are used to describe initial and maximum values for stocks,
    and the magnitude of flows.


## Specifying stocks

Stocks are specified on their own line, or implicitly in flow declarations:

    MyStock

This would create a stock named `MyStock` with an initial value of zero and
a maximum value of infinity:

    OtherStock(10)

You can also specify maximum values:

    ThirdStock(0, 10)

This would create `ThirdStock` with an initial value of zero, and a maximum value of ten.

Going back to `OtherStock` for a moment, you can also use the special literal `inf`
to explicitly specify its maximum value:

    OtherStock(10, inf)

This is a more explicit way to specify a stock with an infinite maximum.
Generally it's a strange indicator if you're using the `inf` literal directly,
and instead you'd use the special syntax for infinite flows:

    [InfiniteFlow]

This `InfiniteFlow` would have initial and maximum values of infinity.

Without going too far into the details, initial and maximums can be specified using any
legal formula, more on formulas below:

    Managers(2)
    Engineers(Managers * 4, Managers * 8)

In many cases, though, you'll end up specifying your stocks inline in your
flows, as opposed to doing them on their own lines, but the syntax
is the same.

## Flows

For example, this would have both `a` and `b` would initialize at zero,
and both would have infinite maximum values, in addition there would be
a flow of one unit per round from `a` to `b` (assuming that `a` is above zero):

    a > b @ 1

In the above example, `a` has an initial value of zero, so it would never
do anything. Most working systems address that problem by starting with
an infinite stock:

    [a] >  b  @ 5
     b  > [c] @ 3

In the above, `a` and `c` would be infinite, and `b` would start
with a value of zero. You can also solve the empty start problem
by specifying non-zero initial values for your stocks:

    a(10) > b(3)  @ 5
    b     > c(12) @ 1
    c     > a

In this example, `a` is initialized at 10, `b` at 3, and `c` at 12.
Note that you don't have to set the value at first reference. It is legal
to initialize a value at a later definition of a stock, e.g. this is fine:

    a(1) > b @ 5
    b(2) > c @ 3
    c(3) > a @ 1

However, it *is* illegal to initialize the same stock multiple times.

    a(1) > b(2) @ 1
    b(3) > a    @ 1

This will throw an error, because you can't initialize `b` twice with different values!

## Rates, Conversions and Leaks

Each line specifies two nodes and the link between them. Links are described
following the `@` character. The most common type of flow is a `rate`, which
is a fixed transfer of values in one stock to another.

For example, moving two units per round between `a` and `b`:

    # these are equivalent
    a > b @ 2
    a > b @ Rate(2)

Up to two units will be transfered from `a` to `b` each round.

Another common kind of flow is the `conversion` flow, which takes
the entire contents of the source stock and multiplies that value
against the conversion rate, adding the result to the next flow.

    # these are equivalent
    a(10) > b @ 0.5
    a(10) > b @ Conversion(0.5)

The above would multiple `0.5` against `10` and move `5` units to `b`,
with the other `5` units being lost to the conversion rate (e.g. disappearing).
A common example of a conversion rate would be the offer acceptance rate
in a [hiring funnel](https://lethain.com/hiring-funnel/).

The third kind of flow is the `leak`, which combines properties of the
`rate` and `conversion` flows. It moves a fixed percentage of the source
flow into the destination flow, while leaving the remainder intact.

    a(10) > b @ Leak(0.2)

Considering the difference between the `conversion` and `leak`, if the above
were a `conversion`, then the value of `a` after one round would  be `0`, but if it's
a `leak`, then the value would be `8`.

## Formulas

Any flow value, initial value and maximum value can be a formula:

    Recruiters(3)
    Engineers(Managers * 4, Managers * 8)
    [Candidates] > Engineers @ Recruiters * 6
    [Candidates] > Managers  @ Recruiters * 3

The above system shows that `Engineers` has an initial value of `Managers * 4`,
a maximum value of `Managers * 8` and then shows that both `Engineers` and `Managers`
grow at multiples of the value of the `Recruiters` stock.

This is also a good example of using the `Recruiters` stock as
a variable, as it doesn't' actually change over time.
