
# Systems

`systems` is a set of tools for describing, running and visualizing
[systems diagrams](https://lethain.com/systems-thinking/). You start
by writing a file describing your system:

    Start(10) > Middle @ 2
    Middle    > End    @ 1

You can also define stocks on their own lines, as opposed to implicitly defining
them within flow definitions:

    Start(10)
    Start  > Middle @ 2
    Middle > End

and then are able to evaluate your system (use `--csv` for an
importable format):

    cat tmp.txt | systems-run -r 3

            Start   Middle  End
    0       10      0       0
    1       8       2       0
    2       6       3       1
    3       4       4       2

You can also export your system into [Graphviz](https://www.graphviz.org/):

    cat tmp.txt | systems-viz

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

    cat tmp.txt | systems-viz | dot -Tpng -o tmp.png
    open tmp.png


## Jupyter notebooks

Likely the easiest way to iterate on a model is within a Jupyter notebook.
See an [example notebook here](./notebooks/hiring.ipynb).
[Read this blog post for more installation details](https://lethain.com/systems-jupyter-notebook/).


## Installation

To install via PyPi:

    pip install systems

To install for local development:

    git clone https://github.com/lethain/systems.git
    cd systems
    python3 -m venv ./env
    source ./env/bin/activate    
    python setup.py develop

Run tests via:

    python3 -m unittest tests/test_*.py

Please open an Github issue if you run into any problems!

## Using the command line tools

Run a model in a file:

    cat tmp.txt | systems-run -r 3

Visualize a model into `dot` for Graphviz:

    cat examples/hiring.txt | systems-viz | dot

## Example: Hiring Funnel

Let's say you wanted to describe your hiring funnel and retention
for a rapidly growing company, you could do so via:

     [PossibleRecruiters] > Recruiters(10, 15) @ 1
     [Candidates] > PhoneScreens @ Recruiters * 3
     PhoneScreens > Onsites      @ 0.5
     Onsites      > Offers       @ 0.5
     Offers       > Hires        @ 0.5
     Hires        > Employees    @ 1.0
     Employees    > Departures   @ 0.1, leak
     Departures   > [Departed]   @ 1.0

Note that you're able to refer to the value of `Recruiters` when specifying
the size of the flow between `Candidates` and `PhoneScreens`. This allows you
to build feedback loops and such!

Then you could run the simulation for 10 rounds:

    cat examples/links.txt | systems-run -r10

            Recruiters      PhoneScreens    Onsites Offers  Hires   Employees       Departures
    0       10              0               0       0       0       0               0
    1       11              30              0       0       0       0               0
    2       12              33              15      0       0       0               0
    3       13              36              16      7       0       0               0
    4       14              39              18      8       3       0               0
    5       15              42              19      9       4       3               0
    6       15              45              21      9       4       7               0
    7       15              45              22      10      4       11              0
    8       15              45              22      11      5       14              1
    9       15              45              22      11      5       18              1
    10      15              45              22      11      5       22              1

You can also get the output as CSV:

    cat examples/links.txt | systems-run -r10 --csv

Which you could... load into a spreadsheet or something to graph!

## Specifying stocks

By default stocks start with a value of zero. For example,
this would have both `a` and `b` would initialize at zero,
and have no maximum limit:

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

You are also able to specify maximum values for each stock by adding
a second parameter. You're not able to specify a maximum without specifying
an initial value, but you can simple use zero for the initial value to
achieve equivalent behavior:

    a(10) > b(0, 5) @ 1

In the above, `a` has no maximum value, but
`b` will only have a capacity of 5.

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

The final and most advanced kind of flow is the `formula` which can use the
value of other stocks along with basic arithmetic to represent arbitrarily
complex relationships (this is a riff on the "link" concept in most system dynamic
software):

    [a] > b @ e * 2
     b  > c @ e
    [d] > e @ 1

In this example, the rate between `a` and `b` is dictated by the value of
the `e` stock.

## Error messages

The parser will do its best to give you a useful error message.
For example, if you're missing delimiters:

    cat examples/no_delim.txt | systems-run
    line 1 is missing delimiter '>': "[a] < b @ 25"

At worst, it will give you the line number and line that is
creating an issue:

    cat examples/invalid_flow.txt | systems-run
    line 1 could not be parsed: "a > b @ 0..2"


## Uploading distribution

If you are trying to install this on PyPi, the steps are roughly:

    python3 -m pip install --user --upgrade pip
    python3 -m pip install --user --upgrade wheel
    python3 -m pip install --user --upgrade twine
    python3 setup.py sdist bdist_wheel
    twine upload --repository-url https://upload.pypi.org/legacy/ dist/*    

That should more or less work. :)

    

