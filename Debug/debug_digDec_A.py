from Pythonic_TriFSS.Communication.dealer import TrustedDealer
import Pythonic_TriFSS.Configs.fixed_point_repr as repr_config
from Pythonic_TriFSS.Communication.semi_honest_party import SemiHonestParty
from Pythonic_TriFSS.Common.group_elements import GroupElements
from Pythonic_TriFSS.General_MPC.Decompose import digit_decomposition, digit_decomposition_offline
from Pythonic_TriFSS.Common.tensor import TriFSSTensor

# dealer = TrustedDealer()
# digit_decomposition_offline(party=dealer, segLen=4)

party = SemiHonestParty(party_id=0, partner_addr='127.0.0.1', partner_recv_port=43000, recv_port=44000)
x = GroupElements(-23)

res = digit_decomposition(x=x, segLen=4, party=party, offline_data='digDec_4_16_9_0.pack')
res_ = party.recv()

constructed = GroupElements(-23) + GroupElements(-12)
new_res = TriFSSTensor()
for i in range(4):
    new_res.add_elements(res_[i] + res[i])
pass

