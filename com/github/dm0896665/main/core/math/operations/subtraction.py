from com.github.dm0896665.main.core.math.operation import Operation
from com.github.dm0896665.main.core.math.operation_type import OperationType


class Subtraction(Operation):
    def __init__(self):
        super().__init__(100, 0, OperationType.SUBTRACTION)