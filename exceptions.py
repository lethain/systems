"""
Custom exceptions for systems package.
"""
import exceptions


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
        return "stock '%s' can be used as source for rate '%s'" % (self.source, self.rate)


class ParseError(ParseException):
    "Most generic parse error."
    def __init__(self, line="", line_number=0):
        self.line = line
        self.line_number = line_number
        
    def __str__(self):
        return "line %s could not be parsed: \"%s\"" % (self.line_number, self.line)


class DeferLineInfo(ParseError):
    pass


class NoFlowType(DeferLineInfo):
    "No flow type known."
    pass


class ConflictingValues(DeferLineInfo):
    "Stock intialized with multiple distinct values."
    def __init__(self, name, first, second):
        self.name = name
        self.first = first
        self.second = second

    def __str__(self):
        return "line %s initializes %s with conflict value %s (was %s): \"%s\"" % (self.line_number,self.name, self.second, self.first, self.line)


class UnknownFlowType(DeferLineInfo):
    "Specified flow type is unknown."
    def __init__(self, flow_type):
        super().__init__()
        self.flow_type = flow_type

    def __str__(self):
        return "line %s has invalid flow type \"%s\": \"%s\"" % (self.line_number, self.flow_type, self.line)


class MissingDelimiter(ParseError):
    "Line is missing a delimiter."
    def __init__(self, line, line_number, delimiter):
        super().__init__(line, line_number)
        self.delimiter = delimiter        

    def __str__(self):        
        return "line %s is missing delimiter '%s': \"%s\"" % (self.line_number, self.delimiter, self.line)

