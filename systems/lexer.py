import sys


NEWLINE = "\n"
WHITESPACE = " "
START_INFINITE_STOCK = '['
END_INFINITE_STOCK = ']'
START_PARAMETER_SET = '('
END_PARAMETER_SET = ')'
FLOW_DIRECTION = '>'
FLOW_DELIMITER = '@'
COMMENT = '#'

ATOM_WHITESPACE = 'whitespace'
ATOM_LINE = 'line'
ATOM_NAME = 'name'
ATOM_VALUE = 'value'
ATOM_STOCK = 'stock'
ATOM_FLOW = 'flow'
ATOM_FLOW_DIRECTION = 'flow_direction'
ATOM_FLOW_DELIMITER = 'flow_delimiter'


def lex(txt):
    # to eliminate edge cases, every txt starts with
    # a whitespace and ends with a newline
    txt = " " + txt + "\n"

    atoms = []
    line = []
    char_buff = txt[0]
    parsing = ATOM_STOCK

    line_num = 1
    for c in txt[1:]:
        prev = char_buff[-1]
        if not line and c == COMMENT:
            line_num += 1
            continue     
        elif parsing == ATOM_STOCK:
            if c == FLOW_DIRECTION:
                # if you encounter a flow_direction, you must encounter a flow
                line.append((ATOM_STOCK, char_buff))
                line.append((ATOM_FLOW_DIRECTION, c))
                c = WHITESPACE
                char_buff = WHITESPACE
                parsing = ATOM_STOCK
            if c == FLOW_DELIMITER:
                line.append((ATOM_STOCK, char_buff))
                line.append((ATOM_FLOW_DELIMITER, c))
                c = WHITESPACE
                char_buff = WHITESPACE
                parsing = ATOM_FLOW
            elif c == NEWLINE:
                if char_buff != WHITESPACE:
                    line.append((ATOM_STOCK, char_buff))
                char_buff = WHITESPACE
        elif parsing == ATOM_FLOW:
            if c == NEWLINE:
                if char_buff != WHITESPACE:
                    line.append((ATOM_FLOW, char_buff))
                char_buff = WHITESPACE            

        if c == NEWLINE:
            line_num += 1            
            if char_buff != WHITESPACE:
                raise Exception("unused char_buff: %s" % char_buff)
            if line:
                atoms.append((ATOM_LINE, line_num, line))
            line = []
            parsing = ATOM_STOCK
            char_buff = WHITESPACE
        elif c in (WHITESPACE, FLOW_DIRECTION):
            continue
        else:
            char_buff += c
    return atoms


def main():
    txt = sys.stdin.read()
    print(lex(txt))


if __name__ == "__main__":
    main()
