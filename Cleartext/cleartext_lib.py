from typing import Union
from Pythonic_TriFSS.Common.group_elements import GroupElements
import Pythonic_TriFSS.Common.tensor as Tensor


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


def clear_mod(x: GroupElements, N: Union[int, GroupElements], unsigned=False) -> GroupElements:
    """
    This function calculates x % N by confirming gt relation.
    :param unsigned:
    :param x:
    :param N:
    :return:
    """
    if unsigned:
        sign = False
        if type(N) is int:
            N = GroupElements(N, bitlen=x.bitlen, scale=x.scalefactor)
        for i in range(x.bitlen):
            if x[x.bitlen - 1 - i] > N[x.bitlen - 1 - i]:
                sign = True
                break
            elif x[x.bitlen - 1 - i] < N[x.bitlen - 1 - i]:
                sign = False
                break
    else:
        sign = not (x < N)
    result = x - (N * int(sign))
    return result


def clear_containment(x: GroupElements, knots_list) -> Tensor.TriFSSTensor:
    """
    This function checks which intervals the x in.
    :param x:
    :param knots_list:
    :return:
    """
    result_vector = Tensor.TriFSSTensor()
    for i in range(len(knots_list) - 1):
        if (not (x > knots_list[i + 1])) and (not (x < knots_list[i])):
            result_vector.add_elements(1)
        else:
            result_vector.add_elements(0)
    return result_vector


def clear_dpf_all(x: GroupElements, domain: float) -> Tensor.TriFSSTensor:
    """
    This function returns all value at place x
    :param domain:
    :param x:
    :return:
    """
    entries = 2 ** x.bitlen
    resolution = 1 / (2 ** x.scalefactor)
    vector = Tensor.TriFSSTensor()
    for i in range(entries):
        this_val = i * resolution
        group_this = GroupElements(value=this_val, DEBUG=True)
        if group_this.value == x.value:
            vector.add_elements(1)
        else:
            vector.add_elements(0)
    return vector


def clear_digit_decompose(x: GroupElements, segNum: int):
    """
    This function returns digit decomposition of x
    :param x:
    :param segNum:
    :return:
    """
    assert (x.bitlen % segNum == 0), 'Currently we only support segNum is a divisor of bit length'
    segLen = int(x.bitlen / segNum)
    segmentation = []
    for i in range(segNum):
        segmentation.append(GroupElements(value=None,
                                          repr_value=(x.value >> (i * segLen) & ((2 ** segLen) - 1)),
                                          bitlen=segLen,
                                          scale=x.scalefactor))
    return segmentation
