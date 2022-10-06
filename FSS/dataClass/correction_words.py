from Pythonic_TriFSS.Configs.fss import sec_para


class CW_DPF(object):
    def __init__(self, s, b_l, b_r, sec_para=sec_para):
        self.s = s
        self.b_l = b_l
        self.b_r = b_r
        self.__sec_para = sec_para

    def __get_decompressed_CW__(self):
        return (self.s << (self.__sec_para + 2)) ^ (self.b_l << (self.__sec_para + 1)) ^ (self.s << 1) ^ self.b_r


class CW_DCF(object):
    def __init__(self, s, b_l, b_r, c_l, c_r , sec_para=sec_para):
        self.s = s
        self.b_l = b_l
        self.b_r = b_r
        self.c_l = c_l
        self.c_r = c_r
        self.__sec_para = sec_para

    def __get_decompressed_CW__(self):
        return (self.c_l << (self.__sec_para * 2 + 3)) ^ (self.s << (self.__sec_para + 3)) ^ \
               (self.b_l << (self.__sec_para + 2)) ^ (self.s << 2) ^ (self.b_r << 1) ^ self.c_r
