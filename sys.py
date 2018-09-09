class Stock(object):
    def __init__(self, name, initial=0):
        self.name = name
        self.initial = initial

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.name)


class Flow(object):
    def __init__(self, source, destination, rate):
        self.source = source
        self.destination = destination
        self.rate = rate

    def __repr__(self):
        return "%s(%s to %s at %s)" % (self.__class__.__name__, self.source, self.destination, self.rate)
        

class Rate(object):
    def __init__(self, velocity):
        self.velocity = velocity

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.velocity)


class State(object):
    def __init__(self, model):
        self.round = 0
        self.model = model
        self.state = {}
        for stock in self.model.stocks:
            self.state[stock.name] = stock.initial

    def advance(self):
        self.round += 1


    def snapshot(self):
        return self.state.copy()

    def __str__(self):
        s = "%s\t" % self.round
        stocks = ["%s(%s)" % (x.name, self.state[x.name]) for x in  self.model.stocks]
        return s + ", ".join(stocks)


class Model(object):
    "Models contain and runs stocks and flows."
    def __init__(self, name):
        self.name = name
        self.stocks = []
        self.flows = []

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

        header = "\t"
        header += "\t".join([s.name for s in self.stocks])
        col_size = [len(s.name) for s in self.stocks]
        
        print(header)
        for i, snapshot in enumerate(snapshots):
            row = "%s" % i
            for j, col in enumerate(self.stocks):
                row += "\t" + str(snapshot[col.name]).ljust(col_size[j])
            print(row)
            
            
            
def main():
    m = Model("Hiring funnel")
    candidates = m.stock("Candidates", 10)
    screens = m.stock("Phone Screen")
    onsites = m.stock("Onsites")

    r = Rate(1)
    m.flow(candidates, screens, Rate(2))
    m.flow(screens, onsites, Rate(1))

    m.run()
    

        
if __name__ == "__main__":
    main()
