from Pythonic_TriFSS.Communication.dealer import TrustedDealer
from Pythonic_TriFSS.Communication.semi_honest_party import SemiHonestParty
from Pythonic_TriFSS.Common.group_elements import GroupElements
from Pythonic_TriFSS.FSS.dif import keygenDIF, evalDIF, keygenCorrelatedDIF, evalCorrelatedDIF

x = GroupElements(-2)
interval_0 = GroupElements(-5)
interval_1 = GroupElements(11.86)

# dealer = TrustedDealer()
# keygenCorrelatedDIF(interval=(interval_0, interval_1), party=dealer)

party = SemiHonestParty(party_id=0, partner_addr='127.0.0.1', partner_recv_port=43000, recv_port=44000)
res = evalCorrelatedDIF(party=party, x=x, filename='rDIF_32_20_0.key', DEBUG=True)
res_ = party.recv()
party.statistic_pack.print()

pass
