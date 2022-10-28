from Pythonic_TriFSS.Cleartext.cleartext_functions import clear_tan
from Pythonic_TriFSS.Common.group_elements import GroupElements
from Pythonic_TriFSS.Utils.statistics import calculate_ulp_error
import math

input_ = 30.772
x = GroupElements(input_)
y = clear_tan(x)
print(calculate_ulp_error(y, math.tan(math.pi*input_)))
