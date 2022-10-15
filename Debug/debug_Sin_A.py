from Pythonic_TriFSS.Communication.dealer import TrustedDealer
import Pythonic_TriFSS.Configs.fixed_point_repr as repr_config
from Pythonic_TriFSS.Math.sine import sin, sin_offline
from Pythonic_TriFSS.Communication.semi_honest_party import SemiHonestParty
from Pythonic_TriFSS.Common.group_elements import GroupElements

#
# dealer = TrustedDealer()
# sin_offline(party=dealer)

party = SemiHonestParty(party_id=0, partner_addr='127.0.0.1', partner_recv_port=43000, recv_port=44000)
x = GroupElements(10)
res = sin(x=x, party=party)
res_ = party.recv()
final = res + res_
party.get_performance_statics()
