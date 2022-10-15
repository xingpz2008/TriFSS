from Pythonic_TriFSS.Communication.dealer import TrustedDealer
from Pythonic_TriFSS.Communication.semi_honest_party import SemiHonestParty
from Pythonic_TriFSS.Common.tensor import TriFSSTensor
import Pythonic_TriFSS.Configs.fss as fss_config
from Pythonic_TriFSS.General_MPC.dataClass.protocol_offline_pack import Containment_pack
from Pythonic_TriFSS.FSS.dif import keygenCorrelatedDIF, evalCorrelatedDIF
from Pythonic_TriFSS.Common.group_elements import GroupElements


def Containment_Offline(party: TrustedDealer, knots_list: TriFSSTensor, filename=None, sec_para=fss_config.sec_para,
                        unsigned=False, local_transfer=True, DEBUG=fss_config.DEBUG):
    """
    This function Generates key pack for containment gate. The insight is that, we can invoke multiple instances of DIF
    :param unsigned:
    :param party:
    :param knots_list: We assume that this sequence is in order from smaller elements to bigger one.
    :param filename:
    :param sec_para:
    :param local_transfer:
    :param DEBUG:
    :return:
    """
    party.set_start_marker('Containment', 'offline')
    length = knots_list.__get_len__()
    pack_0 = Containment_pack()
    pack_1 = Containment_pack()
    for i in range(length - 1):
        # Here we invoke length-1 instances of CorrDIF
        interval = (knots_list.val_list[i], knots_list.val_list[i + 1])
        key_0, key_1 = keygenCorrelatedDIF(interval=interval, party=party, sec_para=sec_para, unsigned=unsigned,
                                           local_transfer=False, DEBUG=DEBUG)
        pack_0.add_key(key_0)
        pack_1.add_key(key_1)
    if local_transfer:
        if filename is None:
            filename_0 = f'Ctn_{knots_list.val_list[0].bitlen}_{knots_list.val_list[1].scalefactor}_0.pack'
            filename_1 = f'Ctn_{knots_list.val_list[0].bitlen}_{knots_list.val_list[1].scalefactor}_1.pack'
            filename = [filename_0, filename_1]
        party.send(pack_0, filename[0])
        party.send(pack_1, filename[1])
        return filename
    party.eliminate_start_marker('Containment', 'offline')
    return pack_0, pack_1


def Containment(party: SemiHonestParty, x: GroupElements,
                offline_pack_file: str, sec_para=fss_config.sec_para, DEBUG=fss_config.DEBUG):
    """
    This function evaluates containment using correlated DIF instances.
    :param party:
    :param x:
    :param offline_pack_file:
    :param sec_para:
    :param DEBUG:
    :return: TriFSSTensor that contains boolean shares of containment of i-th interval at index [i]
    """
    party.set_start_marker('Containment')
    offline_data: Containment_pack = party.local_recv(offline_pack_file)
    result_tensor = []
    for i in range(offline_data.len):
        # Here we start to evaluate intervals
        index_result = evalCorrelatedDIF(party=party, x=x, key=offline_data.key_list[i], sec_para=sec_para, DEBUG=DEBUG)
        result_tensor.append(index_result)
    party.eliminate_start_marker('Containment')
    return result_tensor
