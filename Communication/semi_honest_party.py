from Pythonic_TriFSS.Communication import api
import Pythonic_TriFSS.Configs.communication as config
from Pythonic_TriFSS.Utils.statistics import get_data_size
from Pythonic_TriFSS.Utils.dataClass.statistic_pack import statistic_pack
from Pythonic_TriFSS.Communication.dataClass.thread import TriFSSThreadFactory, TriFSSThread


class SemiHonestParty(object):
    def __init__(self, party_id, partner_addr, partner_recv_port, addr=config.default_localhost,
                 recv_port=config.default_port_1, LOG=config.LOG):
        assert (party_id in [0, 1]), 'Invalid Party ID'
        self.party_id = party_id
        self.partner_addr = partner_addr
        self.partner_recv_port = partner_recv_port
        self.addr = addr
        self.recv_port = recv_port
        self.statistic_pack = statistic_pack()
        self.recv_socket = api.listen(self.addr, self.recv_port, LOG)
        self.threadFactory = TriFSSThreadFactory()
        self.LOG = LOG
        self.DPF_Dict = dict()

    def send(self, data):
        api.send(self.partner_addr, self.partner_recv_port, data, self.LOG)
        self.statistic_pack.add_send(get_data_size(data))

    def recv(self):
        data = api.recv(self.recv_socket, self.recv_port, self.LOG)
        self.statistic_pack.add_recv(get_data_size(data))
        return data

    def local_recv(self, filename):
        data = api.local_recv(filename)
        self.statistic_pack.add_io()
        return data

    def set_start_marker(self, func: str, func_type: str = 'online'):
        assert (func_type in ['online', 'offline']), 'Invalid function type'
        if func_type == 'online':
            self.statistic_pack.add_function_online_start_maker(func)
        else:
            self.statistic_pack.add_function_offline_start_maker(func)

    def eliminate_start_marker(self, func: str, func_type: str = 'online'):
        assert (func_type in ['online', 'offline']), 'Invalid function type'
        if func_type == 'online':
            self.statistic_pack.eliminate_online_maker(func)
        else:
            self.statistic_pack.eliminate_offline_maker(func)

    def empty_cache_dict(self):
        self.DPF_Dict = dict()

    def add_thread(self, new_thread: TriFSSThread):
        self.threadFactory.append(new_thread=new_thread)

    def start_all_thread(self):
        self.threadFactory.execute()

    def get_existing_thread_num(self):
        return self.threadFactory.get_existing_thread_num()

    def refresh_thread_pool_item(self, index, func, args):
        self.threadFactory.refresh_thread(index, func, args)

    def empty_thread_pool(self):
        self.threadFactory.empty_thread_pool()

    def get_performance_statics(self):
        self.statistic_pack.print()
