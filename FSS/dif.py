from Pythonic_TriFSS.FSS.dcf import evalDCF, keygenDCF, keygenCorrelatedDCF, evalCorrelatedDCF
from Pythonic_TriFSS.Common.group_elements import GroupElements
import Pythonic_TriFSS.Configs.fss as config
from Pythonic_TriFSS.FSS.dataClass.function_key import DIFKey, Correlated_DIFKey
from Pythonic_TriFSS.Communication.dealer import TrustedDealer
from Pythonic_TriFSS.Communication.semi_honest_party import SemiHonestParty


def keygenDIF(interval: (GroupElements, GroupElements), party: TrustedDealer, filename=None, sec_para=config.sec_para,
              local_transfer=True, DEBUG=config.DEBUG) -> [DIFKey, DIFKey]:
    """
    This function generates DIF for if input in (interval), return 1, else 0.
    The insight is that, if there is no wrap around, we can use evalDCF1 ^ evalDCF2
    If there is a wrap around, we can use inverse to accomplish it.
    If x0 < 0 and x1 > 0, key for interval 0 (the negative one) should inverse
    ----@@@@-x1-----0-----x0--@@@@--- for fixed-arithmetic
    TODO: Consider Payload
    :param local_transfer:
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
    if local_transfer:
        if filename is None:
            filename_0 = f'DIF_{x.bitlen}_{x.scalefactor}_0.key'
            filename_1 = f'DIF_{x.bitlen}_{x.scalefactor}_1.key'
            filename = [filename_0, filename_1]
        party.send(k0, filename[0])
        party.send(k1, filename[1])
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


def keygenCorrelatedDIF(interval: (GroupElements, GroupElements), party: TrustedDealer, filename=None,
                        sec_para=config.sec_para, unsigned=False,
                        local_transfer=True, DEBUG=config.DEBUG):
    """
    This function returns the correlated DIF key for the target interval
    :param unsigned:
    :param interval:
    :param party:
    :param filename:
    :param sec_para:
    :param local_transfer:
    :param DEBUG:
    :return:
    """
    # TODO: Check Inverse, we need unsigned here for non-inverse comparison
    if not unsigned:
        assert (interval[1] > interval[0]), 'Invalid Interval Sequence'
    inverse = False if unsigned else None
    party.set_start_marker('keygenCorrelatedDIF', 'offline')
    k0 = Correlated_DIFKey()
    k1 = Correlated_DIFKey()
    k0.interval_0_key, k1.interval_0_key = keygenCorrelatedDCF(x=interval[0], party=party, sec_para=sec_para,
                                                               inverse=inverse,
                                                               local_transfer=False, DEBUG=DEBUG)
    k0.interval_1_key, k1.interval_1_key = keygenCorrelatedDCF(x=interval[1], party=party, local_transfer=False,
                                                               inverse=inverse,
                                                               sec_para=sec_para, DEBUG=DEBUG)
    if local_transfer:
        if filename is None:
            filename_0 = f'rDIF_{interval[0].bitlen}_{interval[0].scalefactor}_0.key'
            filename_1 = f'rDIF_{interval[1].bitlen}_{interval[1].scalefactor}_1.key'
            filename = [filename_0, filename_1]
        party.send(k0, filename[0])
        party.send(k1, filename[1])
    party.eliminate_start_marker('keygenCorrelatedDIF', 'offline')
    return k0, k1


def evalCorrelatedDIF(party: SemiHonestParty, x: GroupElements,
                      key: Correlated_DIFKey = None, filename=None,
                      sec_para=config.sec_para, DEBUG=config.DEBUG):
    """
    This function evaluates coorrelated DIF
    :param party:
    :param x:
    :param key:
    :param filename:
    :param sec_para:
    :param DEBUG:
    :return:
    """
    party.set_start_marker(func='evalCorrelatedDIF')
    if filename is None:
        assert (key is not None), "We need at least key or keyfile to continue."
    else:
        key = party.local_recv(filename=filename)
    # We first evaluate the first result
    interval_0_result = evalCorrelatedDCF(party=party, x=x, key=key.interval_0_key,
                                          filename=None, sec_para=sec_para, DEBUG=DEBUG)
    # Then we evaluate the next result
    interval_1_result = evalCorrelatedDCF(party=party, x=x, key=key.interval_1_key,
                                          filename=None, sec_para=sec_para, DEBUG=DEBUG)
    result = interval_0_result ^ interval_1_result
    if DEBUG:
        print(f'==========DEBUG INFO for Party {party.party_id}==========')
        print(f'Interval 0 Res = {interval_0_result}')
        print(f'Interval 1 Res = {interval_1_result}')
    party.eliminate_start_marker('evalCorrelatedDIF')
    return result
