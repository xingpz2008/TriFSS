from Pythonic_TriFSS.FSS.dcf import keygenDCF, evalDCF
from Pythonic_TriFSS.Common.group_elements import GroupElements

k0, k1 = keygenDCF(GroupElements(50))

r0 = evalDCF(0, GroupElements(51), k0)
r1 = evalDCF(1, GroupElements(51), k1)

print(r0)
print(r1)
