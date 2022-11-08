from Pythonic_TriFSS.Cleartext.cleartext_lib import clear_bits_removal, clear_mod
from Pythonic_TriFSS.Configs.fixed_point_repr import scalefactor, bitlen
from Pythonic_TriFSS.Utils.random_sample import sampleGroupElements

# Here we check correctness when reflecting value into [0,2]
test_case = 3

# Test case1: original=positive, share1=positive, share2=positive
if test_case == 1:
    x_0_0 = sampleGroupElements(lower_bound=0)
    x_0_1 = sampleGroupElements(lower_bound=0)
    x_0 = x_0_1 + x_0_0

    moded_x_0 = clear_mod(clear_bits_removal(x_0, (bitlen-(2+scalefactor))), 2, True)
    _x_0_0 = clear_bits_removal(x_0_0, (bitlen-(2+scalefactor)))
    _x_0_1 = clear_bits_removal(x_0_1, (bitlen-(2+scalefactor)))
    _x_0 = _x_0_0 + _x_0_1
    _moded_x_0 = clear_mod(_x_0, 2)

# Test case2: original=positive, share1=positive, share2=negative
elif test_case == 2:
    x_0_0 = sampleGroupElements(lower_bound=0)
    x_0_1 = sampleGroupElements(upper_bound=0)
    x_0 = x_0_1 + x_0_0

    moded_x_0 = clear_mod(clear_bits_removal(x_0, (bitlen-(2+scalefactor))), 2, True)
    _x_0_0 = clear_bits_removal(x_0_0, (bitlen-(2+scalefactor)))
    _x_0_1 = clear_bits_removal(x_0_1, (bitlen-(2+scalefactor)))
    _x_0 = _x_0_0 + _x_0_1
    _moded_x_0 = clear_mod(_x_0, 2)

# Test case3: original=negative, share1=negative, share2=negative
elif test_case == 3:
    x_0 = sampleGroupElements(upper_bound=0)
    x_0_0 = sampleGroupElements(upper_bound=0)
    x_0_1 = x_0 - x_0_0

    moded_x_0 = clear_mod(clear_bits_removal(x_0, (bitlen-(2+scalefactor))), 2, True)
    _x_0_0 = clear_bits_removal(x_0_0, (bitlen-(2+scalefactor)))
    _x_0_1 = clear_bits_removal(x_0_1, (bitlen-(2+scalefactor)))
    _x_0 = _x_0_0 + _x_0_1
    _moded_x_0 = clear_mod(_x_0, 2, True)
    pass
