from com.github.dm0896665.main.core.math.operation import Operation
from com.github.dm0896665.main.core.math.operations import *
from com.github.dm0896665.main.util.class_util import ClassUtil


class Math:
    is_math_enabled = True
    operations = ClassUtil.get_subtypes_of(Operation, "core.math.operations")

    def __init__(self):
        super().__init__()

    def is_math_enabled(self):
        return self.is_math_enabled

    def enable_math(self):
        self.set_math_enabled(True)

    def disable_math(self):
        self.set_math_enabled(False)

    def set_math_enabled(self, is_enabled):
        self.is_math_enabled = is_enabled
