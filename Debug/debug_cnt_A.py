from Pythonic_TriFSS.Communication.dealer import TrustedDealer
from Pythonic_TriFSS.Communication.semi_honest_party import SemiHonestParty
from Pythonic_TriFSS.Common.group_elements import GroupElements
from Pythonic_TriFSS.General_MPC.Containment import Containment_Offline, Containment
from Pythonic_TriFSS.Common.tensor import TriFSSTensor

# dealer = TrustedDealer()
# knots_list = TriFSSTensor([GroupElements(0), GroupElements(0.5), GroupElements(1.0),
#                            GroupElements(1.5), GroupElements(2)])
# Containment_Offline(dealer, knots_list)
x = GroupElements(1.00)
party = SemiHonestParty(party_id=0, partner_addr='127.0.0.1', partner_recv_port=43000, recv_port=44000)
res = Containment(party=party, x=x, offline_pack_file='../Assets/Ctn_8_3_0.pack')
res_ = party.recv()
party.statistic_pack.print()
pass
