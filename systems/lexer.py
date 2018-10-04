import re
import sys
import systems.errors


NEWLINE = "\n"
WHITESPACE = " "
START_INFINITE_STOCK = '['
END_INFINITE_STOCK = ']'
START_PARAMETER_SET = '('
END_PARAMETER_SET = ')'
FLOW_DIRECTION = '>'
FLOW_DELIMITER = '@'
COMMENT = '#'

TOKEN_WHITESPACE = 'whitespace'
TOKEN_LINE = 'line'
TOKEN_NAME = 'name'
TOKEN_VALUE = 'value'
TOKEN_STOCK = 'stock'
TOKEN_STOCK_INFINITE = 'infinite_stock'
TOKEN_FLOW = 'flow'
TOKEN_FLOW_DIRECTION = 'flow_direction'
TOKEN_FLOW_DELIMITER = 'flow_delimiter'
TOKEN_PARAMS = 'params'
TOKEN_WHOLE = 'whole'
TOKEN_DECIMAL = 'decimal'
TOKEN_FORMULA = 'formula'
TOKEN_COMMENT = 'comment'

LEGAL_STOCK_NAME = '[a-zA-Z][a-zA-Z0-9_]*'
PARAM_WHOLE = '\-?[0-9]+'
PARAM_DECIMAL = '[0-9]+\.[0-1]+'


def lex_parameters(txt):
    if txt == "":
        return (TOKEN_PARAMS, tuple())
    elif txt.startswith(START_PARAMETER_SET) and txt.endswith(END_PARAMETER_SET):
        txt = txt[1:-1]
        params = txt.split(',')
        return (TOKEN_PARAMS, tuple([lex_parameter(x) for x in params]))
    else:
        raise systems.errors.InvalidParameters(txt)

def lex_parameter(txt):
    txt = txt.strip()
    if re.fullmatch(PARAM_WHOLE, txt):
        return (TOKEN_WHOLE, txt)
    elif re.fullmatch(PARAM_DECIMAL, txt):
        return (TOKEN_DECIMAL, txt)
    else:
        return (TOKEN_FORMULA, txt)

def lex_caller(token, txt):
    txt = txt.strip()
    match = re.match(LEGAL_STOCK_NAME, txt)
    if not match:
        raise systems.errors.IllegalStockName(txt, LEGAL_STOCK_NAME)
    
    name = match.group(0)
    rest = txt[match.end(0):]
    if rest != "" and not (rest.startswith(START_PARAMETER_SET) and rest.endswith(END_PARAMETER_SET)):
        raise systems.errors.IllegalStockName(txt, LEGAL_STOCK_NAME)
    
    params = lex_parameters(rest)
    return (token, name, params)

def lex_stock(txt):
    txt = txt.strip()
    if txt.startswith(START_INFINITE_STOCK) and txt.endswith(END_INFINITE_STOCK):
        return (TOKEN_STOCK_INFINITE, txt[1:-1], (TOKEN_PARAMS, []))
    else:
        return lex_caller(TOKEN_STOCK, txt)


def lex_flow(txt):
    # coercing flow parameters into same format as stock
    # parameters, which admittedly does feel like a bit of
    # a crummy hack
    #txt = '(' + txt.strip() + ')'

    txt = txt.strip()
    if txt.endswith(END_PARAMETER_SET):
        
        return lex_caller(TOKEN_FLOW, txt)
    else:
        return (TOKEN_FLOW, '', lex_parameters('('+txt+')'))


def lex(txt):
    # to eliminate edge cases, every txt starts with
    # a whitespace and ends with a newline
    txt = " " + txt + "\n"

    tokens = []
    line = []
    char_buff = txt[0]
    parsing = TOKEN_STOCK

    line_num = 1
    for c in txt[1:]:
        prev = char_buff[-1]
        if c == COMMENT and not line:
            parsing = TOKEN_COMMENT
        elif parsing == TOKEN_COMMENT:
            if c == NEWLINE:
                line.append((TOKEN_COMMENT, char_buff[1:]))
                char_buff = WHITESPACE
        elif parsing == TOKEN_STOCK:
            if c == FLOW_DIRECTION:
                # if you encounter a flow_direction, you must encounter a flow
                line.append(lex_stock(char_buff))
                line.append((TOKEN_FLOW_DIRECTION, c))
                c = WHITESPACE
                char_buff = WHITESPACE
                parsing = TOKEN_STOCK
            if c == FLOW_DELIMITER:
                line.append(lex_stock(char_buff))
                line.append((TOKEN_FLOW_DELIMITER, c))
                c = WHITESPACE
                char_buff = WHITESPACE
                parsing = TOKEN_FLOW
            elif c == NEWLINE:
                if char_buff != WHITESPACE:
                    line.append(lex_stock(char_buff))
                char_buff = WHITESPACE
        elif parsing == TOKEN_FLOW:
            if c == NEWLINE:
                if char_buff != WHITESPACE:
                    line.append(lex_flow(char_buff))
                char_buff = WHITESPACE

        if c == NEWLINE:
            line_num += 1
            if char_buff != WHITESPACE:
                raise Exception("unused char_buff: %s" % char_buff)
            if line:
                tokens.append((TOKEN_LINE, line_num, line))
            line = []
            parsing = TOKEN_STOCK
            char_buff = WHITESPACE
        elif c in (WHITESPACE, FLOW_DIRECTION) and not parsing == TOKEN_COMMENT:
            continue
        else:
            char_buff += c
    return tokens


def main():
    txt = sys.stdin.read()
    tokens = lex(txt)
    for token in tokens:
        print(token)


if __name__ == "__main__":
    main()
