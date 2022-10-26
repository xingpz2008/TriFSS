import random
from socket import *
import pickle
import Pythonic_TriFSS.Configs.communication as config
import time
from Pythonic_TriFSS.Utils.statistics import get_data_size


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
    data = pickle.dumps(data)
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
    return pickle.loads(data)


def listen(addr, port, LOG=config.LOG) -> socket:
    s = socket(AF_INET, SOCK_STREAM)
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
