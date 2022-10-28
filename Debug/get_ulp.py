from Pythonic_TriFSS.Utils.statistics import calculate_ulp_error
from Pythonic_TriFSS.Common.group_elements import GroupElements

in_ = 0.227565
actual = 0.22756412351334981
y = calculate_ulp_error(GroupElements(in_), actual)
print(y)
