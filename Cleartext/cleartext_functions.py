from Pythonic_TriFSS.Common.group_elements import GroupElements
import Pythonic_TriFSS.Cleartext.cleartext_lib as lib
from Pythonic_TriFSS.Common.tensor import LookUpTable
import Pythonic_TriFSS.Communication.api as api
import Pythonic_TriFSS.Configs.fixed_point_repr as repr_config


# TODO: Add tangent
# TODO: Add bit-decomposition with smaller LUT

def clear_sin(x: GroupElements) -> GroupElements:
    """
    This function is the cleartext implementation of sine, for accuracy evaluation only.
    :param x:
    :return:
    """
    x = lib.clear_bits_removal(x, (x.bitlen - 2 - x.scalefactor))
    x = lib.clear_mod(x, 2, unsigned=True)
    containment_result = lib.clear_containment(x, [0, 0.5, 1, 1.5, 2])
    coefficients: LookUpTable = api.local_recv(f'publicSinCoefficients_{repr_config.bitlen}_'
                                               f'{repr_config.scalefactor}.lut')
    sin_var: LookUpTable = api.local_recv(f'publicSin_{repr_config.bitlen}_{repr_config.scalefactor}.lut')
    res = GroupElements(0)
    # bit-length of coefficients should equal to the truncated x
    a = 0
    b = 0
    c = 0
    for i in range(4):
        a = coefficients[i]['a'] * containment_result[i] + a
        b = coefficients[i]['b'] * containment_result[i] + b
        c = coefficients[i]['c'] * containment_result[i] + c
    new_x = x * b + c
    new_x = lib.clear_bits_removal(new_x, 2)
    del containment_result
    result = lib.clear_dpf_all(new_x, 0.5)
    for i in range(result.__get_len__()):
        res = res + (sin_var[i] * result[i])
    res = res * a
    return res
