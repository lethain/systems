import sys
import systems


def parse(txt):
    m = systems.Model("Parsed")
    
    return m


def main():
    txt = sys.stdin.read()
    model = parse(txt)
    model.run()
    

if __name__ == "__main__":
    main()
