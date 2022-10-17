from Pythonic_TriFSS.FSS.dpf import keygenCorrelatedDPF, evalCorrelatedDPF, keygenDPF, evalAllDPF, evalDPF
from Pythonic_TriFSS.Common.group_elements import GroupElements
from Pythonic_TriFSS.Communication.dealer import TrustedDealer
from Pythonic_TriFSS.Communication.semi_honest_party import SemiHonestParty

# For debug correlated Eval, x should be shares instead of the value itself!!!!!
# For debug Eval, x should be the identical!

k = GroupElements(10.5)

# dealer = TrustedDealer()
# keygenDPF(x=k, party=dealer, payload=GroupElements(1))

x = GroupElements(11.5)

party = SemiHonestParty(party_id=0, partner_addr='127.0.0.1', partner_recv_port=43000, recv_port=44000)
res = evalDPF(party=party, x=x, filename='DPF_16_9_0.key', DEBUG=True, return_Arithmetic=True)
res_ = party.recv()
final = res + res_
party.statistic_pack.print()

pass
