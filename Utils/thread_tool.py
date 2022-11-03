from math import ceil


def get_loc_list(fullNum, threadNum):
    """
    This function returns the segmentation of multi thread task
    :param fullNum:
    :param threadNum:
    :return:
    """
    if (threadNum == 0) or (threadNum == 1):
        return [fullNum]
    loc_list = []
    segment = ceil(fullNum / threadNum)
    pointer = 0
    while (pointer + segment) < fullNum:
        pointer += segment
        loc_list.append(pointer)
    if fullNum not in loc_list:
        loc_list.append(fullNum)
    return loc_list
