
# Systems

`systems` is a set of tools for describing, running and visualizing
[systems diagrams](https://lethain.com/systems-thinking/).


Installation directions are below, and then get started by [working through the tutorial](./docs/tutorial.md)
or reading through the [Jupyter notebook example](../notebooks/hiring.ipynb) example.

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

Please open an Github issue if you run into any problems!

## Using the command line tools

Run a model in a file:

    cat tmp.txt | systems-run -r 3

Visualize a model into `dot` for Graphviz:

    cat examples/hiring.txt | systems-viz | dot


## Uploading distribution

If you are trying to install this on PyPi, the steps are roughly:

    python3 -m pip install --user --upgrade pip
    python3 -m pip install --user --upgrade wheel
    python3 -m pip install --user --upgrade twine
    python3 setup.py sdist bdist_wheel
    twine upload --repository-url https://upload.pypi.org/legacy/ dist/*

That should more or less work. :)
