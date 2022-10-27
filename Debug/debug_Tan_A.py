from Pythonic_TriFSS.Communication.dealer import TrustedDealer
import Pythonic_TriFSS.Configs.fixed_point_repr as repr_config
from Pythonic_TriFSS.Math.tangent import tan, tan_offline
from Pythonic_TriFSS.Communication.semi_honest_party import SemiHonestParty
from Pythonic_TriFSS.Common.group_elements import GroupElements


# dealer = TrustedDealer()
# tan_offline(party=dealer)

party = SemiHonestParty(party_id=0, partner_addr='127.0.0.1', partner_recv_port=43000, recv_port=44000)
x = GroupElements(10)
for i in range(1):
    res = tan(x=x, party=party)


party.get_performance_statics()
