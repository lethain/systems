import sys
import argparse

import systems.models
import systems.lexer as lexer
from systems.errors import ParseException, ParseError, UnknownFlowType, ConflictingValues, DeferLineInfo


def parse_stock(model, name):
    """
    Parse stock name and initial value from text.

    Examples:

    - a is a stock named "a" with an intial value of 0.
    - [a] is an infinite stock named "a".
    - a(50) is a stock named "a" with an initial value of 50.
    - a(5, 10) is a stock named "a' with innitia lvalue of 5
      and maximum value of 10.
    """
    name = name.strip()
    infinite = False
    if name.startswith('[') and name.endswith(']'):
        name = name[1:-1]
        infinite = True

    value = 0
    maximum = systems.models.DEFAULT_MAXIMUM
    if name.endswith(')'):
        start_pos = name.rfind('(')
        if start_pos > 0:
            value_str = name[start_pos + 1:-1]
            name = name[:start_pos]

            # handle (10, 20) format
            if ',' in value_str:
                front, tail = value_str.split(',')
                maximum = int(tail.strip())
                value_str = front
            value = int(value_str)

    exists = model.get_stock(name)
    if exists:
        if value != 0:
            if exists.initial != value and exists.initial == 0:
                exists.initial = value
            else:
                raise ConflictingValues(name, exists.initial, value)
        if maximum != systems.models.DEFAULT_MAXIMUM:
            if exists.maximum != maximum and exists.maximum == systems.models.DEFAULT_MAXIMUM:
                exists.maximum = maximum
            else:
                raise ConflictingValues(name, exists.maximum, maximum)
        exists.validate()
        return exists

    if infinite:
        return model.infinite_stock(name)
    return model.stock(name, value, maximum)


def parse_flow(model, src, dest, txt):
    parts = txt.split(",")
    val = parts[0].strip()

    rate_class = None

    # guess class by value
    try:
        if "." in val:
            val = float(val)
            rate_class = systems.models.Conversion
        else:
            val = int(val)
            rate_class = systems.models.Rate
    except ValueError:
        pass

    # use specified class if any
    if len(parts) > 1:
        class_str = parts[1].strip()
        if class_str == "leak":
            rate_class = systems.models.Leak
        elif class_str == "conversion":
            rate_class = systems.models.Conversion
        elif class_str == "rate":
            rate_class = systems.models.Rate
        else:
            raise UnknownFlowType(class_str)

    if rate_class is None:
        rate_class = systems.models.Formula

    rate = rate_class(val)
    return model.flow(
        src, dest, rate)


def parse(txt):
    m = systems.models.Model("Parsed")
    stocks = []
    by_name = {}
    flows = []

    tokens = lexer.lex(txt)
    for _, n, line in tokens:
        first_stock = None
        second_stock = None

        try:        
            for atom, data in line:
                if atom == lexer.ATOM_STOCK:
                    if first_stock is None:
                        first_stock = parse_stock(m, data)
                    elif second_stock is None:
                        second_stock = parse_stock(m, data)
                elif atom == lexer.ATOM_FLOW:
                    parse_flow(m, first_stock, second_stock, data)
        except DeferLineInfo as dli:
            dli.line = line
            dli.line_number = n
            raise dli
        except Exception as e:
            raise ParseError(line, n, e)        

    return m


def main():
    p = argparse.ArgumentParser()
    p.add_argument(
        '-r',
        '--rounds',
        type=int,
        help="number of rounds to run evaluation",
        default=10)
    p.add_argument('--csv', action='store_true', default=False)
    args = p.parse_args()

    txt = sys.stdin.read()

    try:
        model = parse(txt)
    except ParseException as pe:
        print(pe)
        return

    results = model.run(rounds=args.rounds)
    kwargs = {}
    if args.csv:
        kwargs['sep'] = ','
        kwargs['pad'] = False
    print(model.render(results, **kwargs))


if __name__ == "__main__":
    main()
