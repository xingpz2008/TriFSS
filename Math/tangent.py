import Pythonic_TriFSS.Configs.fixed_point_repr as repr_config
import Pythonic_TriFSS.Configs.math as config
from Pythonic_TriFSS.Common.group_elements import GroupElements
from Pythonic_TriFSS.Communication.semi_honest_party import SemiHonestParty
from Pythonic_TriFSS.Communication.dealer import TrustedDealer
from Pythonic_TriFSS.Utils.construct_LUT import tan_val, tan_coefficients
from Pythonic_TriFSS.General_MPC.Mod import Mod_offline, Mod
from Pythonic_TriFSS.General_MPC.Containment import Containment_Offline, Containment
from Pythonic_TriFSS.Common.tensor import TriFSSTensor
from Pythonic_TriFSS.FSS.dpf import keygenCorrelatedDPF, evalAllDPF
from Pythonic_TriFSS.Cleartext.cleartext_lib import clear_bits_removal
from Pythonic_TriFSS.General_MPC.B2A import generate_massive_cross_term_triplet, tensor_like_B2A
from Pythonic_TriFSS.General_MPC.Decompose import digit_decomposition, digit_decomposition_offline
from Pythonic_TriFSS.General_MPC.Arithmetic import arithmetic_mul, arithmetic_mul_offline


def tan_offline(party: TrustedDealer, bitlen=repr_config.bitlen,
                scale=repr_config.scalefactor, segNum=1):
    """
    This function generates offline assistance data for tan function
    :param party:
    :param bitlen:
    :param scale:
    :param segNum:
    :return:
    """
    file_dict = dict()
    file_dict['tan_coefficients'] = tan_coefficients(save=True)
    if not segNum > 1:
        file_dict['tan_val'] = tan_val(save=True, key_bitlen=scale, key_scale=scale)
    else:
        for i in range(segNum):
            file_dict[f'tan_val_{i}'] = tan_val(save=True, key_bitlen=int(scale / segNum), key_scale=scale,
                                                segSeq=i, segLen=int(scale / segNum))
        # Now start with the real offline.
    party.set_start_marker(func='tan', func_type='offline')

    # For Modular operation, we need B2A offline (generate cross triples)
    file_dict['Mod'] = Mod_offline(party=party, N=1, bitlen=(1 + scale), scale=scale,
                                   local_transfer=True, unsigned=True)
    # For Containment pack, we need containment offline
    knots_list = TriFSSTensor([GroupElements(0, bitlen=(1 + scale)), GroupElements(0.5, bitlen=(1 + scale)),
                               GroupElements((1 - (1 / (2 ** scale))), bitlen=(1 + scale))])
    # Here we need an extra B2A
    file_dict['Ctn'] = Containment_Offline(party=party, knots_list=knots_list, local_transfer=True, unsigned=True)
    file_dict['Ctn_B2A_a'] = generate_massive_cross_term_triplet(number=2, party=party,
                                                                 bitlen=bitlen, scale=scale,
                                                                 local_transfer=True)
    file_dict['Ctn_B2A_b'] = generate_massive_cross_term_triplet(number=2, party=party,
                                                                 bitlen=1 + scale, scale=scale,
                                                                 local_transfer=True)

    # For EvalAll, we need one DPF Key.
    # Here we need an extra B2A.
    if not segNum > 1:
        file_dict['DPF'] = keygenCorrelatedDPF(party=party, bitlen=scale, scale=scale,
                                               local_transfer=True,
                                               payload=GroupElements(value=1, bitlen=bitlen, scale=scale))
    else:
        # Now we consider situation with digit decompose
        file_dict['DigDec'] = digit_decomposition_offline(party=party, segLen=int(scale / segNum),
                                                          global_bitlen=scale, global_scale=scale,
                                                          local_transfer=True)

        # Then we need 2 * (segNum - 1) DPF
        for i in range(2 * (segNum - 1)):
            file_dict[f'DPF_{i}'] = keygenCorrelatedDPF(party=party, bitlen=int(scale / segNum),
                                                        scale=scale, local_transfer=True,
                                                        payload=GroupElements(value=1, bitlen=bitlen, scale=scale))

        # After constructing DPF, we need 2 * (segNum - 1) Mult for arithmetic sharing
        for i in range(2 * (segNum - 1)):
            file_dict[f'A_Mul_{i}'] = arithmetic_mul_offline(party=party, bitlen=bitlen,
                                                             scale=scale, local_transfer=True)
    party.send(file_dict, f'tangent_file_dict_{bitlen}_{scale}.dict')
    party.eliminate_start_marker(func='tan', func_type='offline')


