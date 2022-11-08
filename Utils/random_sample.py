from Pythonic_TriFSS.Common.group_elements import GroupElements
from Pythonic_TriFSS.Configs.fixed_point_repr import bitlen, scalefactor, DEBUG
import time
import random


def sampleGroupElements(bitlen=bitlen, scale=scalefactor, seed=None,
                        upper_bound=None, lower_bound=None) -> GroupElements:
    """
    This function returns random group elements
    :param lower_bound: should be real value
    :param upper_bound: should be real value
    :param seed:
    :param bitlen:
    :param scale:
    :return:
    """
    if seed is None:
        random.seed(time.time())
    else:
        random.seed(seed)
    ring = 2 ** (bitlen - 1) - 1
    if (upper_bound is None) and (lower_bound is None):
        return GroupElements(random.uniform(-ring, ring), bitlen=bitlen, scale=scale, DEBUG=DEBUG)
    elif upper_bound is None:
        return GroupElements(random.uniform(lower_bound, ring), bitlen=bitlen, scale=scale, DEBUG=DEBUG)
    elif lower_bound is None:
        return GroupElements(random.uniform(-ring, upper_bound), bitlen=bitlen, scale=scale, DEBUG=DEBUG)
    else:
        return GroupElements(random.uniform(lower_bound, upper_bound), bitlen=bitlen, scale=scale, DEBUG=DEBUG)


def sampleBit(seed=None) -> int:
    if seed is None:
        random.seed(time.time())
    else:
        random.seed(seed)
    return random.getrandbits(1)
