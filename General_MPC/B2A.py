from Pythonic_TriFSS.Common.group_elements import GroupElements
from Pythonic_TriFSS.Utils.random_sample import sampleGroupElements
from Pythonic_TriFSS.General_MPC.dataClass.triplet import CrossTermTriplets
import Pythonic_TriFSS.Configs.fixed_point_repr as config
from Pythonic_TriFSS.Communication.semi_honest_party import SemiHonestParty
from Pythonic_TriFSS.Communication.dealer import TrustedDealer


def generate_cross_term_triplet(bitlen=config.bitlen, scale=config.scalefactor,
                                executor: TrustedDealer = None, filename: str = None) \
        -> [CrossTermTriplets, CrossTermTriplets]:
    """
    This function generates xy mult triplets for P0 have x, P1 have y (Not additive shares)
    :param filename:
    :param executor:
    :param bitlen:
    :param scale:
    :return:
    """
    if executor is not None:
        executor.set_start_marker('B2A', 'offline')
    a = sampleGroupElements(bitlen, scale, config.seed)
    b = sampleGroupElements(bitlen, scale, config.seed)
    r = sampleGroupElements(bitlen, scale, config.seed)
    z = a * b
    z = z - r
    if executor is not None:
        executor.send(data=CrossTermTriplets(a, z), name=filename)
        executor.send(data=CrossTermTriplets(b, r), name=filename)
        executor.eliminate_start_marker('B2A', 'offline')
    else:
        return CrossTermTriplets(a, z), CrossTermTriplets(b, r)


def B2A(x: int, triplet, party: SemiHonestParty, bitlen=config.bitlen, scale=config.scalefactor, DEBUG=False) \
        -> GroupElements:
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
