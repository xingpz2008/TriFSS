from typing import Union

from Pythonic_TriFSS.FSS.dataClass.function_key import Correlated_DIFKey, DIFKey
from Pythonic_TriFSS.Common.tensor import TriFSSTensor


class Mod_pack(object):
    """
    For mod operation, we need one triplet and one Correlated DCF Key compare to
    """

    def __init__(self):
        self.triplet = None
        self.rDCFkey = None


class Containment_pack(object):
    def __init__(self):
        self.key_list = []
        self.len = 0

    def add_key(self, key: Union[DIFKey, Correlated_DIFKey]):
        self.key_list.append(key)
        self.len += 1


class massive_B2A_triplet_pack(object):
    def __init__(self, number=0):
        self.a_tensor = TriFSSTensor([None] * number)
        self.ab_b_tensor = TriFSSTensor([None] * number)


class boolean_AND_pack(object):
    def __init__(self):
        self.triplet = None


class wrap_and_all1s_pack(object):
    def __init__(self):
        self.rcDPFkey = None
        self.rDCFkey = None


class digit_decompose_pack(object):
    def __init__(self):
        self.wrap_and_all1s_pack = None
        self.boolean_AND_pack_list = []
        self.B2A_triplet_list = []


class arithmetic_mult_pack(object):
    def __init__(self):
        self.triplet = None
