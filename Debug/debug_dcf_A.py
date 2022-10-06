from Pythonic_TriFSS.FSS.dcf import keygenDCF, evalDCF
from Pythonic_TriFSS.Common.group_elements import GroupElements
from Pythonic_TriFSS.Communication.dealer import TrustedDealer
from Pythonic_TriFSS.Communication.semi_honest_party import SemiHonestParty

x = GroupElements(5.0049)
interval = GroupElements(5)

# dealer = TrustedDealer()
# keygenDCF(x=interval, party=dealer)
#TODO: [EMERGENCY] FIX DCF!

party = SemiHonestParty(party_id=0, partner_addr='127.0.0.1', partner_recv_port=43000, recv_port=44000)
res = evalDCF(party=party, x=x, filename='1665081720.88787170.5279922267856386', DEBUG=True)
res_ = party.recv()
party.statistic_pack.print()
pass
