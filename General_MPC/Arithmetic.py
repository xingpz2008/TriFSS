from typing import Union

from Pythonic_TriFSS.Common.group_elements import GroupElements
from Pythonic_TriFSS.General_MPC.dataClass.triplet import BeaverTriplets
from Pythonic_TriFSS.General_MPC.dataClass.protocol_offline_pack import arithmetic_mult_pack
from Pythonic_TriFSS.Utils.random_sample import sampleGroupElements
import Pythonic_TriFSS.Configs.fixed_point_repr as repr_config
from Pythonic_TriFSS.Communication.dealer import TrustedDealer
from Pythonic_TriFSS.Communication.semi_honest_party import SemiHonestParty


def generate_beaver_triplet(bitlen=repr_config.bitlen,
                            scale=repr_config.scalefactor,
                            seed=repr_config.seed):
    """
    This function generates beaver triplets for shares multiplication.
    :param bitlen:
    :param scale:
    :param seed:
    :return:
    """
    mask_a_0 = sampleGroupElements(bitlen=bitlen, scale=scale, seed=seed)
    mask_a_1 = sampleGroupElements(bitlen=bitlen, scale=scale, seed=seed)
    a = mask_a_0 + mask_a_1
    mask_b_0 = sampleGroupElements(bitlen=bitlen, scale=scale, seed=seed)
    mask_b_1 = sampleGroupElements(bitlen=bitlen, scale=scale, seed=seed)
    b = mask_b_0 + mask_b_1
    c = a * b
    mask_c = sampleGroupElements(bitlen=bitlen, scale=scale, seed=seed)
    c = c - mask_c
    return BeaverTriplets(a=mask_a_0, b=mask_b_0, ab_b=c), BeaverTriplets(a=mask_a_1, b=mask_b_1, ab_b=mask_c)


def arithmetic_mul_offline(party: TrustedDealer,
                           bitlen=repr_config.bitlen,
                           scale=repr_config.scalefactor,
                           local_transfer=True,
                           filename: [str, str] = None,
                           seed=repr_config.seed):
    """
    This function is the offline phase of arithmetic multiplication
    :param party:
    :param bitlen:
    :param scale:
    :param local_transfer:
    :param filename:
    :param seed:
    :return:
    """
    party.set_start_marker(func='Mult', func_type='offline')
    pack_0 = arithmetic_mult_pack()
    pack_1 = arithmetic_mult_pack()
    pack_0.triplet, pack_1.triplet = generate_beaver_triplet(bitlen=bitlen,
                                                             scale=scale,
                                                             seed=seed)
    if local_transfer:
        if filename is None:
            filename_0 = f'A_MUL_{bitlen}_{scale}_0.pack'
            filename_1 = f'A_MUL_{bitlen}_{scale}_1.pack'
            filename = [filename_0, filename_1]
        party.send(data=pack_0, name=filename[0])
        party.send(data=pack_1, name=filename[1])
        party.eliminate_start_marker('Mult', 'offline')
        return filename
    else:
        party.eliminate_start_marker(func='Mult', func_type='offline')
        return pack_0, pack_1


def arithmetic_mul(x: GroupElements, y: GroupElements,
                   party: SemiHonestParty, offline_data: Union[str, arithmetic_mult_pack]):
    """
    This function returns shares of X*Y for Arithmetic share X and Y.
    :param x:
    :param y:
    :param party:
    :param offline_data:
    :return:
    """
    party.set_start_marker(func='Mult')
    if type(offline_data) is str:
        offline_data = party.local_recv(offline_data)
    e = x - offline_data.triplet.a
    f = y - offline_data.triplet.b
    party.send([e, f])
    recv = party.recv()
    recv_e, recv_f = recv[0], recv[1]
    e = e + recv_e
    f = f + recv_f
    z = (e * f * party.party_id) + (f * offline_data.triplet.a) + \
        (e * offline_data.triplet.b) + offline_data.triplet.ab_b
    party.eliminate_start_marker(func='Mult')
    return z
