from Pythonic_TriFSS.Communication.dealer import TrustedDealer
from Pythonic_TriFSS.Communication.semi_honest_party import SemiHonestParty
from Pythonic_TriFSS.General_MPC.Mod import Mod, Mod_offline
from Pythonic_TriFSS.Common.group_elements import GroupElements

N = GroupElements(2)
x = GroupElements(2.75)
# dealer = TrustedDealer()
# Mod_offline(dealer, 2)

party = SemiHonestParty(party_id=0, partner_addr='127.0.0.1', partner_recv_port=43000, recv_port=44000)
res = Mod(party, x, N, 'Mod_8_3_0.pack', DEBUG=True)
res_ = party.recv()
recon = res+res_
party.statistic_pack.print()
pass
