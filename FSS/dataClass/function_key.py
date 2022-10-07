class DPFKey(object):
    def __init__(self):
        self.seed = []
        self.CW_List = []


class DCFKey(object):
    def __init__(self):
        self.seed = []
        self.CW_List = []
        self.inverse = False


class DIFKey(object):
    def __int__(self):
        self.interval_0_key = None
        self.interval_1_key = None


class Correlated_DPFKey(DPFKey):
    def __init__(self):
        super().__init__()
        self.r = None

    def init_from_DPFKey(self, Key: DPFKey):
        self.seed = Key.seed
        self.CW_List = Key.CW_List
