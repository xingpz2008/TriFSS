from Pythonic_TriFSS.Configs.fss import sec_para


class CW_DPF(object):
    def __init__(self, s, b_l, b_r, sec_para=sec_para):
        self.s = s
        self.b_l = b_l
        self.b_r = b_r
        self.__sec_para = sec_para
        self.__decompressed_CW = None

    def __get_decompressed_CW__(self):
        if self.__decompressed_CW is None:
            self.__decompressed_CW = (self.s << (self.__sec_para + 2)) ^ (self.b_l << (self.__sec_para + 1)) ^ \
                                   (self.s << 1) ^ self.b_r
        return self.__decompressed_CW


class CW_DCF(object):
    def __init__(self, s, b_l, b_r, c_l, c_r , sec_para=sec_para):
        self.s = s
        self.b_l = b_l
        self.b_r = b_r
        self.c_l = c_l
        self.c_r = c_r
        self.__sec_para = sec_para
        self.__decompressed_CW = None

    def __get_decompressed_CW__(self):
        if self.__decompressed_CW is None:
            self.__decompressed_CW = (self.c_l << (self.__sec_para * 2 + 3)) ^ (self.s << (self.__sec_para + 3)) ^ \
               (self.b_l << (self.__sec_para + 2)) ^ (self.s << 2) ^ (self.b_r << 1) ^ self.c_r
        return self.__decompressed_CW
