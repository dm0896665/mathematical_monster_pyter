from com.github.dm0896665.main.core.math.operation_type import OperationType

class Operation:
    correct_questions = 0
    total_questions = 0
    is_enabled = True

    def __init__(self, max: int = 0, min: int = 0, operation_type: OperationType = OperationType.UNKNOWN):
        super().__init__()
        self.max = max
        self.min = min
        self.operation_type = operation_type
