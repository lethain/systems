"""
Tooling to convert a model into a graphviz diagram.
"""
import sys

from graphviz import Digraph

from . import parse
from .errors import ParseException


def as_dot(model, rankdir="LR"):
    mapping = {s.name: str(i) for i, s in enumerate(model.stocks)}
    dot = Digraph(comment=model.name)
    dot.attr(rankdir=rankdir)

    nodes_in_flow = set()

    for flow in model.flows:
        source_id = mapping[flow.source.name]
        destination_id = mapping[flow.destination.name]
        nodes_in_flow.add(source_id)
        nodes_in_flow.add(destination_id)

        dot.edge(source_id, destination_id)

    for stock in model.stocks:
        node_id = mapping[stock.name]
        if node_id in nodes_in_flow:
            dot.node(node_id, stock.name)

    return dot


def main():
    txt = sys.stdin.read()

    try:
        model = parse.parse(txt)
    except ParseException as pe:
        print(pe)
        return

    dot = as_dot(model)
    print(dot.source)


if __name__ == "__main__":
    main()
