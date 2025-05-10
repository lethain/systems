
# Systems

`systems` is a set of tools for describing, running and visualizing
[systems diagrams](https://lethain.com/systems-thinking/).


Installation directions are below, and then get started by [working through the tutorial](./docs/tutorial.md)
or reading through the [Jupyter notebook example](./notebooks/hiring.ipynb) example.

For a more in-depth look at the system syntax, please read [the syntax specification](./docs/spec.md).

## Quickest start

Follow the installation instructions below, then write a system definition
such as:

    Start(10)
    Start  > Middle @ 2
    Middle > End

You can then evaluate your system (use `--csv` for an importable format):

    cat tmp.txt | systems-run -r 3

            Start   Middle  End
    0       10      0       0
    1       8       2       0
    2       6       3       1
    3       4       4       2

See [the tutorial](./docs/tutorial.md) for more detailed starting information.

## Running in code

It's also possible to write code to run your model, rather than rely on the command line tool.
For example:

    from systems.parse import parse

    def results_for_spec(spec, rounds):
        model = parse(spec)
        results = model.run(rounds=rounds)
        return model, results

    spec = """Start(10)
    Start  > Middle @ 2
    Middle > End"""
    
    model, results = results_for_spec(spec, 10)
    print(results)
    # outputs: [{'Start': 10, 'Middle': 0, 'End': 0}, {'Start': 8, 'Middle': 2, 'End': 0}, ...]

This pattern is particularly useful when running from inside of a Jupyter Notebook,
such as the examples in [`lethain/eng-strategy-models`](https://github.com/lethain/eng-strategy-models).


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

Or run a single test via:

    python3 tests/test_parse.py TestParse.test_parse_complex_formula

Please open an Github issue if you run into any problems!

## Jupyter notebooks

Likely the easiest way to iterate on a model is within a Jupyter notebook.
See an [example notebook here](./notebooks/hiring.ipynb).
To install, follow the installation steps above, and followed by:

    # install graphviz
    brew install graphviz

    # install these additional python packages
    pip install jupyter pandas matplotlib



## Using the command line tools

There are four command line tools that you'll use when creating and debugging
systems/

`systems-run` is used to run models:

    $ cat examples/hiring.txt | systems-run -r 3
    PhoneScreens    Onsites Offers  Hires   Employees       Departures
    0       0               0       0       0       5               0
    1       25              0       0       0       5               0
    2       25              12      0       0       5               0
    3       25              12      6       0       5               0

`systems-viz` is used to visualize models into [Graphviz](https://www.graphviz.org/):

    $ cat examples/hiring.txt | systems-viz
    // Parsed
    digraph {
      rankdir=LR
      0 [label=Candidates]
      1 [label=PhoneScreens]
      // etc, etc, some other stuff
    }

Typically you'll pipe the output of `systems-viz` into `dot`, for example

    $ cat examples/hiring.txt | systems-viz | dot -Tpng -o tmp.png

`systems-format` reads in a model, tokenizes it and formats the tokens
into properly formatted results. This is similar to `gofmt`, and could
be used for ensuring a consistent house formatting style for your diagrams.
(It was primarily implemented to support generating human readable error
messages instead of surfacing the tokens to humans when errors arise.)

    $ cat examples/hiring.txt | systems-fmt
    [Candidates] > PhoneScreens @ 25
    PhoneScreens > Onsites @ 0.5
    # etc etc

`systems-lex` generates the tokens for a given system file.
This is typically most useful when you're extending the lexer
to support new types of functionality, but can also be useful
for other kinds of debugging:

    $ cat examples/hiring.txt | systems-lex
    ('lines',
       [('line',
         1,
         [('comment', '# wrap with [] to indicate an infinite stock that')]),
        ('line', 2, [('comment', "# isn't included in each table")]),
	('line', 3, [('comment', '# integers are implicitly steady rates')]),
	('line',
	 4,
         [('infinite_stock', 'Candidates', ('params', [])),
	  ('flow_direction', '>'),
          ('stock', 'PhoneScreens', ('params', ())),
          ('flow_delimiter', '@'),
          ('flow', '', ('params', (('formula', [('whole', '25')]),)))]),
	...
      ]
    )


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



## Syntax Specification

The full the syntax specification is available in [./docs/spec.md](./docs/spec.md),
and is replicated here to make this library easier to drive with an LLM.

---

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
