import sys
import argparse

import systems


def parse_stock(model, name):
    name = name.strip()
    infinite = False
    if name.startswith('[') and name.endswith(']'):
        name = name[1:-1]
        infinite = True

    exists = model.get_stock(name)
    if exists:
        return exists
    
    if infinite:
        return model.infinite_stock(name)
    return model.stock(name)

    
def parse_flow(model, src, dest, txt):
    txt = txt.strip()
    if "." in txt:
        rate = systems.Conversion(float(txt))
    else:
        rate = systems.Rate(int(txt))

    return model.flow(src, dest, rate)


def parse(txt):
    m = systems.Model("Parsed")

    stocks = []
    by_name = {}    
    flows = []
    
    for line in txt.split('\n'):
        if line.strip() == "":
            continue
        
        source_name, rest  = line.split(">")
        dest_name, args = rest.split("@")

        source = parse_stock(m, source_name)
        dest = parse_stock(m, dest_name)

        parse_flow(m, source, dest, args)
    
    return m


def main():
    p = argparse.ArgumentParser()
    p.add_argument('-r', '--rounds', type=int, help="number of rounds to run evaluation", default=10)
    args = p.parse_args()

    
    txt = sys.stdin.read()
    model = parse(txt)
    model.run(rounds=args.rounds)
    

if __name__ == "__main__":
    main()
