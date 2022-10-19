from typing import Union

from Pythonic_TriFSS.Common.group_elements import GroupElements
from Pythonic_TriFSS.Communication.dealer import TrustedDealer
from Pythonic_TriFSS.Communication.semi_honest_party import SemiHonestParty
import Pythonic_TriFSS.Configs.fixed_point_repr as repr_config
import Pythonic_TriFSS.Configs.fss as fss_config
from Pythonic_TriFSS.FSS.dpf import evalCorrelatedConstantDPF, keygenCorrelatedConstantDPF
from Pythonic_TriFSS.FSS.dcf import keygenCorrelatedDCF, evalCorrelatedDCF
from Pythonic_TriFSS.General_MPC.dataClass.protocol_offline_pack import wrap_and_all1s_pack, digit_decompose_pack
from Pythonic_TriFSS.General_MPC.Boolean import boolean_and_offline, boolean_and
from Pythonic_TriFSS.General_MPC.B2A import generate_cross_term_triplet, B2A
from Pythonic_TriFSS.Common.tensor import TriFSSTensor
from Pythonic_TriFSS.Cleartext.cleartext_lib import clear_bits_removal


def wrap_and_all_1s_offline(segLen: int, party: TrustedDealer,
                            global_bitlen=repr_config.bitlen, global_scale=repr_config.scalefactor,
                            sec_para=fss_config.sec_para, seed=fss_config.seed,
                            local_transfer=True, filename=None):
    """
    This function generates offline pack for F_wrap&All1s.
    We need one comparison and one equation test.
    # TODO: Consider if the bit len of DCF and DPF can be further reduced. Maybe 1/2 + segLen?
    :param filename:
    :param seed:
    :param sec_para:
    :param global_scale:
    :param local_transfer:
    :param global_bitlen:
    :param segLen:
    :param party:
    :return:
    """
    assert (global_bitlen > (segLen - 1)), 'We require global bitlen bigger than segmentation length - 1'
    assert (global_bitlen % segLen == 0), 'Currently we only support bitlen % segLen == 0'
    party.set_start_marker(func='warp&all1s', func_type='offline')
    pack_0 = wrap_and_all1s_pack()
    pack_1 = wrap_and_all1s_pack()
    # We call x <= 2^segLen
    ring = GroupElements(value=(2 ** segLen - 1), bitlen=global_bitlen, scale=global_scale)
    pack_0.rDCFkey, pack_1.rDCFkey = keygenCorrelatedDCF(x=ring, party=party, inverse=False,
                                                         sec_para=sec_para, local_transfer=False,
                                                         seed=seed)
    # Here we also call DPF on global bitlen rather than segLen because of the correlated setting.
    pack_0.rcDPFkey, pack_1.rcDPFkey = keygenCorrelatedConstantDPF(c=ring, party=party,
                                                                   bitlen=global_bitlen, scale=global_scale,
                                                                   sec_para=sec_para, local_transfer=False,
                                                                   seed=seed)
    if local_transfer:
        if filename is None:
            filename_0 = f'wrap&all1s_{segLen}_{global_bitlen}_{global_scale}_0.pack'
            filename_1 = f'wrap&all1s_{segLen}_{global_bitlen}_{global_scale}_1.pack'
            filename = [filename_0, filename_1]
        party.send(pack_0, filename[0])
        party.send(pack_1, filename[1])
        party.eliminate_start_marker('warp&all1s', 'offline')
        return filename
    else:
        party.eliminate_start_marker(func='warp&all1s', func_type='offline')
        return pack_0, pack_1


def wrap_and_all_1s(x: GroupElements, party: SemiHonestParty, offline_data: Union[str, wrap_and_all1s_pack],
                    sec_para=fss_config.sec_para):
    """
    This function evaluates warp and all 1s on x.
    :param sec_para:
    :param x: Group elements which value is the segmented value, while bitlen and scale is identical to global setting.
    :param party:
    :param offline_data:
    :return:
    """
    party.set_start_marker(func='warp&all1s', func_type='online')
    if type(offline_data) is str:
        offline_data: wrap_and_all1s_pack = party.local_recv(offline_data)
    w = evalCorrelatedDCF(party=party, x=x, key=offline_data.rDCFkey, sec_para=sec_para)
    e = evalCorrelatedConstantDPF(party=party, x=x, key=offline_data.rcDPFkey,
                                  return_Arithmetic=False, sec_para=sec_para)
    party.eliminate_start_marker(func='warp&all1s', func_type='online')
    return w * 10 + e


