
# Systems

`systems` is a set of tools for describing, running and visualizing
[systems diagrams](https://lethain.com/systems-thinking/). You start
by writing a file describing your system:

    Start(10) > Middle @ 2
    Middle    > End    @ 1

and then are able to evaluate your system (use `--csv` for an
importable format):

    cat tmp.txt | python parse.py -r 3
    
    Start   Middle  End
    0       10      0       0
    1       8       2       0
    2       6       3       1
    3       4       4       2

You can also export your system into [Graphviz](https://www.graphviz.org/):

    cat tmp.txt | python viz.py
    
    // Parsed
    digraph {
      0 [label=Start]
      1 [label=Middle]
      2 [label=End]
      0 -> 1
      1 -> 2
    }

From there you could push that output through Graphviz's
`dot` renderer to generate a diagram:

    cat tmp.txt | python viz.py | dot -Tpng -o tmp.png
    open tmp.png

If you're trying to render the diagram into a Jupyterhub notebook,
take a [look at the Graphviz docs on rendering in Jupyterhub](https://graphviz.readthedocs.io/en/stable/manual.html#jupyter-notebooks),
and look at the `systems.viz.as_dot` function which takes a model
and return a `Digraph` object that you can call `_repr_svg_()` against
to render.

## Installation

Currently, install via:

    git clone https://github.com/lethain/systems.git
    cd interactions
    python3 -m venv ./env
    source ./env/bin/activate
    pip install -r requirements.txt

I'll also put it up on PyPi at some point, but not quite yet.


## Using the command line tools

Generally, you should be able to accomplish

cat examples/hiring.txt | python viz.py | dot

## Example: Hiring Funnel

Let's say you wanted to describe your hiring funnel and retention
for a rapidly growing company, you could do so via:

     # wrap with [] to indicate an infinite stock that
     # isn't included in each table
     # integers are implicitly steady rates
     [Candidates] > PhoneScreens @ 25

     # floats are implicitly conversions that convert the
     # source stock into the destination stock at a discount
     # e.g. a source at 10 with a 0.5 conversion would empty
     # itself and add 5 units to the destination
     PhoneScreens > Onsites      @ 0.5
     Onsites      > Offers       @ 0.5
     Offers       > Hires        @ 0.5
     Hires        > Employees    @ 1.0

     # specify leak to avoid a destructive conversion
     Employees    > Departures   @ 0.1, leak
     Departures   > [Departed]   @ 1.0

Then you could run the simulation for 15 rounds:

    > cat hiring.txt | python3 parse.py -r15
            PhoneScreens    Onsites Offers  Hires   Employees       Departures
    0       0               0       0       0       0               0
    1       25              0       0       0       0               0
    2       25              12      0       0       0               0
    3       25              12      6       0       0               0
    4       25              12      6       3       0               0
    5       25              12      6       3       3               0
    6       25              12      6       3       6               0
    7       25              12      6       3       9               0
    8       25              12      6       3       12              0
    9       25              12      6       3       14              1
    10      25              12      6       3       16              1
    11      25              12      6       3       18              1
    12      25              12      6       3       20              1
    13      25              12      6       3       21              2
    14      25              12      6       3       22              2
    15      25              12      6       3       23              2


You can also get the output as CSV:

    cat hiring.txt | python3 parse.py -r2 --csv
    ,PhoneScreens,Onsites,Offers,Hires,Employees,Departures
    0,0,0,0,0,0,0
    1,25,0,0,0,0,0
    2,25,12,0,0,0,0

Which you could... load into a spreadsheet or something to graph!

## Specifying stocks

By default stocks start with a value of zero. For example,
this would have both `a` and `b` would initialize at zero:

    a > b @ 1

You can also initialize stocks with an infinite value, which
is typically done for stocks at the beginning and end of a model:

    [a] >  b  @ 5
     b  > [c] @ 3

In the above, `a` and `c` would be infinite, and `b` would start
with a value of zero. However, you can also specify arbitrary
values:

    a(10) > b(3)  @ 5
    b     > c(12) @ 1
    c     > a

In this example, `a` is initialized at 10, `b` at 3, and `c` at 12.
Note that you only need to set the value at first reference. It is legal
to initialize a value at a later definition of a stock, e.g. this is fine:

    a(1) > b @ 5
    b(2) > c @ 3
    c(3) > a @ 1

However, this is only legal when previous initializes specify no value,
an error will be thrown if you attempt to reinitialize a stock at a different
value, e.g. this is illegal:

    a(1) > b(2) @ 1
    b(3) > a    @ 1

You can't initialize `b` twice with different values!

## Flows

Each line specifies two nodes and the link between them. Links are described
following the `@` character. The most common type of flow is a `rate`, which
is a fixed transfer of values in one stock to another.

For example, moving two units per round between `a` and `b`:

    # these are equivalent
    a > b @ 2
    a > b @ 2, leak

Up to two units will be transfered from `a` to `b` each round.

Another common kind of flow is the `conversion` flow, which takes
the entire contents of the source stock and multiplies that value
against the conversion rate, adding the result to the next flow.

    # these are equivalent
    a(10) > b @ 0.5
    a(10) > b @ 0.5, conversion    


The above would multiple `0.5` against `10` and move `5` units to `b`,
with the other `5` units being lost to the conversion rate (e.g. disappearing).
A common example of a conversion rate would be the offer acceptance rate
in a [hiring funnel](https://lethain.com/hiring-funnel/).

The third kind of flow is the `leak`, which combines properties of the
`rate` and `conversion` flows. It moves a fixed percentage of the source
flow into the destination flow, while leaving the remainder intact.

    a(10) > b @ 0.2, leak

Considering the difference between the `conversion` and `leak`, if the above
were a `conversion`, then the value of `a` after one round would  be `0`, but if it's
a `leak`, then the value would be `8`.

## Links

If you want something a bit more sophisticated, you might also want to
include links between a flow and a stock, for example you might want
to model the number of recruiters and use that to influence the phone
screen rate instead of fixing it at a constant value.

Links are... not implemented quite yet.

## Error messages

The parser will do its best to give you a useful error message.
For example, if you're missing delimiters:

    cat examples/no_delim.txt | python parse.py
    line 1 is missing delimiter '>': "[a] < b @ 25"

At worst, it will give you the line number and line that is
creating an issue:

    cat examples/invalid_flow.txt | python parse.py
    line 1 could not be parsed: "a > b @ 0..2"
