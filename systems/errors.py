"""
Custom exceptions for systems package.
"""


class SystemsException(Exception):
    "Base class for systems package."


class ParseException(SystemsException):
    "Base class for parse exceptions."
    pass


class IllegalSystemException(SystemsException):
    "Base class for illegal system configurations."
    pass


class IllegalStockName(SystemsException):
    "Illegal stock name specified."
    def __init__(self, name, allowed):
        self.name = name
        self.allowed = allowed

    def __str__(self):
        return "name '%s' is not a legal stock name, must be of format %s" % (self.name, self.allowed)


class IllegalSourceStock(IllegalSystemException):
    "Source can't be used with this Rate."

    def __init__(self, rate, source):
        self.rate = rate
        self.source = source

    def __str__(self):
        return "stock '%s' can be used as source for rate '%s'" % (
            self.source, self.rate)

class FormulaError(IllegalSystemException):
    "Parent class for formula exceptions."
    def __init__(self, formula):
        self.formula = formula

    def __str__(self):
        return "%s for formula '%s'" % (self.__class__.__name__, self.formula)


class MismatchedParens(FormulaError):
    pass


class CircularReferences(IllegalSystemException):
    def __init__(self, cycle, graph):
        self.cycle = cycle
        self.graph = graph

    def __str__(self):
        return "found cycle '%s' in references '%s'" % (self.cycle, self.graph)


class InvalidFormula(IllegalSystemException):
    def __init__(self, formula, msg):
        self.formula = formula
        self.msg = msg

    def __str__(self):
        return "illegal formula '%s' due to '%s'" % (self.formula, self.msg)


class ParseError(ParseException):
    "Most generic parse error."

    def __init__(self, line="", line_number=0, exception=None):
        self.line = line
        self.line_number = line_number
        self.exception = exception

    def __str__(self):
        s = "line %s could not be parsed: \"%s\"" % (self.line_number, self.line)
        if self.exception is not None:
            s += "\n" + str(self.exception)
        return s


class DeferLineInfo(ParseError):
    pass


class InvalidParameters(DeferLineInfo):
    def __init__(self, txt):
        super().__init__()
        self.txt = txt

    def __str__(self):
        return "line %s specifies invalid parameters '%s': \"%s\"" % (
            self.line_number, self.txt, self.line)



class ConflictingValues(DeferLineInfo):
    "Stock intialized with multiple distinct values."

    def __init__(self, name, first, second):
        super().__init__()
        self.name = name
        self.first = first
        self.second = second

    def __str__(self):
        if self.line_number or self.line:
            return "line %s initializes %s with conflict value %s (was %s): \"%s\"" % (
                self.line_number, self.name, self.second, self.first, self.line)
        else:
            return "'%s' initialized with conflicting value %s (was %s)" % (self.name, self.second, self.first)


class UnknownFlowType(DeferLineInfo):
    "Specified flow type is unknown."

    def __init__(self, flow_type):
        super().__init__()
        self.flow_type = flow_type

    def __str__(self):
        return "line %s has invalid flow type \"%s\": \"%s\"" % (
            self.line_number, self.flow_type, self.line)
