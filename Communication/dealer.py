from Pythonic_TriFSS.Communication import api
from Pythonic_TriFSS.Utils.dataClass.statistic_pack import statistic_pack
import Pythonic_TriFSS.Configs.communication as config
from Pythonic_TriFSS.Communication.dataClass.thread import TriFSSThreadFactory, TriFSSThread


class TrustedDealer(object):
    """
    Currently, the produced data are stored locally without Internet transfer.
    """
    def __init__(self, LOG=config.LOG):
        self.threadFactory = TriFSSThreadFactory()
        self.statistic_pack = statistic_pack()
        self.LOG = LOG

    def send(self, data, name=None):
        api.local_send(data, name, LOG=True)
        self.statistic_pack.add_io()

    def recv(self, name):
        api.local_recv(name, LOG=self.LOG)
        self.statistic_pack.add_io()

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

    def add_thread(self, new_thread: TriFSSThread):
        self.threadFactory.append(new_thread=new_thread)

    def empty_thread_pool(self):
        self.threadFactory.empty_thread_pool()

    def start_all_thread(self):
        self.threadFactory.execute()

    def get_performance_statics(self):
        self.statistic_pack.print()