def tan(x: GroupElements, party: SemiHonestParty, file_dict: str = None, segNum=1,
        is_leaf_func=False, DEBUG=config.DEBUG):
    """
    # TODO: Verify Correctness
    # TODO: Consider applying segmentation
    This function returns tan(pi*x)
    :param segNum:
    :param file_dict:
    :param DEBUG:
    :param x:
    :param party:
    :param is_leaf_func: This var indicates if we need further division of the trigonometric function. Not used at this
           moment.
    :return:
    """
    assert (segNum == 1), 'Segmentation is currently unavailable for tan!'
    party.set_start_marker(func='tan')
    if file_dict is None:
        file_dict: dict = party.local_recv(f'tangent_file_dict_{x.bitlen}_{x.scalefactor}.dict')
    else:
        file_dict: dict = party.local_recv(filename=file_dict)
    sin_coefficient = party.local_recv(filename=file_dict['tan_coefficients'])
    # Range Reduction
    x_ = clear_bits_removal(x, (x.bitlen - 1 - x.scalefactor))

    # Period Reflection:
    Moded_x = Mod(party=party, x=x_, N=GroupElements(1, bitlen=x_.bitlen, scale=x_.scalefactor),
                  offline_pack_file=file_dict['Mod'][party.party_id])

    # Specialized Transformation
    Ctn_res = Containment(party=party, x=Moded_x, offline_pack_file=file_dict['Ctn'][party.party_id])
    Arithmetic_Ctn_a = tensor_like_B2A(x=Ctn_res, triplet=file_dict['Ctn_B2A_a'][party.party_id], party=party,
                                       bitlen=x.bitlen, scale=x.scalefactor)
    Arithmetic_Ctn_b = tensor_like_B2A(x=Ctn_res, triplet=file_dict['Ctn_B2A_b'][party.party_id], party=party,
                                       bitlen=1 + x_.scalefactor, scale=x_.scalefactor)
    Arithmetic_Ctn_c = Arithmetic_Ctn_b
    Arithmetic_Ctn_a.downgrade_to_non_thread_tensor()
    Arithmetic_Ctn_b.downgrade_to_non_thread_tensor()
    Arithmetic_Ctn_c.downgrade_to_non_thread_tensor()
    coefficients_a = GroupElements(value=0, bitlen=x.bitlen, scale=x.scalefactor)
    coefficients_b = GroupElements(value=0, bitlen=1 + x_.scalefactor, scale=x_.scalefactor)
    coefficients_c = GroupElements(value=0, bitlen=1 + x_.scalefactor, scale=x_.scalefactor)
    for i in range(2):
        coefficients_a = coefficients_a + Arithmetic_Ctn_a[i] * sin_coefficient[i]['a']
        coefficients_b = coefficients_b + Arithmetic_Ctn_b[i] * sin_coefficient[i]['b']
        coefficients_c = coefficients_c + Arithmetic_Ctn_c[i] * sin_coefficient[i]['c']
    new_x = x_ * coefficients_b + coefficients_c

    # Results Retrieval
    new_x = clear_bits_removal(new_x, 1)
    if not segNum > 1:
        dpf_vector = evalAllDPF(party=party, x=GroupElements(value=0, bitlen=x_.scalefactor),
                                filename=file_dict['DPF'][party.party_id], enable_cache=True, return_arithmetic=True)
        dpf_vector.update_to_thread_tensor(party=party)
        r: GroupElements = party.local_recv(file_dict['DPF'][party.party_id]).r
        party.send(r - new_x)  # Reconstruct r-x
        recv: GroupElements = party.recv()
        offset = recv + r - new_x
        shifted = dpf_vector.vector_left_shift(offset=offset)
        tan_value = party.local_recv(filename=file_dict['tan_val'])
        result_vector = shifted * tan_value
        final = result_vector.get_all_added()
        final = coefficients_a * final
        party.eliminate_start_marker(func='tan')
        return final
    else:
        assert (x.scalefactor % segNum == 0), 'Unsupported scale for Digit Decomposition!'
        decomposed_x = digit_decomposition(x=new_x, segLen=int(new_x.bitlen / segNum),
                                           party=party, offline_data=file_dict['DigDec'][party.party_id])
        dpf_vector_list = []
        for i in range(2 * (segNum - 1)):
            # In this iteration, we evaluate and shift DPF on two value, high position x and low position x.
            dpf_vector = evalAllDPF(party=party, x=GroupElements(value=0, bitlen=decomposed_x[i].bitlen),
                                    filename=file_dict[f'DPF_{i}'][party.party_id], enable_cache=True,
                                    return_arithmetic=True)
            dpf_vector.update_to_thread_tensor(party=party)
            r: GroupElements = party.local_recv(file_dict[f'DPF_{i}'][party.party_id]).r
            party.send(r - decomposed_x[i])
            recv: GroupElements = party.recv()
            offset = recv + r - decomposed_x[i]
            shifted = dpf_vector.vector_left_shift(offset=offset)
            dpf_vector_list.append(shifted)
        # Then we use the two vector to calculate.
        # For sine, the equation holds:
        # sin(x+y) = 0 sin(x) 2 cos(y)+1 cos(x) 3 sin(y)
        # Digit Array [0] indicates the data of lower position
        result_list = []
        for i in range(2 * (segNum - 1)):
            pass
        final = GroupElements(0)
        front_result = arithmetic_mul(x=result_list[0], y=result_list[2],
                                      party=party, offline_data=file_dict[f'A_Mul_{0}'][party.party_id])
        back_result = arithmetic_mul(x=result_list[1], y=result_list[3],
                                     party=party, offline_data=file_dict[f'A_Mul_{1}'][party.party_id])
        final = front_result + back_result
        party.eliminate_start_marker(func='tan')
        return final
