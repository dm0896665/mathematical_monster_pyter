from enum import Enum
class OperationType(Enum):
    ADDITION = lambda a, b : a + b, "+"
    SUBTRACTION = lambda a, b : a - b, "-"
    MULTIPLICATION = lambda a, b : a * b, "x"
    DIVISION = lambda a, b : a / b, "/"
    UNKNOWN = lambda a, b : a + b, "?"

    def __new__(cls, *args, **kwds):
        obj = object.__new__(cls)
        obj._value_ = args[0]
        return obj

    # ignore the first param since it's already set by __new__
    def __init__(self, operation_function: str, sign: str = None):
        self.operation_function = operation_function
        self.sign = sign

    def __str__(self):
        return self.name

    @property
    def get_operation_function(self):
        return self.operation_function

    @property
    def get_sign(self):
        return self.sign

    def perform_operation(self, number_one, number_two):
        return self.get_operation_function(number_one, number_two)
