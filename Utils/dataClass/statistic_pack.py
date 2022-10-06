import time


class statistic_pack(object):
    # TODO: Repair total online time and offline time
    def __init__(self):
        self.__offline_time = 0
        self.__online_time = 0
        self.__online_func_time_table = dict()
        self.__offline_func_time_table = dict()
        self.__send_bytes = 0
        self.__recv_bytes = 0
        self.__prg_invocations = 0
        self.__io = 0
        self.__online_time_maker_list = dict()
        self.__offline_time_maker_list = dict()

    def add_online(self, delta, func=None):
        self.__online_time += delta
        if func is not None:
            if func not in self.__online_func_time_table.keys():
                self.__online_func_time_table[func] = delta
            else:
                self.__online_func_time_table[func] += delta

    def add_offline(self, delta, func=None):
        self.__offline_time += delta
        if func is not None:
            if func not in self.__offline_func_time_table.keys():
                self.__offline_func_time_table[func] = delta
            else:
                self.__offline_func_time_table[func] += delta

    def add_send(self, delta):
        self.__send_bytes += delta

    def add_recv(self, delta):
        self.__recv_bytes += delta

    def add_prg(self):
        self.__prg_invocations += 1

    def add_io(self):
        self.__io += 1

    def add_function_online_start_maker(self, func):
        assert (func not in self.__online_time_maker_list.keys()), f'Only one maker for func {func} is allowed.'
        self.__online_time_maker_list[func] = time.time()

    def add_function_offline_start_maker(self, func):
        assert (func not in self.__offline_time_maker_list.keys()), f'Only one maker for func {func} is allowed.'
        self.__offline_time_maker_list[func] = time.time()

    def eliminate_online_maker(self, func):
        assert (func in self.__online_time_maker_list.keys()), f'Maker for {func} does not exist.'
        delta = time.time() - self.__online_time_maker_list[func]
        self.add_online(delta=delta, func=func)
        self.__online_time_maker_list.pop(func)

    def eliminate_offline_maker(self, func):
        assert (func in self.__offline_time_maker_list.keys()), f'Maker for {func} does not exist.'
        delta = time.time() - self.__offline_time_maker_list[func]
        self.add_offline(delta=delta, func=func)
        self.__offline_time_maker_list.pop(func)

    def print(self):
        print('\n==========Statistic START==========')
        print('[WARNING] Total time consumption is not reliable, we recommend to set time maker manually'
              'by calling <party>.set_start_maker() & <party>.eliminate_start_maker() at target function!')
        print(f'Total Offline Time (Unreliable) = {self.__offline_time} s')
        print(f'Total Online Time (Unreliable) = {self.__online_time} s')
        print(f'Bytes Sent = {self.__send_bytes}')
        print(f'Bytes Received = {self.__recv_bytes}')
        print(f'PRG Invocations = {self.__prg_invocations}')
        print(f'I/O = {self.__io}')
        if len(self.__online_func_time_table) != 0:
            print('Online Function Overhead List (s):')
            print(self.__online_func_time_table)
        if len(self.__offline_func_time_table) != 0:
            print('Online Function Overhead List (s):')
            print(self.__offline_func_time_table)
        print('==========Statistic END==========\n')
