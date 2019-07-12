
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

Or run a single test via:

    python3 tests/test_parse.py TestParse.test_parse_complex_formula

Please open an Github issue if you run into any problems!

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
