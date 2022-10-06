from threading import Thread


class TriFSSThread(Thread):
    def __init__(self, func, args=()):
        Thread.__init__(self)
        self.__return_value = None
        self.func = func
        self.args = args
        self.func_name = func.__name__

    def run(self):
        self.__return_value = self.func(*self.args)

    def get_thread_result(self):
        return self.__return_value


class TriFSSThreadFactory(object):
    def __init__(self):
        self.thread_list = []

    def append(self, new_thread: TriFSSThread):
        self.thread_list.append(new_thread)

    def execute(self):
        for thread in self.thread_list:
            thread.start()
        for thread in self.thread_list:
            thread.join()

    def get_thread_result_by_name(self, func_name):
        for t in self.thread_list:
            if t.func_name == func_name:
                return t.get_thread_result()
