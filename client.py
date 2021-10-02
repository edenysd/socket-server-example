import socket
import string
import random
import os
import threading
import logging
import time
import struct
import argparse

parser = argparse.ArgumentParser()


parser.add_argument('--host', '-H',
                    help="Host address.",
                    default='localhost')

parser.add_argument('--port', '-P',
                    help="Host port.",
                    default=9999)

parser.add_argument('--string_number', '-SN',
                    help="Number of strings to process.",
                    default=1000000)

parser.add_argument('--stored_path', '-SP',
                    help="Path to the file where the strings will be stored.",
                    default='chains.txt')

parser.add_argument('--log_path', '-LP',
                    help="Path to the log file.",
                    default='client.log')

parser.add_argument('--verbose', '-V',
                    help="Verbosity output. Verbose output ignore LOG_PATH \
                    parameter.",
                    action='store_true',
                    default=False)

args = parser.parse_args()

VERBOSE = args.verbose
HOST, PORT = args.host, int(args.port)
NUMBER_OF_STRINGS = int(args.string_number)
PATH_TO_FILE = args.stored_path

LOG_FILE_PATH = args.log_path

LOG_FORMAT = '%(asctime)s -> %(levelname)s:\n%(message)s\n'

STR_CHARACTERS = string.ascii_letters + string.digits

log_file_handler = logging.FileHandler(LOG_FILE_PATH, 'w', 'utf-8', False)

if(VERBOSE):
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT,
                        handlers=[logging.StreamHandler()])
else:
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT,
                        handlers=[log_file_handler])


def random_string():
    """Generate a single random string that meets all requirements."""
    length = random.randint(50, 100)
    my_list = random.choices(STR_CHARACTERS, k=length)
    number_of_spaces = random.randint(3, 5)
    flag = True
    while flag:
        flag = False

        sample = random.sample(range(1, length-1), k=number_of_spaces)
        sample.sort()

        ant = -1
        for i in sample:
            if i-1 == ant:
                flag = True
                break
            ant = i

    for i in sample:
        my_list[i] = ' '

    return "".join(my_list)


def generate_file():
    """Generate a file with all the generated strings."""
    with open(PATH_TO_FILE, 'w') as file:
        for _ in range(NUMBER_OF_STRINGS):
            new_str = random_string()
            file.write(new_str+'\n')


def send_file_to_endpoint():
    """Send the complete file using high-performance sock.sendfile()."""
    with open(PATH_TO_FILE, 'rb') as file:
        sock.sendall(file_size.to_bytes(4, 'big'))
        sock.sendfile(file)


init_time = time.perf_counter()
generate_file()
file_generated_time = time.perf_counter()

file_size = os.path.getsize(PATH_TO_FILE)

# Create a socket (SOCK_STREAM means a TCP socket)
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    # Connect to server and send data
    sock.connect((HOST, PORT))

    # We use one thread to upload the data and the main thread
    # to download the data
    threading.Thread(target=send_file_to_endpoint).start()

    with open(PATH_TO_FILE, 'r') as file:
        # Receive a float (4-bytes) from the server for every line in
        # the file. The n-value represent the weight of the n-line because
        # the response stream is do it in order.
        #
        # In the next iteration is nice to have a greater buffer
        # (e.g. 4096 bytes) to improve the IO performance
        received = sock.recv(4)
        while received:
            (value,) = struct.unpack('>f', received)
            line = file.readline().strip()
            logging.info('\"%s\"\nValue: %f', line, value)
            received = sock.recv(4)

    elapsed_from_init_transaction = time.perf_counter() - file_generated_time
    elapsed_total = time.perf_counter() - init_time
    elapsed_from_file_creation = file_generated_time - init_time

    logging.info("File generated in %f seconds.",
                 elapsed_from_file_creation)
    logging.info("File transaction and response in %f seconds.",
                 elapsed_from_init_transaction)
    logging.info("Client side operations in %f seconds.",
                 elapsed_total)
