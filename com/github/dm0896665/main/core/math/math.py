from com.github.dm0896665.main.core.math.operation import Operation
from com.github.dm0896665.main.core.math.operations import *
from com.github.dm0896665.main.util.class_util import ClassUtil


class Math:

    def __init__(self):
        super().__init__()
        self.is_math_enabled = True
        self.operations = ClassUtil.get_subtypes_of(Operation, "core.math.operations")

    def enable_math(self):
        self.is_math_enabled = True

    def disable_math(self):
        self.is_math_enabled = False

    def get_ci_ratio(self) -> str:
        # initialize variables
        ci_formatted: str = None;
        ci: int = 0;
        correct: int = self.get_correct_answer_count()
        incorrect: int = self.get_incorrect_answer_count()

        # if the number incorrect or correct are zero make the KD the number of correct
        if incorrect == 0 or correct == 0:
            ci_formatted = f"{correct:.2f}"

        # otherwise, calculate the kill to death ratio
        else:
            ci = correct / incorrect

        # if the KD is not 0 format the KD
        if ci != 0:
            ci_formatted = f"{ci:.2f}"

        # return the formatted KD
        return ci_formatted

    def get_correct_answer_count(self) -> int:
        return sum([operation.correct_questions for operation in self.operations])

    def get_incorrect_answer_count(self) -> int:
        return self.get_total_questions_answered() - self.get_correct_answer_count()

    def get_total_questions_answered(self) -> int:
        return sum([operation.total_questions for operation in self.operations])
