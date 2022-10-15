from Pythonic_TriFSS.Common.group_elements import GroupElements
import Pythonic_TriFSS.Common.tensor as Tensor


class LookUpTable(Tensor.TriFSSTensor):
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
