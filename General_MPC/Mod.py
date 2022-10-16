from Pythonic_TriFSS.Common.group_elements import GroupElements
from Pythonic_TriFSS.Communication.semi_honest_party import SemiHonestParty
import Pythonic_TriFSS.Configs.fixed_point_repr as repr_config
import Pythonic_TriFSS.Configs.fss as fss_config
import Pythonic_TriFSS.Configs.general_mpc as config
from Pythonic_TriFSS.General_MPC.dataClass.protocol_offline_pack import Mod_pack
from Pythonic_TriFSS.Communication.dealer import TrustedDealer
from Pythonic_TriFSS.General_MPC.B2A import generate_cross_term_triplet
from Pythonic_TriFSS.FSS.dcf import keygenCorrelatedDCF, evalCorrelatedDCF
from Pythonic_TriFSS.General_MPC.B2A import B2A


def Mod_offline(party: TrustedDealer, N, unsigned=False,
                bitlen=repr_config.bitlen, scale=repr_config.scalefactor, filename=None,
                sec_para=fss_config.sec_para, local_transfer=True, seed=fss_config.seed, DEBUG=config.DEBUG):
    """
    This function generates Mod_offline_pack
    :param unsigned:
    :param filename:
    :param seed:
    :param sec_para:
    :param DEBUG:
    :param N:
    :param bitlen:
    :param scale:
    :param party:
    :param local_transfer:
    :return:
    """
    assert (type(N) in [GroupElements, int]), 'Invalid data type for N.'
    if type(N) == int:
        N = GroupElements(value=N, bitlen=bitlen, scale=scale)
    assert (N > 0), 'Mod operation can only be applied to N>0'
    party.set_start_marker("Mod_offline", 'offline')
    pack_0 = Mod_pack()
    pack_1 = Mod_pack()
    pack_0.triplet, pack_1.triplet = generate_cross_term_triplet(bitlen=bitlen, scale=scale, local_transfer=False,
                                                                 executor=party, seed=seed)

    pack_0.rDCFkey, pack_1.rDCFkey = keygenCorrelatedDCF(x=N, party=party, inverse=(not unsigned), sec_para=sec_para,
                                                         local_transfer=False, seed=seed, DEBUG=DEBUG)
    if local_transfer:
        if filename is None:
            filename_0 = f'Mod_{N.bitlen}_{N.scalefactor}_0.pack'
            filename_1 = f'Mod_{N.bitlen}_{N.scalefactor}_1.pack'
            filename = [filename_0, filename_1]
        party.send(pack_0, filename[0])
        party.send(pack_1, filename[1])
        party.eliminate_start_marker("Mod_offline", 'offline')
        return filename
    else:
        party.eliminate_start_marker("Mod_offline", 'offline')
        return pack_0, pack_1


def Mod(party: SemiHonestParty, x: GroupElements, N: GroupElements, offline_pack_file: str,
        sec_para=fss_config.sec_para, DEBUG=config.DEBUG):
    """
    This function executes the Mod protocol at online stage. (fixed bitwidth)
    This mod is strictly restricted as it can only turn [0,2N] -> [0,N]
    :param sec_para:
    :param offline_pack_file:
    :param party:
    :param x:
    :param N:
    :param DEBUG:
    :return: Shares of x mod N
    """
    party.set_start_marker(func='Mod')
    # We first read data from file
    offline_data: Mod_pack = party.local_recv(offline_pack_file)
    share_of_x_plus_r = x + offline_data.rDCFkey.r
    party.send(share_of_x_plus_r)
    recv: GroupElements = party.recv()
    reconstructed_x = recv + share_of_x_plus_r
    # We calculate z
    z = evalCorrelatedDCF(party=party, x=reconstructed_x, key=offline_data.rDCFkey, DEBUG=DEBUG, sec_para=sec_para)
    z = z ^ party.party_id
    # Then we transform it to Arithmetic shares
    z_a = B2A(x=z, triplet=offline_data.triplet, party=party, bitlen=x.bitlen, scale=x.scalefactor, DEBUG=DEBUG)
    y = x - (N * z_a)
    if DEBUG:
        print(f'==========DEBUG INFO FOR PARTY {party.party_id} @ MOD==========')
        print(f'Local x+r = {share_of_x_plus_r._GroupElements__init_real_value}')
        print(f'Reconstructed x = {reconstructed_x._GroupElements__init_real_value}')
        print(f'z = {z}')
        print(f'z_a = {z_a._GroupElements__init_real_value}')
        print(f'y = {y._GroupElements__init_real_value}')
        print('==========DEBUG END==========')
    party.eliminate_start_marker(func='Mod')
    return y
