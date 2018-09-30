import math

from .errors import IllegalSourceStock, InitialIsNegative, InitialExceedsMaximum, InvalidFormula


DEFAULT_MAXIMUM = float("+inf")


class Stock(object):
    def __init__(self, name, initial=0, maximum=DEFAULT_MAXIMUM, show=True):
        self.name = name
        self.initial = initial
        self.show = show
        self.maximum = maximum
        self.validate()

    def validate(self):
        if self.initial < 0:
            raise InitialIsNegative(self.initial)

        if self.initial > self.maximum:
            raise InitialExceedsMaximum(self.initial, self.maximum)

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.name)


class Flow(object):
    def __init__(self, source, destination, rate):
        self.source = source
        self.destination = destination
        self.rate = rate
        self.rate.validate_source(self.source)

    def change(self, state, source_state, dest_state):
        capacity = self.destination.maximum - dest_state
        return self.rate.calculate(state, source_state, dest_state, capacity)

    def __repr__(self):
        return "%s(%s to %s at %s)" % (self.__class__.__name__,
                                       self.source, self.destination, self.rate)


class Rate(object):
    def __init__(self, rate):
        self.rate = rate

    def calculate(self, state, src, dest, capacity):
        if src - self.rate >= 0:
            change = self.rate if src - self.rate > 0 else src
            change = min(capacity, change)
            return change, change
        return 0, 0

    def validate_source(self, source_stock):
        "Raise exception is source is not legal."
        return

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.rate)


class Conversion(Rate):
    "Converts a stock into another at a discount rate."

    def calculate(self, state, src, dest, capacity):
        if dest == float("+inf") or capacity == float("+inf"):
            max_src_change = src
        else:
            max_src_change = max(0, math.floor((capacity - dest) / self.rate))

        change = math.floor(max_src_change * self.rate)
        if change == 0:
            return 0, 0
        return max_src_change, change

    def validate_source(self, source_stock):
        if source_stock.initial == float("+inf"):
            raise IllegalSourceStock(self, source_stock)


class Leak(Conversion):
    "A stock leaks a percentage of its value into another."

    def calculate(self, state, src, dest, capacity):
        change = math.floor(src * self.rate)
        if not math.isnan(capacity):
            change = min(capacity, change)
        return change, change


class Formula(Rate):
    "Evaluate a formula reference multiple nodes."
    ops = ["+", "-", "*", "/"]

    def __init__(self, rate):
        super().__init__(0)
        self.formula = rate
        self.elements = self.parse(rate)

    def element_kind(self, string):
        try:
            return ("int", int(string))
        except ValueError:
            pass
        try:
            return ("float", float(string))
        except ValueError:
            pass

        if string in self.ops:
            return ("op", string)
        return ("variable", string)

    def parse(self, formula):
        "Parse formula strings, things like `a * 2` and such."
        ops = ["+", "-", "*", "/"]

        elements = []
        acc = ""
        for char in formula.strip():
            if char == " ":
                if acc:
                    elements.append(self.element_kind(acc))
                acc = ""
            elif char in ops:
                if acc:
                    elements.append(self.element_kind(acc))
                elements.append(self.element_kind(char))
                acc = ""
            else:
                acc += char
        if acc:
            elements.append(self.element_kind(acc))

        # we've built the elements, now to validate them
        acc = False
        op = None
        for kind, value in elements:
            if kind == "op":
                if value not in self.ops:
                    raise InvalidFormula(self.formula, "unknown operator '%s'" % (op,))

                if acc is False:
                    raise InvalidFormula(self.formula, "can't start formula with an operator")
                op = value
                continue

            if acc is False:
                acc = True
                continue

            if acc is True and op is None:
                raise InvalidFormula(self.formula, "must have operation between values")

            if op and kind != "op":
                acc = True
                op = None

        if op is not None:
            raise InvalidFormula(self.formula, "unused operation in formula")

        return elements

    def calculate(self, state, src, dest, capacity):
        acc = None
        op = None
        for kind, value in self.elements:
            if kind == "op":
                op = value
                continue

            if kind == "variable":
                # have to do this validation at run-time because referenced
                # stocks may not exist when flow is first defined
                if value not in state:
                    raise InvalidFormula(self.formula, "referenced variable '%s' does not exist" % (value,))
                value = state[value]

            if acc is None:
                acc = value
                continue

            # if you've reached here, then `op` is specified, `acc` is not None,
            # and it's time to do some math
            if op == '/':
                acc = acc / value
            elif op == '*':
                acc = acc * value
            elif op == '+':
                acc = acc + value
            elif op == '-':
                acc = acc - value
            op = None

        # get into expected format to treat this as a Rate
        self.rate = acc
        return super().calculate(state, src, dest, capacity)
        return 0, 0


