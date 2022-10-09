from typing import Union
from Pythonic_TriFSS.Common.group_elements import GroupElements
from Pythonic_TriFSS.Common.tensor import TriFSSTensor


def clear_bits_removal(x: GroupElements, removal_number: int) -> GroupElements:
    """
    This function explicitly removes high position bits without any extra checking.
    Should be used with cautious!
    :param x:
    :param removal_number:
    :return:
    """
    assert (removal_number < x.bitlen), 'Cannot remove so many bits.'
    new_bit_len = x.bitlen - removal_number
    remaining_bits = x.bitlen - removal_number
    new_value = x.value % (2 ** remaining_bits)
    return GroupElements(value=None, repr_value=new_value, bitlen=new_bit_len, scale=x.scalefactor)


def clear_mod(x: GroupElements, N: Union[int, GroupElements]) -> GroupElements:
    """
    This function calculates x % N by confirming gt relation.
    :param x:
    :param N:
    :return:
    """
    sign = not (x < N)
    result = x - (sign * N)
    return result


def clear_containment(x: GroupElements, knots_list) -> TriFSSTensor:
    """
    This function checks which intervals the x in.
    :param x:
    :param knots_list:
    :return:
    """
    result_vector = TriFSSTensor()
    for i in range(len(knots_list) - 1):
        if (not (x > knots_list[i + 1])) and (not (x < knots_list[i])):
            result_vector.add_elements(1)
        else:
            result_vector.add_elements(0)
    return result_vector


def clear_dpf_all(x: GroupElements, domain: float) -> TriFSSTensor:
    """
    This function returns all value at place x
    :param domain:
    :param x:
    :return:
    """
    entries = 2 ** x.bitlen
    resolution = 1 / (2**x.scalefactor)
    vector = TriFSSTensor()
    for i in range(entries):
        this_val = i * resolution
        group_this = GroupElements(value=this_val, DEBUG=True)
        if group_this.value == x.value:
            vector.add_elements(1)
        else:
            vector.add_elements(0)
    return vector
