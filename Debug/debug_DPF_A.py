from Pythonic_TriFSS.FSS.dpf import keygenCorrelatedDPF, evalCorrelatedDPF, keygenDPF, evalAllDPF
from Pythonic_TriFSS.Common.group_elements import GroupElements
from Pythonic_TriFSS.Communication.dealer import TrustedDealer
from Pythonic_TriFSS.Communication.semi_honest_party import SemiHonestParty

# For debug @ this, x should be shares instead of the value itself!!!!!

k = GroupElements(10.5)

# dealer = TrustedDealer()
# keygenDPF(x=k, party=dealer)

x = GroupElements(1.5)

party = SemiHonestParty(party_id=0, partner_addr='127.0.0.1', partner_recv_port=43000, recv_port=44000)
res = evalAllDPF(party=party, x=x, filename='DPF_8_3_0.key', DEBUG=True)
res_ = party.recv()
party.statistic_pack.print()

pass
