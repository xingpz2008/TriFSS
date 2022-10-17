import Pythonic_TriFSS.Configs.fixed_point_repr as repr_config
import Pythonic_TriFSS.Configs.math as config
from Pythonic_TriFSS.Common.group_elements import GroupElements
from Pythonic_TriFSS.Communication.semi_honest_party import SemiHonestParty
from Pythonic_TriFSS.Communication.dealer import TrustedDealer
from Pythonic_TriFSS.Utils.construct_LUT import sin_val, sin_coefficients
from Pythonic_TriFSS.General_MPC.Mod import Mod_offline, Mod
from Pythonic_TriFSS.General_MPC.Containment import Containment_Offline, Containment
from Pythonic_TriFSS.Common.tensor import TriFSSTensor
from Pythonic_TriFSS.FSS.dpf import keygenCorrelatedDPF, evalAllDPF
from Pythonic_TriFSS.Cleartext.cleartext_lib import clear_bits_removal
from Pythonic_TriFSS.General_MPC.B2A import generate_massive_cross_term_triplet, tensor_like_B2A


# TODO: Add trigonometric

def sin_offline(party: TrustedDealer, bitlen=repr_config.bitlen, scale=repr_config.scalefactor):
    """
    This function generates offline assistance data for sine function
    :param scale:
    :param bitlen:
    :param party:
    :return:
    """
    # We first construct database, which should not be included in time statistics.
    file_dict = dict()
    file_dict['sin_val'] = sin_val(save=True, key_bitlen=scale, key_scale=scale)
    file_dict['sin_coefficient'] = sin_coefficients(save=True)

    # Now start with the real offline.
    party.set_start_marker(func='sin', func_type='offline')

    # For Modular operation, we need B2A offline (generate cross triples)
    file_dict['Mod'] = Mod_offline(party=party, N=2, bitlen=(2 + scale), scale=scale,
                                   local_transfer=True, unsigned=True)
    # For Containment pack, we need containment offline
    knots_list = TriFSSTensor([GroupElements(0, bitlen=(2 + scale)), GroupElements(0.5, bitlen=(2 + scale)),
                               GroupElements(1.0, bitlen=(2 + scale)), GroupElements(1.5, bitlen=(2 + scale)),
                               GroupElements((2 - (1 / (2 ** scale))), bitlen=(2 + scale))])
    # Here we need an extra B2A
    file_dict['Ctn'] = Containment_Offline(party=party, knots_list=knots_list, local_transfer=True, unsigned=True)
    file_dict['Ctn_B2A_a'] = generate_massive_cross_term_triplet(number=4, party=party,
                                                                 bitlen=bitlen, scale=scale,
                                                                 local_transfer=True)
    file_dict['Ctn_B2A_b'] = generate_massive_cross_term_triplet(number=4, party=party,
                                                                 bitlen=2 + scale, scale=scale,
                                                                 local_transfer=True)
    file_dict['Ctn_B2A_c'] = generate_massive_cross_term_triplet(number=4, party=party,
                                                                 bitlen=2 + scale, scale=scale,
                                                                 local_transfer=True)

    # For EvalAll, we need one DPF Key.
    # Here we need an extra B2A.
    file_dict['DPF'] = keygenCorrelatedDPF(party=party, bitlen=scale, scale=scale, local_transfer=True)
    file_dict['DPF_B2A'] = generate_massive_cross_term_triplet(number=(2 ** scale), party=party,
                                                               bitlen=bitlen, scale=scale, local_transfer=True)
    party.send(file_dict, f'sine_file_dict_{bitlen}_{scale}.dict')
    party.eliminate_start_marker(func='sin', func_type='offline')


