from Pythonic_TriFSS.Common.group_elements import GroupElements
from Pythonic_TriFSS.Utils.statistics import get_data_size

x = GroupElements(13, scale=4, bitlen=10, DEBUG=True)
x0 = GroupElements(-5.5, scale=10, bitlen=64, DEBUG=True)
x1 = GroupElements(-1, scale=10, bitlen=64, DEBUG=True)
_x = GroupElements(13, scale=10, bitlen=64, DEBUG=True)

comp = x > 0

z2 = x0 * x1

size = get_data_size(x)
_size = get_data_size(_x)
pass