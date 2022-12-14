from Pythonic_TriFSS.Communication.dealer import TrustedDealer
from Pythonic_TriFSS.Communication.semi_honest_party import SemiHonestParty
from Pythonic_TriFSS.Common.group_elements import GroupElements
from Pythonic_TriFSS.FSS.dif import keygenDIF, evalDIF, evalCorrelatedDIF

x = GroupElements(13.88)
party = SemiHonestParty(party_id=1, partner_addr='127.0.0.1', partner_recv_port=44000, recv_port=43000)
res = evalCorrelatedDIF(party=party, x=x, filename='rDIF_32_20_1.key', DEBUG=True)

party.send(res)
party.statistic_pack.print()
pass
