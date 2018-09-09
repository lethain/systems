class Stock(object):
    def __init__(self, name, initial=0, show=True):
        self.name = name
        self.initial = initial
        self.show = show

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.name)

    
class Flow(object):
    def __init__(self, source, destination, rate):
        self.source = source
        self.destination = destination
        self.rate = rate

    def change(self, source_state, dest_state):
        return self.rate.calculate(source_state, dest_state)

    def __repr__(self):
        return "%s(%s to %s at %s)" % (self.__class__.__name__, self.source, self.destination, self.rate)


class Rate(object):
    def __init__(self, velocity):
        self.velocity = velocity

    def calculate(self, src, dest):
        if src - self.velocity >= 0:
            return min(self.velocity, src - self.velocity)
        return 0

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.velocity)


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
            change = flow.change(source_state, destination_state)
            self.state[flow.source.name] -= change
            deferred.append((flow.destination.name, change))

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

        
        col_stocks = [s for s in self.stocks if s.show]    
        header = "\t"
        header += "\t".join([s.name for s in col_stocks])
        col_size = [len(s.name) for s in col_stocks]

        print(header)
        for i, snapshot in enumerate(snapshots):
            row = "%s" % i
            for j, col in enumerate(col_stocks):
                row += "\t" + str(snapshot[col.name]).ljust(col_size[j])
            print(row)



def main():
    m = Model("Hiring funnel")
    candidates = m.infinite_stock("Candidates")
    screens = m.stock("Phone Screen")
    onsites = m.stock("Onsites")

    r = Rate(1)
    m.flow(candidates, screens, Rate(2))
    m.flow(screens, onsites, Rate(1))

    m.run()



if __name__ == "__main__":
    main()
