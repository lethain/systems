import sys
import systems


def parse_stock(model, name):
    name = name.strip()
    infinite = False
    if name.startswith('[') and name.endswith(']'):
        name = name[1:-1]
        infinite = True

    if not model.stock_exists(name):
        if infinite:
            return model.infinite_stock(name)
        return model.stock(name)


def parse(txt):
    m = systems.Model("Parsed")

    stocks = []
    by_name = {}    
    flows = []
    
    for line in txt.split('\n'):
        if len(line.strip()) == 0:
            continue
        
        source_name, rest  = line.split(">")
        dest_name, args = rest.split("@")

        source = parse_stock(m, source_name)
        dest = parse_stock(m, dest_name)
        
        print([source, dest, args])


    
    return m


def main():
    txt = sys.stdin.read()
    model = parse(txt)
    model.run()
    

if __name__ == "__main__":
    main()
