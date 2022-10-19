from typing import Union

from Pythonic_TriFSS.Communication.semi_honest_party import SemiHonestParty
from Pythonic_TriFSS.Communication.dealer import TrustedDealer
from Pythonic_TriFSS.General_MPC.dataClass.triplet import BooleanMultTriplets
from Pythonic_TriFSS.Utils.random_sample import sampleBit
import Pythonic_TriFSS.Configs.fixed_point_repr as repr_config
from Pythonic_TriFSS.General_MPC.dataClass.protocol_offline_pack import boolean_AND_pack


def generate_boolean_mult_triplet(seed=repr_config.seed):
    mask_a_0 = sampleBit(seed=seed)
    mask_a_1 = sampleBit(seed=seed)
    a = mask_a_0 ^ mask_a_1
    mask_b_0 = sampleBit(seed=seed)
    mask_b_1 = sampleBit(seed=seed)
    b = mask_b_0 ^ mask_b_1
    c = a * b
    mask_c = sampleBit(seed=seed)
    c = c ^ mask_c
    triplet_0 = BooleanMultTriplets(a=mask_a_0, b=mask_b_0, ab_b=c)
    triplet_1 = BooleanMultTriplets(a=mask_a_1, b=mask_b_1, ab_b=mask_c)
    return triplet_0, triplet_1


def boolean_and_offline(party: TrustedDealer, local_transfer=True, filename: [str, str] = None, seed=repr_config.seed):
    """
    This function generates Boolean AND offline data.
    :param party:
    :param local_transfer:
    :param filename:
    :param seed:
    :return:
    """
    party.set_start_marker(func='B_AND', func_type='offline')
    pack_0 = boolean_AND_pack()
    pack_1 = boolean_AND_pack()
    pack_0.triplet, pack_1.triplet = generate_boolean_mult_triplet(seed=seed)
    if local_transfer:
        if filename is None:
            filename_0 = f'B_AND_0.pack'
            filename_1 = f'B_AND_1.pack'
            filename = [filename_0, filename_1]
        party.send(data=pack_0, name=filename[0])
        party.send(data=pack_1, name=filename[1])
        party.eliminate_start_marker('B_AND', 'offline')
        return filename
    else:
        party.eliminate_start_marker(func='B_AND', func_type='offline')
        return pack_0, pack_1


def boolean_and(x: int, y: int, party: SemiHonestParty, offline_data: Union[str, boolean_AND_pack]):
    """
    This function returns share of X*Y where X and Y are bit shares.
    :param offline_data:
    :param x:
    :param y:
    :param party:
    :return:
    """
    assert (x == 0 or x == 1), 'Only Boolean can be accepted'
    assert (y == 0 or y == 1), 'Only Boolean can be accepted'
    party.set_start_marker(func='B_AND', func_type='online')
    if type(offline_data) is str:
        offline_data = party.local_recv(offline_data)
    e = x ^ offline_data.triplet.a
    f = y ^ offline_data.triplet.b
    party.send([e, f])
    recv = party.recv()
    recv_e, recv_f = recv[0], recv[1]
    e = e ^ recv_e
    f = f ^ recv_f
    z = (party.party_id * e * f) ^ (f * offline_data.triplet.a) ^ \
        (e * offline_data.triplet.b) ^ offline_data.triplet.ab_b
    party.eliminate_start_marker(func='B_AND', func_type='online')
    return z
