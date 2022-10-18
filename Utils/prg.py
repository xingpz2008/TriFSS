import random
from Pythonic_TriFSS.Configs.fss import sec_para
from Pythonic_TriFSS.Common.group_elements import GroupElements
import Pythonic_TriFSS.Configs.fixed_point_repr as repr_config


def prg(seed: int, sec_para=sec_para, func_type=None, party=None, extra_m=None):
    random.seed(seed)
    if party is not None:
        party.statistic_pack.add_prg()
    else:
        print('[WARNING] Unsetted party may lead to imprecise performance data!')
    if func_type == 'DPF':
        return random.getrandbits(2 * sec_para + 2)
    if func_type == 'DCF':
        return random.getrandbits(2 * sec_para + 4)
    if func_type == 'Convert_G':
        return random.getrandbits(sec_para + extra_m)
    else:
        raise NotImplementedError("Unsupported Query")


def Convert_G(seed: int, bitlen=repr_config.bitlen, scale=repr_config.scalefactor, sec_para=sec_para, party=None):
    """
    This function converts int seed to group elements, from lambda to G
    :param party:
    :param bitlen:
    :param scale:
    :param sec_para:
    :param seed:
    :return:
    """
    if not bitlen > sec_para:
        repr_value = seed >> (sec_para - bitlen)
        return GroupElements(value=None, repr_value=repr_value, bitlen=bitlen, scale=scale)
    else:
        repr_value = prg(seed=seed, sec_para=sec_para, func_type='Convert_G', party=party, extra_m=bitlen)
        repr_value = repr_value >> sec_para
        return GroupElements(value=None, repr_value=repr_value, bitlen=bitlen, scale=scale)
