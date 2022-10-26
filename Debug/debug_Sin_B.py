from Pythonic_TriFSS.Communication.semi_honest_party import SemiHonestParty
from Pythonic_TriFSS.Common.group_elements import GroupElements
from Pythonic_TriFSS.Math.sine import sin, sin_offline

party = SemiHonestParty(party_id=1, partner_addr='127.0.0.1', partner_recv_port=44000, recv_port=43000)
x = GroupElements(0.5)
for i in range(1):
    res = sin(x=x, party=party)

party.get_performance_statics()