class State(object):
    def __init__(self, model):
        self.model = model
        self.state = {}
        for stock in self.model.stocks:
            self.state[stock.name] = stock.initial

    def advance(self):
        deferred = []

        # HACK: in general better to defer starting at end of list
        # then moving forward to support better pipelining,
        # but it's only by convention that earlier things would
        # be declaed earlier, so this is a weak heuristic at best.
        # would be better to anaylze the graph
        for flow in reversed(self.model.flows):
            source_state = self.state[flow.source.name]
            destination_state = self.state[flow.destination.name]
            rem_change, add_change = flow.change(self.state, source_state, destination_state)
            self.state[flow.source.name] -= rem_change
            deferred.append((flow.destination.name, add_change))

        for dest, change in deferred:
            self.state[dest] += change

    def snapshot(self):
        return self.state.copy()


class Model(object):
    "Models contain and runs stocks and flows."

    def __init__(self, name):
        self.name = name
        self.stocks = []
        self.flows = []

    def get_stock(self, name):
        for stock in self.stocks:
            if stock.name == name:
                return stock

    def infinite_stock(self, name):
        s = Stock(name, float("+inf"), show=False)
        self.stocks.append(s)
        return s

    def stock(self, *args, **kwargs):
        s = Stock(*args, **kwargs)
        self.stocks.append(s)
        return s

    def flow(self, *args, **kwargs):
        f = Flow(*args, **kwargs)
        self.flows.append(f)
        return f

    def run(self, rounds=10):
        s = State(self)
        snapshots = [s.snapshot()]
        for i in range(rounds):
            s.advance()
            snapshots.append(s.snapshot())
        return snapshots

    def render_html(self, results):
        rows = ["<table>", "<theader>", "<tr>"]
        col_stocks = [s for s in self.stocks if s.show]
        rows += ["<td><strong>Round</strong></td>"]
        rows += ["<td><strong>%s</strong></td>" % s.name for s in col_stocks]
        rows += ["</tr>", "</theader>", "<tbody>"]

        for i, snapshot in enumerate(results):
            row = "<tr><td>%s</td>" % i
            for j, col in enumerate(col_stocks):
                num = str(snapshot[col.name])
                row += "<td>%s</td>" % num
            row += "</tr>"
            rows.append(row)
        rows += ["</tbody>", "</table>"]
        return "\n".join(rows)

    def render(self, results, sep='\t', pad=True):
        "Render results to string from Model run."
        lines = []

        col_stocks = [s for s in self.stocks if s.show]
        header = sep[:]
        header += sep.join([s.name for s in col_stocks])
        col_size = [len(s.name) for s in col_stocks]
        lines.append(header)

        for i, snapshot in enumerate(results):
            row = "%s" % i
            for j, col in enumerate(col_stocks):
                num = str(snapshot[col.name])
                if pad:
                    num = num.ljust(col_size[j])

                row += sep[:] + num
            lines.append(row)
        return "\n".join(lines)


def main():
    m = Model("Hiring funnel")
    candidates = m.infinite_stock("Candidates")
    screens = m.stock("Phone Screen")
    onsites = m.stock("Onsites")
    offers = m.stock("Offers")
    hires = m.stock("Hires")

    r = Rate(1)
    m.flow(candidates, screens, Rate(2))
    m.flow(screens, onsites, Conversion(0.5))
    m.flow(onsites, offers, Conversion(0.5))
    m.flow(offers, hires, Conversion(0.7))

    rows = m.run()
    print(m.render(rows))


if __name__ == "__main__":
    main()
