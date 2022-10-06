import Pythonic_TriFSS.Configs.fss as config
from Pythonic_TriFSS.Common.group_elements import GroupElements
from Pythonic_TriFSS.Utils.prg import prg
from Pythonic_TriFSS.FSS.dataClass.correction_words import CW_DCF
from Pythonic_TriFSS.FSS.dataClass.function_key import DCFKey
from Pythonic_TriFSS.Utils.random_sample import sampleGroupElements
from Pythonic_TriFSS.Communication.dealer import TrustedDealer
from Pythonic_TriFSS.Communication.semi_honest_party import SemiHonestParty


def keygenDCF(x: GroupElements, party: TrustedDealer, inverse=False, filename=None, sec_para=config.sec_para,
              DEBUG=config.DEBUG) -> tuple:
    """
    TODO: Correlated Randomness?
    TODO: DIF
    TODO: Payload
    This functions returns DCF Key for if input < x, payload = 1 currently
    :param filename:
    :param party:
    :param x:
    :param inverse:
    :param sec_para:
    :param DEBUG:
    :return:
    """
    # alpha_0 belongs to left, alpha_1 belongs to right
    party.set_start_marker('keygenDCF', 'offline')
    alpha_0 = sampleGroupElements(x.bitlen, x.scalefactor, config.seed)
    alpha_1 = sampleGroupElements(x.bitlen, x.scalefactor, config.seed)
    k0 = DCFKey()
    k1 = DCFKey()
    k0.seed = alpha_0
    k1.seed = alpha_1
    action_bit_l = 0
    action_bit_r = 1
    level_seed_l = alpha_0.value
    level_seed_r = alpha_1.value
    for i in range(x.bitlen):
        prg_res_l = prg(level_seed_l, sec_para, 'DCF', party=party)
        prg_res_r = prg(level_seed_r, sec_para, 'DCF', party=party)
        prg_res = prg_res_r ^ prg_res_l
        # We compare from high position bits x[n] to x[0]
        # The "less than" can be only achieved when the path is to the right while the data is to be left
        if x[x.bitlen - 1 - i] == 1:
            # We first process DPF Key parts
            s_l = prg_res >> (3 + sec_para) & (2 ** sec_para - 1)
            b_l = prg_res >> (2 + sec_para) & 1
            b_r = (prg_res >> 1 & 1) ^ 1
            c_r = prg_res & 1
            c_l = (prg_res >> (3 + 2 * sec_para) & 1) ^ 1
            CW = CW_DCF(s=s_l, b_l=b_l, b_r=b_r, c_r=c_r, c_l=c_l)
        else:
            s_r = prg_res >> 2 & (2 ** sec_para - 1)
            b_l = (prg_res >> (2 + sec_para) & 1) ^ 1
            b_r = prg_res >> 1 & 1
            c_r = prg_res & 1
            c_l = prg_res >> (3 + 2 * sec_para) & 1
            CW = CW_DCF(s=s_r, b_l=b_l, b_r=b_r, c_r=c_r, c_l=c_l)
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
            level_seed_l = pre_prg_seed_l >> 2 & (2 ** sec_para - 1)
            level_seed_r = pre_prg_seed_r >> 2 & (2 ** sec_para - 1)
            action_bit_l = pre_prg_seed_l >> 1 & 1
            action_bit_r = pre_prg_seed_r >> 1 & 1
        else:
            level_seed_l = pre_prg_seed_l >> (3 + sec_para) & (2 ** sec_para - 1)
            level_seed_r = pre_prg_seed_r >> (3 + sec_para) & (2 ** sec_para - 1)
            action_bit_l = pre_prg_seed_l >> (2 + sec_para) & 1
            action_bit_r = pre_prg_seed_r >> (2 + sec_para) & 1
        if DEBUG:
            reconstructed_seed = pre_prg_seed_r ^ pre_prg_seed_l
            print(f'[INFO] {i} Iteration for dealer:')
            print(f'Reconstructed Next Seed: SL = {reconstructed_seed >> (3 + sec_para) & (2 ** sec_para - 1)}, '
                  f'BL = {reconstructed_seed >> (2 + sec_para) & 1}, '
                  f'CL = {reconstructed_seed >> (3 + 2 * sec_para) & 1}, '
                  f'SR = {reconstructed_seed >> 2 & (2 ** sec_para - 1)}, '
                  f'BR = {reconstructed_seed >> 1 & 1}, '
                  f'CR = {reconstructed_seed & 1}, ')
            print(f'Current choice is {x[x.bitlen - 1 - i]}')
    party.send(k0, name=filename)
    party.send(k1, name=filename)
    party.eliminate_start_maker('keygenDPF', 'offline')
    return k0, k1


def evalDCF(party: SemiHonestParty, x: GroupElements, key: DCFKey, inverse=False, filename=None,
            sec_para=config.sec_para, DEBUG=config.DEBUG):
    """
    This function evaluates DCF at key with public value x
    :param filename:
    :param inverse:
    :param party:
    :param x:
    :param key:
    :param sec_para:
    :param DEBUG:
    :return:
    """
    party.set_start_marker(func='evalDCF')
    if filename is None:
        assert (key is not None), "We need at least key or keyfile to continue."
    else:
        key = party.local_recv(filename=filename)
    level_seed = key.seed.value
    action_bit = party.party_id
    identifier_result = 0
    for i in range(x.bitlen):
        if DEBUG:
            print(f'[INFO] {i} Iteration for party {party}:')
            print(f'level seed = {level_seed}')
            print(f'Action bit = {action_bit}')
        # We first expand the seed by PRG
        prg_res = prg(level_seed, sec_para, 'DCF', party=party)
        if action_bit == 1:
            pre_level_seed = prg_res ^ key.CW_List[i].__get_decompressed_CW__()
        else:
            pre_level_seed = prg_res
        if x[x.bitlen - 1 - i] == 1:
            level_seed = pre_level_seed >> 2 & (2 ** sec_para - 1)
            action_bit = pre_level_seed >> 1 & 1
            identifier = pre_level_seed & 1
        else:
            level_seed = pre_level_seed >> (3 + sec_para) & (2 ** sec_para - 1)
            action_bit = pre_level_seed >> (2 + sec_para) & 1
            identifier = pre_level_seed >> (3 + 2 * sec_para) & 1
        if DEBUG:
            print(f'PRG Result = {prg_res}')
            print(f'pre level seed = {pre_level_seed}')
            print(f'Identifier = {identifier}')
        identifier_result = identifier_result ^ identifier
    party.eliminate_start_maker('evalDCF')
    return action_bit ^ identifier_result
