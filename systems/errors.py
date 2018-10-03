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


class IllegalSourceStock(IllegalSystemException):
    "Source can't be used with this Rate."

    def __init__(self, rate, source):
        self.rate = rate
        self.source = source

    def __str__(self):
        return "stock '%s' can be used as source for rate '%s'" % (
            self.source, self.rate)


class InitialExceedsMaximum(IllegalSystemException):
    "Initial value for stock can't be greater than maximum value."
    def __init__(self, initial, maximum):
        self.initial = initial
        self.maximum = maximum

    def __str__(self):
        return "can't specify an initial value '%s' greater than maximum value '%s'" % (self.initial, self.maximum)


class InitialIsNegative(IllegalSystemException):
    "Stock's initial value can't be less than zero."
    def __init__(self, initial):
        self.initial = initial

    def __str__(self):
        return "can't specify a negative initial value, specified '%s'" % (self.initial,)


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


class ConflictingValues(DeferLineInfo):
    "Stock intialized with multiple distinct values."

    def __init__(self, name, first, second):
        self.name = name
        self.first = first
        self.second = second

    def __str__(self):
        return "line %s initializes %s with conflict value %s (was %s): \"%s\"" % (
            self.line_number, self.name, self.second, self.first, self.line)


class UnknownFlowType(DeferLineInfo):
    "Specified flow type is unknown."

    def __init__(self, flow_type):
        super().__init__()
        self.flow_type = flow_type

    def __str__(self):
        return "line %s has invalid flow type \"%s\": \"%s\"" % (
            self.line_number, self.flow_type, self.line)