def digit_decomposition_offline(party: TrustedDealer, segLen: int,
                                global_bitlen=repr_config.bitlen, global_scale=repr_config.scalefactor,
                                sec_para=fss_config.sec_para, seed=fss_config.seed,
                                local_transfer=True, filename=None):
    """
    This function generates digit decomposition offline pack for parties.
    :param party:
    :param segLen:
    :param global_bitlen:
    :param global_scale:
    :param sec_para:
    :param seed:
    :param local_transfer:
    :param filename:
    :return:
    """
    assert (global_bitlen % segLen == 0), 'Currently we only support bitlen % segLen == 0'
    party.set_start_marker(func='digDec', func_type='offline')
    pack_0 = digit_decompose_pack()
    pack_1 = digit_decompose_pack()
    segNum = int(global_bitlen / segLen)

    # First, we generate wrap pack
    pack_0.wrap_and_all1s_pack, pack_1.wrap_and_all1s_pack = wrap_and_all_1s_offline(segLen=segLen,
                                                                                     party=party,
                                                                                     global_bitlen=global_bitlen,
                                                                                     global_scale=global_scale,
                                                                                     sec_para=sec_para,
                                                                                     seed=seed,
                                                                                     local_transfer=False)

    # Then we generate multiple AND pack.

    for i in range(segNum - 1):
        and_generated = boolean_and_offline(party=party,
                                            local_transfer=False,
                                            seed=seed)
        pack_0.boolean_AND_pack_list.append(and_generated[0])
        pack_1.boolean_AND_pack_list.append(and_generated[1])

        b2a_generated = generate_cross_term_triplet(bitlen=segLen, scale=global_scale,
                                                    local_transfer=False, executor=party, seed=seed)
        pack_0.B2A_triplet_list.append(b2a_generated[0])
        pack_1.B2A_triplet_list.append(b2a_generated[1])

    # Finally we store or send packs.
    if local_transfer:
        if filename is None:
            filename_0 = f'digDec_{segLen}_{global_bitlen}_{global_scale}_0.pack'
            filename_1 = f'digDec_{segLen}_{global_bitlen}_{global_scale}_1.pack'
            filename = [filename_0, filename_1]
        party.send(data=pack_0, name=filename[0])
        party.send(data=pack_1, name=filename[1])
        party.eliminate_start_marker('digDec', 'offline')
        return filename
    else:
        party.eliminate_start_marker(func='digDec', func_type='offline')
        return pack_0, pack_1


def digit_decomposition(x: GroupElements, segLen: int, party: SemiHonestParty,
                        offline_data: Union[str, digit_decompose_pack],
                        sec_para=fss_config.sec_para):
    """
    This function decomposes group elements into several parts.
    :param DEBUG:
    :param segLen:
    :param x:
    :param party:
    :param offline_data:
    :param sec_para:
    :return:
    """
    party.set_start_marker(func='digDec', func_type='online')
    if type(offline_data) is str:
        offline_data: digit_decompose_pack = party.local_recv(offline_data)
    segNum = int(x.bitlen / segLen)
    pre_segList = TriFSSTensor()
    segList = TriFSSTensor()

    # First, the parse the binary operation into several sectors.
    for i in range(segNum):
        pre_segList.add_elements(GroupElements(repr_value=((x.value >> (i * segLen)) & (2 ** segLen - 1)),
                                               bitlen=x.bitlen, scale=x.scalefactor, value=None))

    # Then we evaluate wrap and all 1s on 1 to segNum-1 sectors.
    wrap_and_all_1s_res = []
    for i in range(segNum - 1):
        wrap_and_all_1s_res.append(wrap_and_all_1s(x=pre_segList[i],
                                                   party=party,
                                                   offline_data=offline_data.wrap_and_all1s_pack,
                                                   sec_para=sec_para))

    # We manually set parameters for the first sector.
    segList.add_elements(clear_bits_removal(x=pre_segList[0], removal_number=(x.bitlen - segLen)))
    u = 0

    # Now run the second iteration
    for i in range(1, segNum):
        v = boolean_and(x=u, y=(wrap_and_all_1s_res[i - 1] % 10), party=party,
                        offline_data=offline_data.boolean_AND_pack_list[i - 1])
        u = v ^ int(wrap_and_all_1s_res[i - 1] / 10)
        arithmetic_u = B2A(x=u, triplet=offline_data.B2A_triplet_list[i - 1], party=party, bitlen=segLen)
        short_seg_val = clear_bits_removal(x=pre_segList[i], removal_number=(x.bitlen - segLen))
        segList.add_elements(short_seg_val + arithmetic_u)
    party.eliminate_start_marker(func='digDec', func_type='online')
    return segList
