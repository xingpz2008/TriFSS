from Pythonic_TriFSS.Cleartext.cleartext_functions import clear_sin
from Pythonic_TriFSS.Common.group_elements import GroupElements
from Pythonic_TriFSS.Utils.statistics import calculate_ulp_error
import math

input_ = 30.784
x = GroupElements(input_)
y = clear_sin(x)
print(calculate_ulp_error(y, math.sin(math.pi*input_)))
