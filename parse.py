import sys
import argparse

import systems
from exceptions import ParseException, ParseError, MissingDelimiter, UnknownFlowType, NoFlowType, ConflictingValues, DeferLineInfo


def parse_stock(model, name):
    """
    Parse stock name and initial value from text.

    Examples:

    - a is a stock named "a" with an intial value of 0.
    - [a] is an infinite stock named "a"
    - a(50) is a stock named "a" with an initial value of 50.
    """
    name = name.strip()
    infinite = False
    if name.startswith('[') and name.endswith(']'):
        name = name[1:-1]
        infinite = True

    value = 0
    if name.endswith(')'):
        start_pos = name.rfind('(')
        if start_pos > 0:
            value_str = name[start_pos+1:-1]
            name = name[:start_pos]
            value = int(value_str)

    exists = model.get_stock(name)
    if exists:
        if value != 0:
            if exists.initial != value and exists.initial == 0:
                exists.initial = value
            else:
                raise ConflictingValues(name, exists.initial, value)
        return exists

    if infinite:
        return model.infinite_stock(name)
    return model.stock(name, value)


def parse_flow(model, src, dest, txt):
    parts = txt.split(",")
    val = parts[0].strip()

    rate_class = None

    # guess class by value
    try:
        if "." in val:
            val = float(val)            
            rate_class = systems.Conversion
        else:
            val = int(val)            
            rate_class = systems.Rate
    except ValueError:
        pass

    # use specified class if any
    if len(parts) > 1:
        class_str = parts[1].strip()
        if class_str == "leak":
            rate_class = systems.Leak
        elif class_str == "conversion":
            rate_class = systems.Conversion
        elif class_str == "rate":
            rate_class = systems.Rate
        else:
            raise UnknownFlowType(class_str)

    if rate_class is None:
        raise NoFlowType()

    rate = rate_class(val)
    return model.flow(
src, dest, rate)


def parse(txt):
    m = systems.Model("Parsed")

    stocks = []
    by_name = {}
    flows = []

    for n, line in enumerate(txt.split('\n'), 1):
        line = line.strip()
        # ignore comments
        if line == "" or line.startswith("#"):
            continue

        try:
            source_name, rest  = line.split(">")
        except ValueError:
            raise MissingDelimiter(line, n, ">")

        try:
            dest_name, args = rest.split("@")
        except ValueError:
            raise MissingDelimiter(line, n, "@")

        try:
            source = parse_stock(m, source_name)
            dest = parse_stock(m, dest_name)
            parse_flow(m, source, dest, args)
        except DeferLineInfo as dli:
            dli.line = n
            dli.line_number = n
            raise dli
        except Exception:
            raise ParseError(line, n)

    return m


def main():
    p = argparse.ArgumentParser()
    p.add_argument('-r', '--rounds', type=int, help="number of rounds to run evaluation", default=10)
    p.add_argument('--csv', action='store_true', default=False)
    args = p.parse_args()

    txt = sys.stdin.read()

    try:
        model = parse(txt)
    except ParseException as pe:
        print(pe)
        return

    if args.csv:
        model.run(rounds=args.rounds, sep=",", pad=False)
    else:
        model.run(rounds=args.rounds)


if __name__ == "__main__":
    main()