def sin(x: GroupElements, party: SemiHonestParty, file_dict: str = None, is_leaf_func=False, DEBUG=config.DEBUG):
    """
    # TODO: Verify Correctness
    This function returns sin(pi*x)
    :param file_dict:
    :param DEBUG:
    :param x:
    :param party:
    :param is_leaf_func: This var indicates if we need further division of the trigonometric function. Not used at this
           moment.
    :return:
    """
    party.set_start_marker(func='sin')
    if file_dict is None:
        file_dict: dict = party.local_recv(f'sine_file_dict_{x.bitlen}_{x.scalefactor}.dict')
    else:
        file_dict: dict = party.local_recv(filename=file_dict)
    sin_coefficient = party.local_recv(filename=file_dict['sin_coefficient'])
    # Range Reduction
    x_ = clear_bits_removal(x, (x.bitlen - 2 - x.scalefactor))

    # Period Reflection:
    Moded_x = Mod(party=party, x=x_, N=GroupElements(2, bitlen=x_.bitlen, scale=x_.scalefactor),
                  offline_pack_file=file_dict['Mod'][party.party_id])

    # Specialized Transformation
    Ctn_res = Containment(party=party, x=Moded_x, offline_pack_file=file_dict['Ctn'][party.party_id])
    Arithmetic_Ctn_a = tensor_like_B2A(x=Ctn_res, triplet=file_dict['Ctn_B2A_a'][party.party_id], party=party,
                                       bitlen=x.bitlen, scale=x.scalefactor)
    Arithmetic_Ctn_b = tensor_like_B2A(x=Ctn_res, triplet=file_dict['Ctn_B2A_b'][party.party_id], party=party,
                                       bitlen=2 + x_.scalefactor, scale=x_.scalefactor)
    Arithmetic_Ctn_c = tensor_like_B2A(x=Ctn_res, triplet=file_dict['Ctn_B2A_c'][party.party_id], party=party,
                                       bitlen=2 + x_.scalefactor, scale=x_.scalefactor)
    Arithmetic_Ctn_a.downgrade_to_non_thread_tensor()
    Arithmetic_Ctn_b.downgrade_to_non_thread_tensor()
    Arithmetic_Ctn_c.downgrade_to_non_thread_tensor()
    coefficients_a = GroupElements(value=0, bitlen=x.bitlen, scale=x.scalefactor)
    coefficients_b = GroupElements(value=0, bitlen=2 + x_.scalefactor, scale=x_.scalefactor)
    coefficients_c = GroupElements(value=0, bitlen=2 + x_.scalefactor, scale=x_.scalefactor)
    for i in range(4):
        coefficients_a = coefficients_a + Arithmetic_Ctn_a[i] * sin_coefficient[i]['a']
        coefficients_b = coefficients_b + Arithmetic_Ctn_b[i] * sin_coefficient[i]['b']
        coefficients_c = coefficients_c + Arithmetic_Ctn_c[i] * sin_coefficient[i]['c']
    new_x = x_ * coefficients_b + coefficients_c

    # Results Retrieval
    new_x = clear_bits_removal(new_x, 2)
    dpf_vector = evalAllDPF(party=party, x=GroupElements(value=0, bitlen=x_.scalefactor),
                            filename=file_dict['DPF'][party.party_id], enable_cache=True)
    Arithmetic_DPF = tensor_like_B2A(x=dpf_vector, triplet=file_dict['DPF_B2A'][party.party_id], party=party,
                                     bitlen=x.bitlen, scale=x.scalefactor)
    Arithmetic_DPF.update_to_thread_tensor(party=party)
    r: GroupElements = party.local_recv(file_dict['DPF'][party.party_id]).r
    party.send(r - new_x)  # Reconstruct r-x
    recv: GroupElements = party.recv()
    offset = recv + r - new_x
    shifted = Arithmetic_DPF.vector_left_shift(offset=offset)
    sin_value = party.local_recv(filename=file_dict['sin_val'])
    result_vector = shifted * sin_value
    final = result_vector.get_all_added()
    final = coefficients_a * final
    party.eliminate_start_marker(func='sin')
    return final
