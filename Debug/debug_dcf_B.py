from Pythonic_TriFSS.FSS.dcf import keygenDCF, evalDCF, keygenCorrelatedDCF, evalCorrelatedDCF
from Pythonic_TriFSS.Common.group_elements import GroupElements
from Pythonic_TriFSS.Communication.dealer import TrustedDealer
from Pythonic_TriFSS.Communication.semi_honest_party import SemiHonestParty

x = GroupElements(-0.25)

# dealer = TrustedDealer()
# keygenCorrelatedDCF(x=interval, party=dealer)

party = SemiHonestParty(party_id=1, partner_addr='127.0.0.1', partner_recv_port=44000, recv_port=43000)
res = evalCorrelatedDCF(party=party, x=x, filename='rDCF_8_3_1.key', DEBUG=True)
party.send(res)
party.statistic_pack.print()
pass