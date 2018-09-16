import math

from exceptions import IllegalSourceStock


DEFAULT_MAXIMUM = float("+inf")


class Stock(object):
    def __init__(self, name, initial=0, maximum=DEFAULT_MAXIMUM, show=True):
        self.name = name
        self.initial = initial
        self.show = show
        self.maximum = maximum

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.name)


class Flow(object):
    def __init__(self, source, destination, rate):
        self.source = source
        self.destination = destination
        self.rate = rate
        self.rate.validate_source(self.source)

    def change(self, source_state, dest_state):
        capacity = self.destination.maximum - dest_state        
        return self.rate.calculate(source_state, dest_state, capacity)

    def __repr__(self):
        return "%s(%s to %s at %s)" % (self.__class__.__name__, self.source, self.destination, self.rate)


class Rate(object):
    def __init__(self, rate):
        self.rate = rate

    def calculate(self, src, dest, capacity):
        if src - self.rate >= 0:
            change = min(self.rate, src - self.rate)
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
    def calculate(self, src, dest, capacity):
        # TODO: support capacity
        change = math.floor(src * self.rate)
        if change == 0:
            return 0, 0
        return src, math.floor(src * self.rate)

    def validate_source(self, source_stock):
        if source_stock.initial == float("+inf"):
            raise IllegalSourceStock(self, source_stock)


class Leak(Conversion):
    "A stock leaks a percentage of its value into another."
    def calculate(self, src, dest, capacity):
        change = math.floor(src * self.rate)
        change = min(capacity, change)        
        return change, change


class State(object):
    def __init__(self, model):
        self.model = model
        self.state = {}
        for stock in self.model.stocks:
            self.state[stock.name] = stock.initial

    def advance(self):
        deferred = []

        for flow in self.model.flows:
            source_state = self.state[flow.source.name]
            destination_state = self.state[flow.destination.name]
            rem_change, add_change = flow.change(source_state, destination_state)
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
    hires= m.stock("Hires")

    r = Rate(1)
    m.flow(candidates, screens, Rate(2))
    m.flow(screens, onsites, Conversion(0.5))
    m.flow(onsites, offers, Conversion(0.5))
    m.flow(offers, hires, Conversion(0.7))

    rows = m.run()
    print(m.render(rows))


if __name__ == "__main__":
    main()
