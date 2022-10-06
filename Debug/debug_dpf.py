from Pythonic_TriFSS.FSS.dpf import keygenDPF, evalDPF
from Pythonic_TriFSS.Common.group_elements import GroupElements

k0, k1 = keygenDPF(GroupElements(10))

r0 = evalDPF(0, GroupElements(11), k0)
r1 = evalDPF(1, GroupElements(11), k1)

print(r0)
print(r1)

