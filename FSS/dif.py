from Pythonic_TriFSS.FSS.dcf import evalDCF, keygenDCF
from Pythonic_TriFSS.Common.group_elements import GroupElements
import Pythonic_TriFSS.Configs.fss as config
from Pythonic_TriFSS.FSS.dataClass.function_key import DIFKey
from Pythonic_TriFSS.Communication.dealer import TrustedDealer
from Pythonic_TriFSS.Communication.semi_honest_party import SemiHonestParty


def keygenDIF(interval: (GroupElements, GroupElements), party: TrustedDealer, filename=None, sec_para=config.sec_para,
              DEBUG=config.DEBUG) -> [DIFKey, DIFKey]:
    """
    This function generates DIF for if input in (interval), return 1, else 0.
    The insight is that, if there is no wrap around, we can use evalDCF1 ^ evalDCF2
    If there is a wrap around, we can use inverse to accomplish it.
    If x0 < 0 and x1 > 0, key for interval 0 (the negative one) should inverse
    ----@@@@-x1-----0-----x0--@@@@--- for fixed-arithmetic
    TODO: Consider Payload
    :param interval:
    :param party:
    :param filename:
    :param sec_para:
    :param DEBUG:
    :return:
    """
    # We first confirm the +/- of our interval
    assert (interval[1] > interval[0]), 'Invalid Interval Sequence'
    inverse = ((interval[0] < 0) and (interval[1] > 0))
    party.set_start_marker('keygenDIF', 'offline')
    k0 = DIFKey()
    k1 = DIFKey()
    k0.interval_0_key, k1.interval_0_key = keygenDCF(x=interval[0], party=party, inverse=inverse, sec_para=sec_para,
                                                     local_transfer=False, DEBUG=DEBUG)
    k0.interval_1_key, k1.interval_1_key = keygenDCF(x=interval[1], party=party, local_transfer=False,
                                                     sec_para=sec_para, DEBUG=DEBUG)
    party.send(k0, filename)
    party.send(k1, filename)
    party.eliminate_start_marker('keygenDIF', 'offline')
    return k0, k1


def evalDIF(party: SemiHonestParty, x: GroupElements, key: DIFKey = None, filename=None,
            sec_para=config.sec_para, DEBUG=config.DEBUG):
    """
    This function returns the value of DIF for if input in (interval), return 1 else 0.
    :param party:
    :param x:
    :param key:
    :param filename:
    :param sec_para:
    :param DEBUG:
    :return:
    """
    party.set_start_marker(func='evalDIF')
    if filename is None:
        assert (key is not None), "We need at least key or keyfile to continue."
    else:
        key = party.local_recv(filename=filename)
    # We first evaluate the first result
    interval_0_result = evalDCF(party=party, x=x, key=key.interval_0_key, filename=None, sec_para=sec_para, DEBUG=DEBUG)
    # Then we evaluate the next result
    interval_1_result = evalDCF(party=party, x=x, key=key.interval_1_key, filename=None, sec_para=sec_para, DEBUG=DEBUG)
    result = interval_0_result ^ interval_1_result
    if DEBUG:
        print(f'==========DEBUG INFO for Party {party.party_id}==========')
        print(f'Interval 0 Res = {interval_0_result}')
        print(f'Interval 1 Res = {interval_1_result}')
    party.eliminate_start_marker('evalDIF')
    return result
