from Pythonic_TriFSS.Math.dataClass.LookUpTable import LookUpTable
from Pythonic_TriFSS.Common.group_elements import GroupElements
import Pythonic_TriFSS.Configs.fixed_point_repr as repr_config
import Pythonic_TriFSS.Configs.communication as communication_config
import pickle
import math


def sin_coefficients(save: False, filename=None, truncated_scale=2+repr_config.scalefactor) -> LookUpTable:
    """
    Look up table for sin coefficients.
    :param truncated_scale:
    :param save:
    :param filename:
    :return:
    """
    lut = LookUpTable()
    # Add elements of first interval
    coefficients_1 = dict()
    coefficients_2 = dict()
    coefficients_3 = dict()
    coefficients_4 = dict()
    coefficients_1['a'] = GroupElements(1)
    coefficients_1['b'] = GroupElements(1, bitlen=truncated_scale)
    coefficients_1['c'] = GroupElements(0, bitlen=truncated_scale)
    coefficients_2['a'] = GroupElements(1)
    coefficients_2['b'] = GroupElements(-1, bitlen=truncated_scale)
    coefficients_2['c'] = GroupElements(1, bitlen=truncated_scale)
    coefficients_3['a'] = GroupElements(1)
    coefficients_3['b'] = GroupElements(1, bitlen=truncated_scale)
    coefficients_3['c'] = GroupElements(-1, bitlen=truncated_scale)
    coefficients_4['a'] = GroupElements(-1)
    coefficients_4['b'] = GroupElements(-1, bitlen=truncated_scale)
    coefficients_4['c'] = GroupElements(2, bitlen=truncated_scale)
    lut.add_elements(coefficients_1)
    lut.add_elements(coefficients_2)
    lut.add_elements(coefficients_3)
    lut.add_elements(coefficients_4)
    if save:
        if filename is None:
            filename = communication_config.default_filepath + f'publicSinCoefficients_' \
                                                               f'{repr_config.bitlen}_{repr_config.scalefactor}.lut'
        with open(filename, 'wb+') as f:
            pickle.dump(lut, f)
        return filename
    return lut


def sin_val(save: False, filename=None,
            key_bitlen=repr_config.bitlen, key_scale=repr_config.scalefactor,
            value_bitlen=repr_config.bitlen, value_scale=repr_config.scalefactor) -> LookUpTable:
    """
    This function generates sin value in Group elements
    LUT Struct:
    val = GroupElements(f(x))
    key = x in real_value
    :param value_scale:
    :param key_scale:
    :param key_bitlen:
    :param value_bitlen:
    :param save:
    :param filename:
    :return:
    """
    lut_ = LookUpTable()
    entries = 2 ** key_bitlen
    solution = 1 / (2 ** key_scale)
    for i in range(entries):
        this_x = i * solution
        val = math.sin(this_x * math.pi)
        lut_.add_elements(GroupElements(value=val, bitlen=value_bitlen, scale=value_scale, DEBUG=True),
                          GroupElements(value=this_x, bitlen=value_bitlen, scale=value_scale, DEBUG=True))
    if save:
        if filename is None:
            filename = communication_config.default_filepath + f'publicSin_' \
                                                               f'{value_bitlen}_{value_scale}.lut'
        with open(filename, 'wb+') as f:
            pickle.dump(lut_, f)
        return filename
    return lut_


if __name__ == '__main__':
    _ = sin_coefficients(save=True)
    _ = sin_val(save=True)
