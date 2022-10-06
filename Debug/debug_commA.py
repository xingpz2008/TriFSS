from Pythonic_TriFSS.Communication.semi_honest_party import SemiHonestParty
from Pythonic_TriFSS.Common.group_elements import GroupElements

x = SemiHonestParty(0, port=30001)
data = GroupElements(30, DEBUG=True)
x.send('127.0.0.1', 30001, data)
pass
