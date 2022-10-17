from typing import Union

from Pythonic_TriFSS.Common.group_elements import GroupElements
import Pythonic_TriFSS.Configs.general_mpc as mpc_config
from Pythonic_TriFSS.Utils.thread_tool import get_loc_list
from Pythonic_TriFSS.Communication.dataClass.thread import TriFSSThread


# TODO: Consider Optimize Tensor Operation

class TriFSSTensor(object):
    def __init__(self, val_list=[], party=None):
        # self.real_tensor = np.array([1, length])
        if val_list != []:
            self.val_list = val_list
        else:
            self.val_list = []
        if not val_list:
            self.__length = 0
        else:
            self.__length = len(val_list)
        self.party = party
        if self.party is not None:
            self.thread = mpc_config.default_thread
        else:
            self.thread = 1

    def __mul__(self, other):
        assert (type(other) in [TriFSSTensor, int, float, GroupElements, LookUpTable]), 'Unsupported type for tensor ' \
                                                                                        'multiplication. '
        new_tensor = TriFSSTensor()
        if self.thread > 1:
            if type(other) in [TriFSSTensor, LookUpTable]:
                new_tensor = self.__elementwise_mul_with_thread(other)
            elif type(other) in [int, float]:
                new_other = TriFSSTensor([GroupElements(value=other,
                                                        bitlen=self.val_list[0].bitlen,
                                                        scale=self.val_list[0].scalefactor)] * self.__length)
                new_tensor = self.__elementwise_mul_with_thread(new_other)
            else:
                new_other = TriFSSTensor([other] * self.__length)
                new_tensor = self.__elementwise_mul_with_thread(new_other)
        else:
            for i in range(self.__length):
                if type(other) in [TriFSSTensor, LookUpTable]:
                    assert (self.__length == other.__get_len__()), 'Only the same length can be applied when ' \
                                                                   'tensor * ' \
                                                                   'tensor '
                    this_value = self.val_list[i] * other.val_list[i]
                else:
                    this_value = self.val_list[i] * other
                new_tensor.add_elements(this_value)
        return new_tensor

    def __sub__(self, other):
        assert (type(other) in [TriFSSTensor, int, float, GroupElements, LookUpTable]), \
            'Unsupported type for tensor subtraction.'
        new_tensor = TriFSSTensor()
        if self.thread > 1:
            if type(other) in [TriFSSTensor, LookUpTable]:
                new_tensor = self.__elementwise_sub_with_thread(other)
            elif type(other) in [int, float]:
                new_other = TriFSSTensor([GroupElements(value=other,
                                                        bitlen=self.val_list[0].bitlen,
                                                        scale=self.val_list[0].scalefactor)] * self.__length)
                new_tensor = self.__elementwise_sub_with_thread(new_other)
            else:
                new_other = TriFSSTensor([other] * self.__length)
                new_tensor = self.__elementwise_sub_with_thread(new_other)
        else:
            for i in range(self.__length):
                if type(other) == TriFSSTensor:
                    assert (self.__length == other.__get_len__()), 'Only the same length can be applied when ' \
                                                                   'tensor * ' \
                                                                   'tensor '
                    this_value = self.val_list[i] - other.val_list[i]
                else:
                    this_value = self.val_list[i] - other
                new_tensor.add_elements(this_value)
        return new_tensor

    def add_elements(self, x):
        assert (type(x) in [int, float, GroupElements, dict]), 'Invalid data type'
        if self.val_list:
            assert (isinstance(x, type(self.val_list[0]))), "Invalid data type"
        self.val_list.append(x)
        self.__length += 1

    def concat(self, other):
        """
        This is the new function on concat. We use __add__ as the elementwise-addition.
        :param other:
        :return:
        """
        assert (type(other) == TriFSSTensor), '+ operation can only be applied to TriFSSTensor'
        return TriFSSTensor(self.val_list + other.val_list)

    def __add__(self, other):
        assert (type(other) in [TriFSSTensor, int, float, GroupElements, LookUpTable]), \
            'Unsupported type for tensor addition.'
        new_tensor = TriFSSTensor()
        if self.thread > 1:
            if type(other) in [TriFSSTensor, LookUpTable]:
                new_tensor = self.__elementwise_add_with_thread(other)
            elif type(other) in [int, float]:
                new_other = TriFSSTensor([GroupElements(value=other,
                                                        bitlen=self.val_list[0].bitlen,
                                                        scale=self.val_list[0].scalefactor)] * self.__length)
                new_tensor = self.__elementwise_add_with_thread(new_other)
            else:
                new_other = TriFSSTensor([other] * self.__length)
                new_tensor = self.__elementwise_add_with_thread(new_other)
        else:
            for i in range(self.__length):
                if type(other) == TriFSSTensor:
                    assert (self.__length == other.__get_len__()), 'Only the same length can be applied when ' \
                                                                   'tensor * ' \
                                                                   'tensor '
                    this_value = self.val_list[i] + other.val_list[i]
                else:
                    this_value = self.val_list[i] + other
                new_tensor.add_elements(this_value)
        return new_tensor

    def get_all_added(self) -> GroupElements:
        """
        This function add all values in the index together.
        :return: GroupElements
        """
        result = GroupElements(value=0, bitlen=self.val_list[0].bitlen, scale=self.val_list[0].scalefactor)
        if self.thread > 1:
            result_vector = []
            segmentation = [0] + get_loc_list(fullNum=self.__length, threadNum=self.thread)

            def __thread_add_all(interval: [int, int], include_right=False):
                _result = GroupElements(value=0, bitlen=self.val_list[0].bitlen, scale=self.val_list[0].scalefactor)
                for j in range(interval[0], interval[1] + int(include_right)):
                    _result = _result + self.val_list[j]
                result_vector.append(_result)

            for i in range(self.thread):
                new_thread = TriFSSThread(func=__thread_add_all, args=[[segmentation[i], segmentation[i + 1]],
                                                                       False])
                self.party.add_thread(new_thread)
            self.party.start_all_thread()
            for i in range(len(result_vector)):
                result = result + result_vector[i]
        else:
            for i in range(self.__length):
                result = result + self.val_list[i]
        return result

    def __getitem__(self, item):
        return self.val_list[item]

    def __setitem__(self, key, value):
        self.val_list[key] = value

    def __get_len__(self):
        return self.__length

    def __elementwise_mul_with_thread(self, other):
        """
        We assume that the two operands are of the same length
        :param other:
        :return:
        """
        assert (self.thread > 1), 'Please set thread num > 1 in ~/Configs/general_mpc.py'
        assert (self.__length == other.__length), 'Only the tensor with identical length can be multiplied elementwise'
        segmentation = [0] + get_loc_list(fullNum=self.__length, threadNum=self.thread)
        result_tensor = TriFSSTensor([None] * self.__length, party=self.party)

        def __range__mult(interval: [int, int], include_right=False):
            for j in range(interval[0], interval[1] + int(include_right)):
                result_tensor[j] = self[j] * other[j]

        if (len(segmentation) - 1) < self.thread:
            real_thread = len(segmentation) - 1
        else:
            real_thread = self.thread
        for i in range(real_thread):
            new_thread = TriFSSThread(func=__range__mult, args=[[segmentation[i], segmentation[i + 1]],
                                                                False])
            self.party.add_thread(new_thread)
        self.party.start_all_thread()
        self.party.empty_thread_pool()
        return result_tensor

    def __elementwise_add_with_thread(self, other):
        assert (self.thread > 1), 'Please set thread num > 1 in ~/Configs/general_mpc.py'
        assert (self.__length == other.__length), 'Only the tensor with identical length can be multiplied elementwise'
        segmentation = [0] + get_loc_list(fullNum=self.__length, threadNum=self.thread)
        result_tensor = TriFSSTensor([None] * self.__length, party=self.party)

        def __range__add(interval: [int, int], include_right=False):
            for j in range(interval[0], interval[1] + int(include_right)):
                result_tensor[j] = self[j] + other[j]

        if (len(segmentation) - 1) < self.thread:
            real_thread = len(segmentation) - 1
        else:
            real_thread = self.thread
        for i in range(real_thread):
            new_thread = TriFSSThread(func=__range__add, args=[[segmentation[i], segmentation[i + 1]],
                                                               False])
            self.party.add_thread(new_thread)
        self.party.start_all_thread()
        self.party.empty_thread_pool()
        return result_tensor

    def __elementwise_sub_with_thread(self, other):
        assert (self.thread > 1), 'Please set thread num > 1 in ~/Configs/general_mpc.py'
        assert (self.__length == other.__length), 'Only the tensor with identical length can be subtracted elementwise'
        segmentation = [0] + get_loc_list(fullNum=self.__length, threadNum=self.thread)
        result_tensor = TriFSSTensor([None] * self.__length, party=self.party)

        def __range__sub(interval: [int, int], include_right=False):
            for j in range(interval[0], interval[1] + int(include_right)):
                result_tensor[j] = self[j] - other[j]

        if (len(segmentation) - 1) < self.thread:
            real_thread = len(segmentation) - 1
        else:
            real_thread = self.thread
        for i in range(real_thread):
            new_thread = TriFSSThread(func=__range__sub, args=[[segmentation[i], segmentation[i + 1]],
                                                               False])
            self.party.add_thread(new_thread)
        self.party.start_all_thread()
        self.party.empty_thread_pool()
        return result_tensor

    def vector_left_shift(self, offset: Union[int, GroupElements]):
        if type(offset) is GroupElements:
            offset = offset.value
        new_tensor = TriFSSTensor([None] * self.__length)
        for i in range(self.__length):
            new_tensor[i] = self[(i + offset) % self.__length]
        return new_tensor

    def update_to_thread_tensor(self, party, thread=mpc_config.default_thread):
        self.party = party
        self.thread = thread

    def downgrade_to_non_thread_tensor(self):
        self.party = None
        self.thread = 1


class LookUpTable(TriFSSTensor):
    def __init__(self, var_list=[], key_list=[]):
        """
        Here we use tensor-like database implementation, as we do not care the key.
        """
        super().__init__(var_list)
        self.key_list = key_list

    def __getitem__(self, item: int):
        return self.val_list[item]

    def add_elements(self, x, k=None):
        super().add_elements(x)
        if k:
            self.key_list.append(k)

    def get_item_by_key(self, key):
        for key_, idx in enumerate(self.key_list):
            if key == key_:
                return self[idx]
        return None
