from typing import List

from Pythonic_TriFSS.Common.group_elements import GroupElements
from Pythonic_TriFSS.Utils.random_sample import sampleGroupElements
from Pythonic_TriFSS.General_MPC.dataClass.triplet import CrossTermTriplets
import Pythonic_TriFSS.Configs.fixed_point_repr as repr_config
from Pythonic_TriFSS.Communication.semi_honest_party import SemiHonestParty
from Pythonic_TriFSS.Communication.dealer import TrustedDealer
import Pythonic_TriFSS.Configs.general_mpc as config
from Pythonic_TriFSS.Utils.thread_tool import get_loc_list
from Pythonic_TriFSS.Common.tensor import TriFSSTensor
from Pythonic_TriFSS.Communication.dataClass.thread import TriFSSThread


def generate_cross_term_triplet(bitlen=repr_config.bitlen,
                                scale=repr_config.scalefactor,
                                local_transfer=True,
                                mark=True,
                                executor: TrustedDealer = None,
                                filename: [str, str] = None,
                                seed=repr_config.seed) \
        -> [CrossTermTriplets, CrossTermTriplets]:
    """
    This function generates xy mult triplets for P0 have x, P1 have y (Not additive shares)
    # TODO: How to process multiplication loss?
    :param mark:
    :param seed:
    :param local_transfer:
    :param filename:
    :param executor:
    :param bitlen:
    :param scale:
    :return:
    """
    if executor is not None:
        if mark:
            executor.set_start_marker('B2A', 'offline')
    a = sampleGroupElements(bitlen, scale, seed)
    b = sampleGroupElements(bitlen, scale, seed)
    r = sampleGroupElements(bitlen, scale, seed)
    # a = GroupElements(3)
    # b = GroupElements(2)
    # r = GroupElements(1)
    z = a * b
    z = z - r
    if executor is not None:
        if local_transfer:
            if filename is None:
                filename_0 = f'B2A_{bitlen}_{scale}_0.triplet'
                filename_1 = f'B2A_{bitlen}_{scale}_1.triplet'
                filename = [filename_0, filename_1]
            executor.send(data=CrossTermTriplets(a, z), name=filename[0])
            executor.send(data=CrossTermTriplets(b, r), name=filename[1])
            executor.eliminate_start_marker('B2A', 'offline')
            return filename
    if mark:
        executor.eliminate_start_marker('B2A', 'offline')
    return CrossTermTriplets(a, z), CrossTermTriplets(b, r)


def generate_range_triplets(interval: (int, int),
                            result_vector_0: TriFSSTensor,
                            result_vector_1: TriFSSTensor,
                            party: TrustedDealer,
                            include_right=False,
                            bitlen=repr_config.bitlen,
                            scale=repr_config.scalefactor,
                            seed=repr_config.seed):
    """
    This function generates triplets with certain range in single thread.
    :param result_vector_1:
    :param result_vector_0:
    :param interval:
    :param party:
    :param include_right:
    :param bitlen:
    :param scale:
    :param filename:
    :param seed:
    :return:
    """
    for i in range(interval[0], interval[1] + int(include_right)):
        result_vector_0[i], result_vector_1[i] = generate_cross_term_triplet(bitlen=bitlen,
                                                                             scale=scale,
                                                                             local_transfer=False,
                                                                             mark=False,
                                                                             executor=party,
                                                                             filename=None,
                                                                             seed=seed)


def generate_massive_cross_term_triplet(number,
                                        party: TrustedDealer,
                                        bitlen=repr_config.bitlen,
                                        scale=repr_config.scalefactor,
                                        local_transfer=True,
                                        thread=config.default_thread,
                                        filename: [str, str] = None,
                                        seed=repr_config.seed):
    """
    This function generates massive cross_term_triplets.
    :param thread:
    :param number:
    :param bitlen:
    :param scale:
    :param local_transfer:
    :param party:
    :param filename:
    :param seed:
    :return:
    """
    party.set_start_marker("B2A", 'offline')
    segmentation = get_loc_list(fullNum=number, threadNum=thread)
    if 0 not in segmentation:
        segmentation = [0] + segmentation
    result_vector_0 = TriFSSTensor([None] * number)
    result_vector_1 = TriFSSTensor([None] * number)
    for i in range(thread):
        new_thread = TriFSSThread(func=generate_range_triplets, args=[(segmentation[i], segmentation[i + 1]),
                                                                      result_vector_0,
                                                                      result_vector_1,
                                                                      party,
                                                                      int((i + 1) == thread),
                                                                      bitlen,
                                                                      scale,
                                                                      seed])
        party.add_thread(new_thread)
    party.start_all_thread()
    if local_transfer:
        if filename is None:
            filename_0 = f'B2A_massive_{bitlen}_{scale}_{number}_0.triplet'
            filename_1 = f'B2A_massive_{bitlen}_{scale}_{number}_1.triplet'
            filename = [filename_0, filename_1]
        party.send(data=result_vector_0, name=filename[0])
        party.send(data=result_vector_1, name=filename[1])
    party.eliminate_start_marker("B2A", 'offline')
    return result_vector_0, result_vector_1


