class DPFKey(object):
    def __init__(self):
        self.seed = []
        self.CW_List = []
        self.CW_payload = []


class DCFKey(object):
    def __init__(self):
        self.seed = []
        self.CW_List = []
        self.CW_payload = []
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
        self.CW_payload = Key.CW_payload


class Correlated_DCFKey(DCFKey):
    def __init__(self):
        super().__init__()
        self.r = None

    def init_from_DCFKey(self, Key: DCFKey):
        self.seed = Key.seed
        self.CW_List = Key.CW_List
        self.inverse = Key.inverse


class Correlated_DIFKey(DIFKey):
    """
    Correlated DIF Key is almost the same as DIFKey
    However, its self.interval_0/1_key is Correlated DCF
    """
    def __init__(self):
        super().__init__()

