from Pythonic_TriFSS.General_MPC.B2A import generate_cross_term_triplet, B2A
from Pythonic_TriFSS.Communication.semi_honest_party import SemiHonestParty
from Pythonic_TriFSS.Communication.dealer import TrustedDealer

# dealer = TrustedDealer()
party = SemiHonestParty(party_id=1, partner_addr='127.0.0.1', partner_recv_port=44000, recv_port=43000)
x = 1
res = B2A(x, '1665059990.2984588', party, DEBUG=True)
party.send(res)
party.statistic_pack.print()
pass
