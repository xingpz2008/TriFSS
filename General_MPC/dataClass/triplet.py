from Pythonic_TriFSS.Common.group_elements import GroupElements


class CrossTermTriplets(object):
    def __init__(self, a: GroupElements, ab_b: GroupElements):
        self.a = a
        self.ab_b = ab_b


class BeaverTriplets(object):
    def __init__(self, a: GroupElements, b: GroupElements, ab_b: GroupElements):
        self.a = a
        self.b = b
        self.ab_b = ab_b


class BooleanMultTriplets(object):
    def __init__(self, a: int, b: int, ab_b: int):
        self.a = a
        self.b = b
        self.ab_b = ab_b
