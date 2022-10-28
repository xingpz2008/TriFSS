"""
This script defines group elements.
"""

import Pythonic_TriFSS.Configs.fixed_point_repr as config


class GroupElements(object):
    # TODO: Consider if the implementation of Binary Operations for Group Element is proper.
    def __init__(self, value, bitlen=config.bitlen, scale=config.scalefactor, repr_value=None, DEBUG=config.DEBUG):
        assert (bitlen >= 1), "Improper bit length or scale"
        assert (scale >= 0), "Improper scale"
        if scale > bitlen:
            print('[WARNING] You are using GroupElements whose scale is bigger than bit-length. '
                  'It is allowed as an experimental feature, but may cause unexpected result.'
                  '\n[Hint] Checking if both signed and unsigned data are implemented correctly.')
        self.bitlen = bitlen
        self.scalefactor = scale
        if repr_value is None:
            self.value = (int(value * (2 ** self.scalefactor)) + 2 ** self.bitlen) % (2 ** self.bitlen)
        else:
            self.value = repr_value
        self.__init_real_value = 0
        self.__binary__repr = None
        self.__DEBUG = DEBUG
        # self.real_value can not be used in calculation, it is debug only.
        if DEBUG:
            self.__update__real_value__()
            self.__update_binary_repr__()

    def __add__(self, other):
        if type(other) is GroupElements:
            assert ((other.bitlen == self.bitlen) and (other.scalefactor == self.scalefactor)), "Add can only be " \
                                                                                                "applied in the same " \
                                                                                                "bit length and scale" \
                                                                                                "factor "
            value = (self.value + other.value) % (2 ** self.bitlen)
            return GroupElements(value=None, bitlen=self.bitlen, scale=self.scalefactor,
                                 repr_value=value, DEBUG=self.__DEBUG)
        if (type(other) is int) or (type(other) is float):
            new_other = GroupElements(other, self.bitlen, self.scalefactor)
            return self.__add__(new_other)
        else:
            raise NotImplementedError("Not supported at this data type")

    def __sub__(self, other):
        if type(other) is GroupElements:
            assert ((other.bitlen == self.bitlen) and (other.scalefactor == self.scalefactor)), "Sub can only be " \
                                                                                                "applied in the same " \
                                                                                                "bit length and " \
                                                                                                "scale factor "
            value = (self.value - other.value) % (2 ** self.bitlen)
            return GroupElements(value=None, bitlen=self.bitlen, scale=self.scalefactor,
                                 repr_value=value, DEBUG=self.__DEBUG)
        if (type(other) is int) or (type(other) is float):
            new_other = GroupElements(other, self.bitlen, self.scalefactor)
            return self.__sub__(new_other)
        else:
            raise NotImplementedError("Not supported at this data type")

    def __mul__(self, other):
        # Note, this might loss precision, should be invoked with cautious
        if type(other) is GroupElements:
            assert ((other.bitlen == self.bitlen) and (other.scalefactor == self.scalefactor)), "Mul can only be " \
                                                                                                "applied in the same " \
                                                                                                "bit length and " \
                                                                                                "scale factor "
            if self[self.bitlen - 1] == 1:
                extended_self = self.value + ((2 ** self.bitlen - 1) << self.bitlen)
            else:
                extended_self = self.value
            if other[other.bitlen - 1] == 1:
                extended_other = other.value + ((2 ** other.bitlen - 1) << other.bitlen)
            else:
                extended_other = other.value
            value = ((extended_self * extended_other) >> self.scalefactor) % (2 ** self.bitlen)
            return GroupElements(value=None, bitlen=self.bitlen, scale=self.scalefactor,
                                 repr_value=value, DEBUG=self.__DEBUG)
        if (type(other) is int) or (type(other) is float):
            new_other = GroupElements(other, self.bitlen, self.scalefactor)
            return self.__mul__(new_other)
        else:
            raise NotImplementedError("Not supported at this data type")

    def __gt__(self, other):
        assert (type(other) in [GroupElements, int, float]), "Unsupported data type for comparison."
        if type(other) is GroupElements:
            assert ((other.bitlen == self.bitlen) and (other.scalefactor == self.scalefactor)), "Comparison can only " \
                                                                                                "be applied when in " \
                                                                                                "the same parameters "
            self.__update__real_value__()
            other.__update__real_value__()
            return self.__init_real_value > other.__init_real_value
        else:
            new_other = GroupElements(other, self.bitlen, self.scalefactor)
            return self.__gt__(new_other)

    def __lt__(self, other):
        assert (type(other) in [GroupElements, int, float]), "Unsupported data type for comparison."
        if type(other) is GroupElements:
            assert ((other.bitlen == self.bitlen) and (other.scalefactor == self.scalefactor)), "Comparison can only " \
                                                                                                "be applied when in " \
                                                                                                "the same parameters "
            self.__update__real_value__()
            other.__update__real_value__()
            return self.__init_real_value < other.__init_real_value
        else:
            new_other = GroupElements(other, self.bitlen, self.scalefactor)
            return self.__lt__(new_other)

    def __getitem__(self, item):
        assert (self.bitlen >= item >= 0), f"No index at {item}"
        return self.value >> item & 1

    def __update__real_value__(self):
        self.__init_real_value = (float(self.value)) / (2 ** self.scalefactor)  # This is for debug only
        if self.value > 2 ** (self.bitlen - 1):
            self.__init_real_value = float(self.value - 2 ** self.bitlen) / (2 ** self.scalefactor)

    def __update_binary_repr__(self):
        binary_string = ''
        for i in range(self.bitlen):
            binary_string = binary_string + str(self.__getitem__(i))
            if i == self.scalefactor - 1:
                binary_string += '.'
        self.__binary__repr = binary_string[::-1]

    def __get_binary_repr__(self):
        return self.__binary__repr
