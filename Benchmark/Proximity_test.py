from typing import List

from Pythonic_TriFSS.Cleartext.cleartext_functions import clear_sin, clear_cos
from Pythonic_TriFSS.Common.group_elements import GroupElements
from Pythonic_TriFSS.Utils.statistics import calculate_ulp_error
from math import sin, cos, pi
from Pythonic_TriFSS.Utils.construct_LUT import cos_val, cos_coefficients


def proximity_test(a: List, b: List):
    """
    This function returns ULP error of proximity test
    :param a: Not Group elements!
    :param b:
    :return:
    """
    a_ = []
    b_ = []
    a_.append(GroupElements(a[0]))
    a_.append(GroupElements(a[1]))
    b_.append(GroupElements(b[0]))
    b_.append(GroupElements(b[1]))
    front_operand = (a_[0] - b_[0]) * 0.5
    end_operand = (a_[1] - b_[1]) * 0.5
    front_ = clear_sin(front_operand)
    front_part = front_ * front_
    medium_part_0 = clear_cos(a_[0])
    medium_part_1 = clear_cos(b_[0])
    back_ = clear_sin(end_operand)
    back_part = back_ * back_
    all_back = medium_part_0 * medium_part_1 * back_part
    delta = front_part + all_back

    precise_res = sin(pi * (a[0] - b[0]) / 2) * sin(pi * (a[0] - b[0]) / 2) + \
                  cos(pi * a[0]) * cos(pi * b[0]) * sin(pi * (a[1] - b[1]) / 2) * sin(pi * (a[1] - b[1]) / 2)

    error = calculate_ulp_error(delta, precise_res)
    print(error)


if __name__ == '__main__':
    proximity_test([4.52, 2.78], [0.53, 8.44])
