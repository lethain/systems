
import exceptions

class ParseException(Exception):
    "Base class for parse exceptions."
    pass


class MissingDelimiter(ParseException):
    "Line is missing a delimiter."
    def __init__(self, delimiter, line):
        self.delimiter = delimiter
        self.line = line

    def __str__(self):        
        return "missing delimiter '%s'in line '%s'" % (self.delimiter, self.line)
