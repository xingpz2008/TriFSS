# TODO: Add containment gate
from Pythonic_TriFSS.Communication.dealer import TrustedDealer
from Pythonic_TriFSS.Communication.semi_honest_party import SemiHonestParty
from Pythonic_TriFSS.Common.tensor import TriFSSTensor
import Pythonic_TriFSS.Configs.fss as fss_config


def Containment_Offline(party: TrustedDealer, knots_list: TriFSSTensor, filename=None, sec_para=fss_config.sec_para,
                        local_transfer=True, DEBUG=fss_config.DEBUG):
    """
    This function Generates key pack for containment gate. The insight is that, we can invoke multiple instances of DIF
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
    for i in range(length-1):
        # Here we invoke length-1 instances of DIF
        interval = (knots_list.val_list[i], knots_list.val_list[i+1])