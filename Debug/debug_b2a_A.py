from Pythonic_TriFSS.General_MPC.B2A import generate_cross_term_triplet, B2A
from Pythonic_TriFSS.Communication.semi_honest_party import SemiHonestParty
from Pythonic_TriFSS.Communication.dealer import TrustedDealer
from Pythonic_TriFSS.Common.group_elements import GroupElements

# dealer = TrustedDealer()
# generate_cross_term_triplet(executor=dealer)

party = SemiHonestParty(party_id=0, partner_addr='127.0.0.1', partner_recv_port=43000, recv_port=44000)
x = 0
res = B2A(x, '1665059990.298673', party, DEBUG=True)
res_ = party.recv()
party.statistic_pack.print()
recon = res + res_
print(f'Reconstructed Value = {recon.value}')
pass