def B2A(x: int, triplet, party: SemiHonestParty, bitlen=repr_config.bitlen,
        scale=repr_config.scalefactor, DEBUG=False) -> GroupElements:
    """
    This is the protocol converts Boolean shares to arithmetic Shares (1 -> l)
    Triplets should be read locally, while delta to be read at online stage
    :param DEBUG:
    :param scale:
    :param bitlen:
    :param party:
    :param x:
    :param triplet:
    :return:
    """
    assert (party.party_id == 0 or party.party_id == 1), "Invalid party id"
    assert (x == 0 or x == 1), 'Only Boolean can be accepted'
    assert (type(triplet) in [str, CrossTermTriplets, None]), f"Can not identify triplets in format {type(triplet)}"
    party.set_start_marker(func='B2A', func_type='online')
    if triplet is None:
        # TODO: Consider Internet Comm for dealer
        raise NotImplementedError("Mult triplets can only be read locally currently.")
    if type(triplet) is str:
        triplet = party.local_recv(triplet)
    x_in_Group = GroupElements(x, bitlen=bitlen, scale=scale)
    delta = x_in_Group - triplet.a
    party.send(delta)
    recv: GroupElements = party.recv()
    if party.party_id == 0:
        mult_result = recv * x + triplet.ab_b
    else:
        mult_result = recv * triplet.a + triplet.ab_b
    if DEBUG:
        print(f'\n==========DEBUG INFO for Party {party.party_id}==========')
        print(f'x = {x}')
        print("Triplets:")
        print(f"    a = {triplet.a.value} / {triplet.a._GroupElements__init_real_value}")
        print(f"    [ab] = {triplet.ab_b.value} / {triplet.ab_b._GroupElements__init_real_value}")
        print(f"Delta (x-a) = {delta.value} / {delta._GroupElements__init_real_value}")
        print(f"Recv = {recv.value} / {recv._GroupElements__init_real_value}")
        print(f'Mult Res (delta*x/b) = {mult_result.value} / {mult_result._GroupElements__init_real_value}')
        print(f'Shares (x-xy) = {(x_in_Group - mult_result).value} / '
              f'{(x_in_Group - mult_result)._GroupElements__init_real_value}')
        print('==========DEBUG END==========\n')
    result = x_in_Group - (mult_result * 2)
    party.eliminate_start_marker(func='B2A', func_type='online')
    return result


def tensor_like_B2A(x: List,
                    triplet: str,
                    party: SemiHonestParty,
                    bitlen=repr_config.bitlen,
                    scale=repr_config.scalefactor,
                    thread=config.default_thread,
                    DEBUG=config.DEBUG) -> TriFSSTensor:
    """
    This function executes the B2A on the TriFSSTensor with multiple threads.
    :param x:
    :param triplet:
    :param party:
    :param bitlen:
    :param scale:
    :param thread:
    :param DEBUG:
    :return:
    """
    assert (party.party_id == 0 or party.party_id == 1), "Invalid party id"
    assert (type(triplet) in [str]), f"Can not identify triplets in format {type(triplet)}"
    party.set_start_marker(func='B2A', func_type='online')
    # We load the triplet pack from local file, the loaded one is [triplet[0], triplet[1], ...]
    # TODO: We still need to modify triple pack class as we need 2 tensors, 1 for a, one for ab_b
    triplet_pack: TriFSSTensor = party.local_recv(triplet)
    delta_tensor = TriFSSTensor([None] * len(x))
    segmentation = [0] + get_loc_list(fullNum=len(x), threadNum=thread)
    x_in_group = TriFSSTensor([None] * len(x))

    # First, we call new thread to process delta-x
    def construct_delta(index: [int, int], include_right=False):
        for j in range(index[0], index[1] + int(include_right)):
            x_in_group[j] = GroupElements(x[j], bitlen=bitlen, scale=scale)
            delta_tensor[j] = GroupElements(x[j], bitlen=bitlen, scale=scale) - triplet_pack[j].a

    for i in thread:
        new_thread = TriFSSThread(func=construct_delta,
                                  args=[[segmentation[i], segmentation[i + 1]], ((i + 1) == thread)])
        party.add_thread(new_thread)
    party.start_all_thread()
    party.send(delta_tensor)
    recv_tensor: TriFSSTensor = party.recv()
    party.empty_thread_pool()
    # Then, we re-construct the multi_res
    if party.party_id == 0:
        # TODO: Fix here
        mult_res_vector = recv_tensor * x_in_group
    else:
        mult_res_vector = recv_tensor * triplet_pack
    pass
