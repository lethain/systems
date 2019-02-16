import re
import sys
import pprint
import systems.errors


NEWLINE = "\n"
WHITESPACE = " "
START_INFINITE_STOCK = '['
END_INFINITE_STOCK = ']'
START_PAREN = START_PARAMETER_SET = '('
END_PAREN = END_PARAMETER_SET = ')'
FLOW_DIRECTION = '>'
FLOW_DELIMITER = '@'
COMMENT = '#'
INFINITY = 'inf'

TOKEN_WHITESPACE = 'whitespace'
TOKEN_LINES = 'lines'
TOKEN_LINE = 'line'
TOKEN_NAME = 'name'
TOKEN_STOCK = 'stock'
TOKEN_STOCK_INFINITE = 'infinite_stock'
TOKEN_FLOW = 'flow'
TOKEN_FLOW_DIRECTION = 'flow_direction'
TOKEN_FLOW_DELIMITER = 'flow_delimiter'
TOKEN_PARAMS = 'params'
TOKEN_WHOLE = 'whole'
TOKEN_DECIMAL = 'decimal'
TOKEN_INFINITY = 'inf'
TOKEN_REFERENCE = 'reference'
TOKEN_FORMULA = 'formula'
TOKEN_OP = 'operation'
TOKEN_COMMENT = 'comment'

LEGAL_STOCK_NAME = '[a-zA-Z][a-zA-Z0-9_]*'
PARAM_WHOLE = '\-?[0-9]+'
PARAM_DECIMAL = '[0-9]+\.[0-9]+'
OPERATIONS = '[\/\+\-\*]'


def lex_value(txt):
    "Lex a single value. One of: WHOLE, DECLINE, REFERENCE."
    txt = txt.strip()
    if txt == INFINITY:
        return (TOKEN_INFINITY, txt)
    elif re.fullmatch(PARAM_WHOLE, txt):
        return (TOKEN_WHOLE, txt)
    elif re.fullmatch(PARAM_DECIMAL, txt):
        return (TOKEN_DECIMAL, txt)
    else:
        return (TOKEN_REFERENCE, txt)


def lex_formula(txt):
    groups = []
    tokens = []
    acc = ""
    for c in txt.strip() + NEWLINE:
        if c == START_PAREN:
            groups.append(tokens)
            tokens = []
        elif c == END_PAREN:
            if acc:
                tokens.append(lex_value(acc))
            acc = ""
            prev_tokens = groups.pop()
            prev_tokens.append((TOKEN_FORMULA, tokens))
            tokens = prev_tokens
        elif c in (WHITESPACE, NEWLINE):
            if acc:
                tokens.append(lex_value(acc))
            acc = ""
        elif re.fullmatch(OPERATIONS, c):
            if acc:
                tokens.append(lex_value(acc))
                acc = ""
            tokens.append((TOKEN_OP, c))
        else:
            acc += c

    return (TOKEN_FORMULA, tokens)


def lex_parameters(txt):
    if txt == "":
        return (TOKEN_PARAMS, tuple())
    elif txt.startswith(START_PARAMETER_SET) and txt.endswith(END_PARAMETER_SET):
        txt = txt[1:-1]
        params = txt.split(',')
        return (TOKEN_PARAMS, tuple([lex_formula(x) for x in params]))
    else:
        raise systems.errors.InvalidParameters(txt)

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

    match = re.match(LEGAL_STOCK_NAME, txt)
    if match and txt[len(match.group(0)):].startswith(START_PARAMETER_SET) and txt.endswith(END_PARAMETER_SET):
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

    line_num = 0
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
    return (TOKEN_LINES, tokens)


def readable(token, class_str=None):
    "Create human readable format of lexed tokens."
    kind = token[0]
    if kind == TOKEN_WHITESPACE:
        return WHITESPACE
    elif kind == TOKEN_INFINITY:
        return INFINITY
    elif kind == TOKEN_LINES:
        lines = token[1]
        return "\n".join([readable(x) for x in lines])
    elif kind == TOKEN_FORMULA:
        return " ".join([readable(x) for x in token[1]])
    elif kind == TOKEN_LINE:
        line_tokens = token[2]
        return " ".join([readable(x) for x in line_tokens])
    elif kind in [TOKEN_FLOW_DIRECTION, TOKEN_FLOW_DELIMITER, TOKEN_OP, TOKEN_COMMENT, TOKEN_DECIMAL, TOKEN_WHOLE, TOKEN_REFERENCE]:
        return token[1]
    elif kind == TOKEN_PARAMS:
        params = token[1]
        if len(params) == 0:
            return ""
        joined_params = ", ".join([readable(x) for x in params])
        if not class_str:
            return joined_params
        return "(%s)" % joined_params
    elif kind == TOKEN_STOCK_INFINITE:
        return START_INFINITE_STOCK + token[1] + END_INFINITE_STOCK
    elif kind in [TOKEN_STOCK, TOKEN_FLOW]:
        _, class_str, params = token
        return "%s%s" % (class_str, readable(params, class_str))
    else:
        return "[unexpected token: '%s']" % (token,)


def main():
    txt = sys.stdin.read()
    lexed = lex(txt)
    pprint.pprint(lexed)


if __name__ == "__main__":
    main()
