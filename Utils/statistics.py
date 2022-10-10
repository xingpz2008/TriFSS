import sys
from Pythonic_TriFSS.Common.group_elements import GroupElements


# TODO: Consider Add theory statistical

def get_data_size(x):
    """
    This function returns by byte
    :param x:
    :return:
    """
    return sys.getsizeof(x)


def calculate_ulp_error(result: GroupElements, real_result):
    """
    This function calculates ulp error.
    :param result:
    :param real_result:
    :return:
    """
    x = GroupElements(value=real_result, bitlen=result.bitlen, scale=result.scalefactor)
    return abs(x.value-result.value)
