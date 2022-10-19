from Pythonic_TriFSS.Common.group_elements import GroupElements
from Pythonic_TriFSS.Configs.fixed_point_repr import bitlen, scalefactor, DEBUG
import time
import random


def sampleGroupElements(bitlen=bitlen, scale=scalefactor, seed=None) -> GroupElements:
    """
    This function returns random group elements
    :param seed:
    :param bitlen:
    :param scale:
    :return:
    """
    if seed is None:
        random.seed(time.time())
    else:
        random.seed(seed)
    ring = 2 ** bitlen - 1
    return GroupElements(random.uniform(-ring, ring), bitlen=bitlen, scale=scale, DEBUG=DEBUG)


def sampleBit(seed=None) -> int:
    if seed is None:
        random.seed(time.time())
    else:
        random.seed(seed)
    return random.getrandbits(1)
