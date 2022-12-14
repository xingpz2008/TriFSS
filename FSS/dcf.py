import Pythonic_TriFSS.Configs.fss as config
from Pythonic_TriFSS.Common.group_elements import GroupElements
from Pythonic_TriFSS.Utils.prg import prg
from Pythonic_TriFSS.FSS.dataClass.correction_words import CW_DCF
from Pythonic_TriFSS.FSS.dataClass.function_key import DCFKey, Correlated_DCFKey
from Pythonic_TriFSS.Utils.random_sample import sampleGroupElements
from Pythonic_TriFSS.Communication.dealer import TrustedDealer
from Pythonic_TriFSS.Communication.semi_honest_party import SemiHonestParty


def keygenDCF(x: GroupElements, party: TrustedDealer, inverse=None, filename=None, sec_para=config.sec_para,
              local_transfer=True, DEBUG=config.DEBUG) -> [DCFKey, DCFKey]:
    """
    TODO: Consider Payload
    This functions returns DCF Key for if input < x, payload = 1 currently
    Attention, this is unsigned comparison, that compares without considering sign bit!
    :param local_transfer:
    :param filename:
    :param party:
    :param x:
    :param inverse: Keep False for unsigned comparison, keep None for signed comparison.
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
    if inverse is None:
        # This means we use the default settings and we use automatic judgement to determine if we need the inverse
        inverse = x < 0
    else:
        print('[WARNING] We STRONGLY recommend you to set var \'inverse\' as None to enable automatic inverse '
              'judgement, unless you know what it means!')
    k0.seed = alpha_0
    k0.inverse = inverse
    k1.seed = alpha_1
    k1.inverse = inverse
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
    if local_transfer:
        if filename is None:
            filename_0 = f'DCF_{x.bitlen}_{x.scalefactor}_0.key'
            filename_1 = f'DCF_{x.bitlen}_{x.scalefactor}_1.key'
            filename = [filename_0, filename_1]
        party.send(k0, name=filename[0])
        party.send(k1, name=filename[1])
    party.eliminate_start_marker('keygenDCF', 'offline')
    return k0, k1


def evalDCF(party: SemiHonestParty, x: GroupElements, key: DCFKey = None, filename=None,
            sec_para=config.sec_para, DEBUG=config.DEBUG):
    """
    This function evaluates DCF at key with public value x
    :param filename:
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
    inverse = key.inverse
    identifier_result = 0
    for i in range(x.bitlen):
        if DEBUG:
            print(f'[INFO] {i} Iteration for party {party.party_id}:')
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
    party.eliminate_start_marker('evalDCF')
    return action_bit ^ identifier_result ^ (inverse * party.party_id)


def keygenCorrelatedDCF(x: GroupElements, party: TrustedDealer, inverse=None,
                        sec_para=config.sec_para, filename=None,
                        local_transfer=True, seed=config.seed, DEBUG=config.DEBUG):
    """
    This function generates comparison at k+r, i.e. x<k -> (x+r)<(k+r)
    :param inverse: None for automatic judgement (recommended)
    :param x:
    :param party:
    :param sec_para:
    :param filename:
    :param local_transfer:
    :param seed:
    :param DEBUG:
    :return:
    """
    party.set_start_marker('keygenCorrelatedDCF', 'offline')
    mask_0 = sampleGroupElements(x.bitlen, x.scalefactor, seed)
    mask_1 = sampleGroupElements(x.bitlen, x.scalefactor, seed)
    reconstructed_x = x + mask_0 + mask_1
    _k0, _k1 = keygenDCF(x=reconstructed_x, party=party, sec_para=sec_para, inverse=inverse,
                         filename=filename, local_transfer=False, DEBUG=DEBUG)
    k0 = Correlated_DCFKey()
    k1 = Correlated_DCFKey()
    k0.init_from_DCFKey(_k0)
    k1.init_from_DCFKey(_k1)
    k0.r = mask_0
    k1.r = mask_1
    if local_transfer:
        if filename is None:
            filename_0 = f'rDCF_{x.bitlen}_{x.scalefactor}_0.key'
            filename_1 = f'rDCF_{x.bitlen}_{x.scalefactor}_1.key'
            filename = [filename_0, filename_1]
        party.send(k0, filename[0])
        party.send(k1, filename[1])
    party.eliminate_start_marker('keygenCorrelatedDCF', 'offline')
    return k0, k1


def evalCorrelatedDCF(party: SemiHonestParty, x: GroupElements, key: Correlated_DCFKey = None,
                      filename=None, sec_para=config.sec_para, DEBUG=config.DEBUG):
    """
    This function returns the DCF result at place k+r, i.e. x<k -> x+r<k+r
    :param party:
    :param x:
    :param key:
    :param filename:
    :param sec_para:
    :param DEBUG:
    :return:
    """
    party.set_start_marker(func='evalCorrelatedDCF')
    if filename is None:
        assert (key is not None), "We need at least key or keyfile to continue."
    else:
        key = party.local_recv(filename=filename)
    new_x = x + key.r
    party.send(new_x)
    recv = party.recv()
    reconstructed_x = new_x + recv
    if DEBUG:
        print(f'==========DEBUG INFO FOR {party.party_id} @ evalCorrDCF==========')
        print(f'x+r = {new_x.value}')
        print(f'x+r+recv = {reconstructed_x.value}')
        print('==========DEBUG @ evalCorrDPF END==========')
    del new_x
    result = evalDCF(party=party, x=reconstructed_x, key=key, sec_para=sec_para, DEBUG=DEBUG)
    party.eliminate_start_marker(func='evalCorrelatedDCF')
    return result
