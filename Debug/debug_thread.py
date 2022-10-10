from Pythonic_TriFSS.Communication.dataClass.thread import TriFSSThread, TriFSSThreadFactory
from Pythonic_TriFSS.Communication.semi_honest_party import SemiHonestParty
from Pythonic_TriFSS.Utils.thread_tool import get_loc_list

def test_func(x):
    print(x)
    return x


party = SemiHonestParty(party_id=0, partner_addr='127.0.0.1', partner_recv_port=43000, recv_port=44000)
for i in range(6):
    new = TriFSSThread(func=test_func, args=[i])
    party.add_thread(new)

party.start_all_thread()
list_ = get_loc_list(512, )
pass

