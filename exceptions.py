
import exceptions

class ParseException(Exception):
    "Base class for parse exceptions."
    pass


class ParseError(ParseException):
    "Most generic parse error."
    def __init__(self, line, line_number):
        self.line = line
        self.line_number = line_number
        
    def __str__(self):
        return "line %s could not be parsed: \"%s\"" % (self.line_number, self.line)


class NoFlowType(ParseError):
    "No flow type known."
    def __init__(self):
        # requires flow control to fill in these values later
        super().__init__("", 0)


class UnknownFlowType(ParseError):
    "Specified flow type is unknown."
    def __init__(self, flow_type, line="", line_number=0):
        super().__init__(line, line_number)
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

