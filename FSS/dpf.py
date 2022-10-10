import Pythonic_TriFSS.Configs.fss as config
from Pythonic_TriFSS.Common.group_elements import GroupElements
from Pythonic_TriFSS.Utils.prg import prg
from Pythonic_TriFSS.Utils.random_sample import sampleGroupElements
from Pythonic_TriFSS.FSS.dataClass.correction_words import CW_DPF
from Pythonic_TriFSS.FSS.dataClass.function_key import DPFKey, Correlated_DPFKey
from Pythonic_TriFSS.Communication.semi_honest_party import SemiHonestParty
from Pythonic_TriFSS.Communication.dealer import TrustedDealer
from Pythonic_TriFSS.Common.tensor import TriFSSTensor
from Pythonic_TriFSS.Utils.thread_tool import get_loc_list
from Pythonic_TriFSS.Communication.dataClass.thread import TriFSSThread


def keygenDPF(x: GroupElements, party: TrustedDealer, sec_para=config.sec_para, filename=None,
              local_transfer=True, DEBUG=config.DEBUG) \
        -> tuple:
    """
    This function returns the key pair for DPF @ x, payload = 1 currently.
    We sample the first seed from the ring
    :param local_transfer:
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
    if local_transfer:
        if filename is None:
            filename_0 = f'DPF_{x.bitlen}_{x.scalefactor}_0.key'
            filename_1 = f'DPF_{x.bitlen}_{x.scalefactor}_1.key'
            filename = [filename_0, filename_1]
        party.send(k0, name=filename[0])
        party.send(k1, name=filename[1])
    party.eliminate_start_marker('keygenDPF', 'offline')
    return k0, k1


def evalDPF(party: SemiHonestParty, x: GroupElements, key: DPFKey = None, filename=None, enable_cache=False,
            thread=1, sec_para=config.sec_para, mark=True, DEBUG=config.DEBUG):
    """
    This function evaluates DPF at key with the public value x
    # TODO Consider Enable thread
    :param thread:
    :param enable_cache: check if we enable cache optimization
    :param filename:
    :param DEBUG:
    :param sec_para:
    :param party:
    :param key:
    :param x:
    :return:
    """
    if mark:
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
        if enable_cache:
            try:
                prg_res = party.DPF_Dict[level_seed]
            except KeyError as e:
                if DEBUG:
                    print(f'[INFO] Add {level_seed} into dict')
                prg_res = prg(level_seed, sec_para, 'DPF', party=party)
                party.DPF_Dict[level_seed] = prg_res
        else:
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
    if mark:
        party.eliminate_start_marker('evalDPF')
    return action_bit


def keygenCorrelatedDPF(x: GroupElements, party: TrustedDealer, sec_para=config.sec_para, filename=None,
                        local_transfer=True, seed=config.seed, DEBUG=config.DEBUG) -> tuple:
    """
    This function returns the correlated DPF keys. The insight is that, we produce DPF at the random place from group,
    then construct delta and sending to each other.
    :param local_transfer:
    :param x: This is data-independent function
    :param seed:
    :param party:
    :param sec_para:
    :param filename:
    :param DEBUG:
    :return:
    """
    party.set_start_marker('keygenCorrelatedDPF', 'offline')
    r = sampleGroupElements(x.bitlen, x.scalefactor, seed)
    mask = sampleGroupElements(x.bitlen, x.scalefactor, seed)
    k0 = Correlated_DPFKey()
    k1 = Correlated_DPFKey()
    _k0, _k1 = keygenDPF(x=(x + r), party=party, sec_para=sec_para, filename=filename, local_transfer=False,
                         DEBUG=DEBUG)
    k0.init_from_DPFKey(_k0)
    k1.init_from_DPFKey(_k1)
    del _k0, _k1
    k0.r = (r - mask)
    k1.r = mask
    if local_transfer:
        if filename is None:
            filename_0 = f'rDPF_{x.bitlen}_{x.scalefactor}_0.key'
            filename_1 = f'rDPF_{x.bitlen}_{x.scalefactor}_1.key'
            filename = [filename_0, filename_1]
        party.send(k0, filename[0])
        party.send(k1, filename[1])
    party.eliminate_start_marker('keygenCorrelatedDPF', 'offline')
    return k0, k1


def evalCorrelatedDPF(party: SemiHonestParty, x: GroupElements, key: Correlated_DPFKey = None, filename=None,
                      sec_para=config.sec_para, DEBUG=config.DEBUG):
    """
    This function evaluates DPF from a random place r and then reconstruct the to result the correct one.
    :param party:
    :param x:
    :param key:
    :param filename: This indicates the file that storing the serialized key.
    :param sec_para:
    :param DEBUG:
    :return:
    """
    party.set_start_marker(func='evalCorrelatedDPF')
    if filename is None:
        assert (key is not None), "We need at least key or keyfile to continue."
    else:
        key = party.local_recv(filename=filename)
    new_x = x + key.r
    party.send(new_x)
    recv = party.recv()
    reconstructed_x = new_x + recv
    if DEBUG:
        print(f'==========DEBUG INFO FOR {party.party_id} @ evalCorrDPF==========')
        print(f'x+r = {new_x.value}')
        print(f'x+r+recv = {reconstructed_x.value}')
        print('==========DEBUG @ evalCorrDPF END==========')
    del new_x
    result = evalDPF(party=party, x=reconstructed_x, key=key, sec_para=sec_para, DEBUG=DEBUG)
    party.eliminate_start_marker(func='evalCorrelatedDPF')
    return result


def evalAllDPF(party: SemiHonestParty, x: GroupElements, key: Correlated_DPFKey = None, filename=None,
               enable_cache=False, thread=config.full_domain_eval_thread, sec_para=config.sec_para,
               DEBUG=config.DEBUG):
    """
    This function evaluates all the nodes within the input domain.
    returns the bool value tensor
    # TODO: Add correlated DPF for evalAll, when invoking the function, not inside the function
    :param party:
    :param x: The very value of this var is useless, we only use it to specify the group information.
    :param key:
    :param filename:
    :param enable_cache:
    :param thread:
    :param sec_para:
    :param DEBUG:
    :return:
    """
    assert (thread > 0), 'Invalid thread number'
    party.set_start_marker(func='evalAllDPF')
    if filename is None:
        assert (key is not None), "We need at least key or keyfile to continue."
    else:
        key = party.local_recv(filename=filename)
    ring = 2 ** x.bitlen
    result_tensor = TriFSSTensor([None] * ring)
    segmentation = get_loc_list(ring, threadNum=thread)
    if 0 not in segmentation:
        segmentation = [0] + segmentation
    iterator = segmentation[1]
    for i in range(iterator - 1):
        for j in range(thread):
            if segmentation[j] == ring:
                continue
            segmentation[j] += i
            this_x = GroupElements(segmentation[j])
            if DEBUG:
                print(f'[INFO] DPF eval on {segmentation[j]}')
            if party.get_existing_thread_num() < thread:
                new_thread = TriFSSThread(func=evalDPF, args=[party, this_x, key, None,
                                                              enable_cache, 0, sec_para, False, False])
                party.add_thread(new_thread)
            else:
                party.refresh_thread_pool_item(index=j, func=None, args=[[party, this_x, key, None,
                                                                          enable_cache, 0, sec_para, False, False]])
        party.start_all_thread()
        for j in range(thread):
            if segmentation[j] == ring:
                continue
            if DEBUG:
                print(f'[INFO] DPF res write to index {segmentation[j]}')
            result_tensor[segmentation[j]] = party.threadFactory.thread_list[j].get_thread_result()
    # for i in range(ring):
    #     if DEBUG:
    #         if i % (int(0.1 * ring)) == 0:
    #             print(f'[INFO] EvalAll {i / ring * 100}% completed')
    #     this_x = GroupElements(value=None, repr_value=i)
    #     dpf_value = evalDPF(party=party, x=this_x, key=key, enable_cache=enable_cache,
    #                         thread=thread, sec_para=sec_para, DEBUG=False)
    #     result_tensor.add_elements(dpf_value)
    # We do not apply B2A here.
    party.empty_cache_dict()
    party.eliminate_start_marker(func='evalAllDPF')
    return result_tensor
