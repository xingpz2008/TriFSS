from Pythonic_TriFSS.Common.group_elements import GroupElements
import Pythonic_TriFSS.Cleartext.cleartext_lib as lib


def clear_sin(x: GroupElements) -> GroupElements:
    """
    This function is the cleartext implementation of sine, for accuracy evaluation only.
    :param x:
    :return:
    """
    x = lib.clear_bits_removal(x, (x.bitlen-1-x.scalefactor))
    x = lib.clear_mod(x, 2)
    result = lib.clear_containment(x, [0, 0.5, 1, 1.5, 2])

