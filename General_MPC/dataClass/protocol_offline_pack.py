from typing import Union

import Pythonic_TriFSS.Configs.fixed_point_repr as config
from Pythonic_TriFSS.Common.group_elements import GroupElements
from Pythonic_TriFSS.General_MPC.B2A import generate_cross_term_triplet
from Pythonic_TriFSS.FSS.dataClass.function_key import Correlated_DIFKey, DIFKey

# TODO: Add massive B2A Pack

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
