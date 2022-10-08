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
