from Pythonic_TriFSS.Communication.semi_honest_party import SemiHonestParty
from Pythonic_TriFSS.Common.group_elements import GroupElements
from Pythonic_TriFSS.General_MPC.Containment import Containment

x = GroupElements(-1.75)
party = SemiHonestParty(party_id=1, partner_addr='127.0.0.1', partner_recv_port=44000, recv_port=43000)
res = Containment(party=party, x=x, offline_pack_file='../Assets/Ctn_8_3_1.pack')
party.send(res)
party.statistic_pack.print()
pass
