import random
from socket import *
import pickle
import Pythonic_TriFSS.Configs.communication as config
import time
from Pythonic_TriFSS.Utils.statistics import get_data_size
from Pythonic_TriFSS.Common.group_elements import GroupElements


def pack(data, protocol=config.protocol):
    """
    This function converts
    :param data:
    :param protocol:
    :return:
    """
    if protocol == 0:
        if type(data) is GroupElements:
            # This is bitlen and scale
            byte_data = b'GR'
            byte_data = byte_data + (data.bitlen * (10 ** 2) +
                                     data.scalefactor).to_bytes(2, 'big')
            b_repr = data.value.to_bytes(int(data.bitlen / 2), 'big')
            byte_data = byte_data + b_repr
            return byte_data
        else:
            return pickle.dumps(data)
    else:
        return pickle.dumps(data)


def unpack(data, protocol=config.protocol):
    """
    This function creates variable from data
    :param data:
    :param protocol:
    :return:
    """
    if protocol == 0:
        if data[:2] == b'GR':
            front = data[2:4]
            back = data[4:-1]
            int_front = int().from_bytes(front, 'big')
            bitlen = int(int_front / 100)
            scale = int_front % 100
            repr_value = int().from_bytes(back, 'big')
            return GroupElements(value=None, repr_value=repr_value, bitlen=bitlen, scale=scale)
        else:
            return pickle.loads(data)
    else:
        return pickle.loads(data)


def send(addr, port, data, LOG=config.LOG):
    s = socket(AF_INET, SOCK_STREAM)
    for i in range(config.MAX_Connection_Time):
        try:
            s.connect((addr, port))
        except ConnectionRefusedError as e:
            time.sleep(config.connection_interval_in_s)
            s.close()
            if i == config.MAX_Connection_Time - 1:
                raise Exception(f'[ERROR] Connection failed after {config.MAX_Connection_Time} times.')
            s = socket(AF_INET, SOCK_STREAM)
            if LOG:
                print(f"[WARNING] Re-try to connect {addr}:{port}")
            continue
        break
    if LOG:
        print(f"[INFO] Connection Established with {addr}:{port}")
    data = pack(data)
    s.sendall(data)
    if LOG:
        print(f"[INFO] Data Sent to {addr}:{port}")
    s.close()
    return get_data_size(data)


def _recv(buffer, comm):
    data = comm.recv(buffer)
    return data


def recv(s: socket, port, LOG=config.LOG):
    data = b''
    comm, addr = s.accept()
    while True:
        packet = _recv(config.buffer, comm)
        if packet is not None:
            data += packet
        if packet is None or len(packet) < config.buffer:
            break
    return unpack(data)


def listen(addr, port, LOG=config.LOG) -> socket:
    s = socket(AF_INET, SOCK_STREAM)
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    s.bind((addr, port))
    s.listen(config.MAX_LISTEN)
    if LOG:
        print(f'[INFO] Start Listen at {addr} : {port}')
    return s


def local_send(data, filename: str = None, LOG=config.LOG):
    if filename is None:
        filename = config.default_filepath + str((time.time())) + str(random.random())
    if ('\\' not in filename) and ('/' not in filename):
        filename = config.default_filepath + filename
    with open(filename, "wb+") as f:
        pickle.dump(data, f)
        if LOG:
            print(f'[INFO] Data Dumped into {filename}')


def local_recv(filename: str, LOG=config.LOG):
    filename = config.default_filepath + filename
    with open(filename, "rb") as f:
        data = pickle.load(f)
        if LOG:
            print(f'[INFO] Data loaded from {filename}')
    return data
