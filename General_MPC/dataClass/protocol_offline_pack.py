import Pythonic_TriFSS.Configs.fixed_point_repr as config
from Pythonic_TriFSS.Common.group_elements import GroupElements
from Pythonic_TriFSS.General_MPC.B2A import generate_cross_term_triplet


class Mod_pack(object):
    """
    For mod operation, we need one triplet and one Correlated DCF Key compare to
    """

    def __init__(self):
        self.triplet = None
        self.rDCFkey = None


class Containment_pack(object):
    def __init__(self):
        pass
    # TODO: Add containment pack
