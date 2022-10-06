import Pythonic_TriFSS.Configs.fss as config
from Pythonic_TriFSS.Common.group_elements import GroupElements
from Pythonic_TriFSS.Utils.prg import prg
from Pythonic_TriFSS.Utils.random_sample import sampleGroupElements
from Pythonic_TriFSS.FSS.dataClass.correction_words import CW_DPF
from Pythonic_TriFSS.FSS.dataClass.function_key import DPFKey
from Pythonic_TriFSS.Communication.semi_honest_party import SemiHonestParty
from Pythonic_TriFSS.Communication.dealer import TrustedDealer


def keygenDPF(x: GroupElements, party: TrustedDealer, sec_para=config.sec_para, filename=None, DEBUG=config.DEBUG) \
        -> tuple:
    """
    This function returns the key pair for DPF @ x, payload = 1 currently.
    We sample the first seed from the ring
    TODO: Add randomness DPF
    TODO: Add Full Domain Evaluation
    :param filename:
    :param party:
    :param DEBUG:
    :param sec_para:
    :param x:
    :return:
    """
    # First, generate a0, a1
    # alpha_0 belongs to left, alpha_1 belongs to right
    party.set_start_marker('keygenDPF', 'offline')
    alpha_0 = sampleGroupElements(x.bitlen, x.scalefactor, config.seed)
    alpha_1 = sampleGroupElements(x.bitlen, x.scalefactor, config.seed)
    k0 = DPFKey()
    k1 = DPFKey()
    k0.seed = alpha_0
    k1.seed = alpha_1
    action_bit_l = 0
    action_bit_r = 1
    level_seed_l = alpha_0.value
    level_seed_r = alpha_1.value
    for i in range(x.bitlen):
        prg_res_l = prg(level_seed_l, sec_para, 'DPF', party=party)
        prg_res_r = prg(level_seed_r, sec_para, 'DPF', party=party)
        prg_res = prg_res_r ^ prg_res_l
        # We compare from high position bits x[n] to x[0]
        if x[x.bitlen - 1 - i] == 1:
            s_l = prg_res >> (2 + sec_para) & (2 ** sec_para - 1)
            b_l = prg_res >> (1 + sec_para) & 1
            b_r = prg_res & 1 ^ 1
            CW = CW_DPF(s=s_l, b_l=b_l, b_r=b_r, sec_para=sec_para)
        else:
            s_r = prg_res >> 1 & (2 ** sec_para - 1)
            b_l = prg_res >> (1 + sec_para) & 1 ^ 1
            b_r = prg_res & 1
            CW = CW_DPF(s=s_r, b_l=b_l, b_r=b_r, sec_para=sec_para)
        k0.CW_List.append(CW)
        k1.CW_List.append(CW)
        decompressed_CW = CW.__get_decompressed_CW__()
        pre_prg_seed_l = prg_res_l
        pre_prg_seed_r = prg_res_r
        if action_bit_l:
            pre_prg_seed_l = decompressed_CW ^ prg_res_l
        if action_bit_r:
            pre_prg_seed_r = decompressed_CW ^ prg_res_r
        if x[x.bitlen - 1 - i] == 1:
            level_seed_l = pre_prg_seed_l >> 1 & (2 ** sec_para - 1)
            level_seed_r = pre_prg_seed_r >> 1 & (2 ** sec_para - 1)
            action_bit_l = pre_prg_seed_l & 1
            action_bit_r = pre_prg_seed_r & 1
        else:
            level_seed_l = pre_prg_seed_l >> (2 + sec_para) & (2 ** sec_para - 1)
            level_seed_r = pre_prg_seed_r >> (2 + sec_para) & (2 ** sec_para - 1)
            action_bit_l = pre_prg_seed_l >> (1 + sec_para) & 1
            action_bit_r = pre_prg_seed_r >> (1 + sec_para) & 1
        if DEBUG:
            reconstructed_seed = pre_prg_seed_r ^ pre_prg_seed_l
            print(f'[INFO] {i} Iteration for dealer:')
            print(f'Reconstructed Next Seed: SL = {reconstructed_seed >> (2 + sec_para) & (2 ** sec_para - 1)}, '
                  f'BL = {reconstructed_seed >> (1 + sec_para) & 1}, '
                  f'SR = {reconstructed_seed >> 1 & (2 ** sec_para - 1)}, '
                  f'BR = {reconstructed_seed & 1}')
            print(f'Current choice is {x[x.bitlen - 1 - i]}')
    party.send(k0, name=filename)
    party.send(k1, name=filename)
    party.eliminate_start_maker('keygenDPF', 'offline')
    return k0, k1


def evalDPF(party: SemiHonestParty, x: GroupElements, key: DPFKey = None, filename=None, sec_para=config.sec_para,
            DEBUG=config.DEBUG):
    """
    This function evaluates DPF at key with the public value x
    :param filename:
    :param DEBUG:
    :param sec_para:
    :param party:
    :param key:
    :param x:
    :return:
    """
    party.set_start_marker(func='evalDPF')
    if filename is None:
        assert (key is not None), "We need at least key or keyfile to continue."
    else:
        key = party.local_recv(filename=filename)
    level_seed = key.seed.value
    action_bit = party.party_id
    for i in range(x.bitlen):
        if DEBUG:
            print(f'[INFO] {i} Iteration for party {party.party_id}:')
            print(f'level seed = {level_seed}')
            print(f'Action bit = {action_bit}')
        # We first expand the seed by PRG
        prg_res = prg(level_seed, sec_para, 'DPF', party=party)
        # Then add it with CW
        if action_bit == 1:
            pre_level_seed = prg_res ^ key.CW_List[i].__get_decompressed_CW__()
        else:
            pre_level_seed = prg_res
        if x[x.bitlen - 1 - i] == 1:
            level_seed = pre_level_seed >> 1 & (2 ** sec_para - 1)
            action_bit = pre_level_seed & 1
        else:
            level_seed = pre_level_seed >> (2 + sec_para) & (2 ** sec_para - 1)
            action_bit = pre_level_seed >> (1 + sec_para) & 1
        if DEBUG:
            print(f'PRG Result = {prg_res}')
            print(f'pre level seed = {pre_level_seed}')
    party.eliminate_start_maker('evalDPF')
    return action_bit
