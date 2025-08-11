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
