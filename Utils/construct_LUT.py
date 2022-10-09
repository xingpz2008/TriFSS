from Pythonic_TriFSS.Math.dataClass.LookUpTable import LookUpTable
from Pythonic_TriFSS.Common.group_elements import GroupElements
import Pythonic_TriFSS.Configs.fixed_point_repr as repr_config
import Pythonic_TriFSS.Configs.communication as communication_config
import pickle
import math


def sin_coefficients(save: False, filename=None, truncated_scale=1+repr_config.scalefactor) -> LookUpTable:
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
    return lut


def sin_val(save: False, filename=None) -> LookUpTable:
    """
    This function generates sin value in Group elements
    LUT Struct:
    val = GroupElements(f(x))
    key = x in real_value
    :param save:
    :param filename:
    :return:
    """
    lut_ = LookUpTable()
    entries = 2 ** repr_config.bitlen
    solution = 1 / (2 ** repr_config.scalefactor)
    for i in range(entries):
        this_x = i * solution
        val = math.sin(this_x * math.pi)
        lut_.add_elements(GroupElements(value=val, DEBUG=True), GroupElements(value=this_x, DEBUG=True))
    if save:
        if filename is None:
            filename = communication_config.default_filepath + f'publicSin_' \
                                                               f'{repr_config.bitlen}_{repr_config.scalefactor}.lut'
        with open(filename, 'wb+') as f:
            pickle.dump(lut_, f)
    return lut_


if __name__ == '__main__':
    _ = sin_coefficients(save=True)
    _ = sin_val(save=True)
