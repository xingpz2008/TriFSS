import sys

sys.path.append('../..')
import time
from multiprocessing import Process
from Pythonic_TriFSS.Common.group_elements import GroupElements
from Pythonic_TriFSS.Communication.semi_honest_party import SemiHonestParty
import Pythonic_TriFSS.Configs.fixed_point_repr as repr_config
from Pythonic_TriFSS.Math.sine import sin
from Pythonic_TriFSS.Math.tangent import tan
import argparse
from math import ceil

fun_dict = {
    'sin': sin,
    'cos': sin,
    'tan': tan
}


def run_test(function, number, index, args):
    party = SemiHonestParty(party_id=args.role,
                            partner_addr='127.0.0.1',
                            partner_recv_port=((43 + args.role) * 1000 + index * 10),
                            recv_port=((44 - args.role) * 1000 + index * 10))
    for i in range(number):
        function(x=GroupElements(i), party=party)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Benchmarking with Multiprocess')
    parser.add_argument('-n', '--number', default=1000, type=int)
    parser.add_argument('-f', '--function', default='sin')
    parser.add_argument('-t', '--thread', default=2, type=int)
    parser.add_argument('-v', '--verbose', default=False, type=bool)
    parser.add_argument('-r', '--role', default=0, type=int)
    args = parser.parse_args()

    party_list = []
    process_list = []
    number_list = [ceil(args.number / args.thread)] * args.thread

    start = time.time()
    for i in range(args.thread):
        p = Process(target=run_test, args=(fun_dict[args.function], number_list[i], i, args))
        p.start()
        process_list.append(p)
    for process in process_list:
        process.join()
    end = time.time()
    print(f'Benchmarking Result: {end - start}s in {args.number} operations')
