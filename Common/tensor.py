from Pythonic_TriFSS.Common.group_elements import GroupElements


# TODO: Consider Optimize Tensor Operation
# TODO: Add Elementwise Addition

class TriFSSTensor(object):
    def __init__(self, val_list=[]):
        # self.real_tensor = np.array([1, length])
        self.val_list = val_list
        if not val_list:
            self.__length = 0
        else:
            self.__length = len(val_list)

    def __mul__(self, other):
        assert (type(other) in [TriFSSTensor, int, float, GroupElements]), 'Unsupported type for tensor multiplication.'
        new_tensor = TriFSSTensor()
        for i in range(self.__length):
            if type(other) == TriFSSTensor:
                assert (self.__length == other.__get_len__()), 'Only the same length can be applied when tensor * ' \
                                                               'tensor '
                this_value = self.val_list[i] * other.val_list[i]
            else:
                this_value = self.val_list[i] * other
            new_tensor.add_elements(this_value)
        return new_tensor

    def add_elements(self, x):
        assert (type(x) in [int, float, GroupElements]), 'Invalid data type'
        if self.val_list:
            assert (isinstance(x, type(self.val_list[0]))), "Invalid data type"
        self.val_list.append(x)
        self.__length += 1

    def __add__(self, other):
        """
        This build-in class method is the concat one, do not confused with elementwise addition!
        :param other: 
        :return:
        """
        assert (type(other) == TriFSSTensor), '+ operation can only be applied to TriFSSTensor'
        return TriFSSTensor(self.val_list+other.val_list)

    def __get_len__(self):
        return self.__length
