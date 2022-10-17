from Pythonic_TriFSS.FSS.dpf import keygenCorrelatedDPF, evalCorrelatedDPF, keygenDPF, evalAllDPF, evalDPF
from Pythonic_TriFSS.Common.group_elements import GroupElements
from Pythonic_TriFSS.Communication.dealer import TrustedDealer
from Pythonic_TriFSS.Communication.semi_honest_party import SemiHonestParty


x = GroupElements(11.5)

party = SemiHonestParty(party_id=1, partner_addr='127.0.0.1', partner_recv_port=44000, recv_port=43000)
res = evalDPF(party=party, x=x, filename='DPF_16_9_1.key', DEBUG=True, return_Arithmetic=True)
party.send(res)
party.statistic_pack.print()
