from Pythonic_TriFSS.Communication.semi_honest_party import SemiHonestParty
from Pythonic_TriFSS.Common.group_elements import GroupElements

x = SemiHonestParty(1, port=30002)
data = x.recv('127.0.0.1', 30001)
pass
