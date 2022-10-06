import random
from Pythonic_TriFSS.Configs.fss import sec_para


def prg(seed: int, sec_para=sec_para, func_type=None, party=None):
    random.seed(seed)
    if party is not None:
        party.statistic_pack.add_prg()
    else:
        print('[WARNING] Unsetted party may lead to imprecise performance data!')
    if func_type == 'DPF':
        return random.getrandbits(2 * sec_para + 2)
    if func_type == 'DCF':
        return random.getrandbits(2 * sec_para + 2)
    else:
        raise NotImplementedError("Unsupported Query")
