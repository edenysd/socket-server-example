import socketserver
import logging
import time
import re
import struct
import argparse

parser = argparse.ArgumentParser()

parser.add_argument('--port', '-P',
                    help="Host port.",
                    default=9999)

parser.add_argument('--buffer_size', '-BF',
                    help="Buffer size of the host socket.",
                    default=4096)

parser.add_argument('--log_path', '-LP',
                    help="Path to the log file.",
                    default='server.log')

parser.add_argument('--verbose', '-V',
                    help="Verbosity output. Verbose output ignore LOG_PATH \
                    parameter.",
                    action='store_true',
                    default=False)

args = parser.parse_args()

VERBOSE = args.verbose
HOST, PORT = "localhost", int(args.port)
BUFFER_SIZE = int(args.buffer_size)
LOG_FILE_PATH = args.log_path
LOG_FORMAT = '%(asctime)s -> %(process)d: %(levelname)s: "%(message)s"'


if(VERBOSE):
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT,
                        handlers=[logging.StreamHandler()])
else:
    logging.basicConfig(filename=LOG_FILE_PATH, filemode='w',
                        level=logging.INFO, format=LOG_FORMAT)


pattern_aa = re.compile("[Aa][Aa]")
pattern_letter = re.compile("[a-zA-Z]")
pattern_number = re.compile("[0-9]")
pattern_space = re.compile(" ")


def process_str(cur_str: str):
    """Calculate the string value according to the rules."""
    if pattern_aa.search(cur_str):
        logging.info('Double \'a\' rule detected >> \'%s\'', cur_str)
        return 1000
    number_of_letters = len(pattern_letter.findall(cur_str))
    number_of_digits = len(pattern_number.findall(cur_str))
    number_of_spaces = len(pattern_space.findall(cur_str))

    return (number_of_letters*1.5 + number_of_digits*2)/(number_of_spaces)


class MyTCPHandler(socketserver.StreamRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        """Handle the client request."""
        init_time = time.perf_counter()

        # The first 4 bytes are the number of total bytes of the file
        length = int.from_bytes(self.request.recv(4), byteorder='big')
        total_buffer = length

        my_string = ''

        while total_buffer:

            read_size = min(BUFFER_SIZE, total_buffer)
            data: bytes = self.request.recv(read_size)
            total_buffer -= len(data)

            my_string += str(data, 'utf-8')

            my_string_parts = my_string.splitlines()

            split_rem_size = 0
            for i in my_string_parts:
                split_rem_size += len(i)

            amount_of_linebreaks = len(my_string) - split_rem_size

            for i in range(amount_of_linebreaks):
                str_to_procces = my_string_parts[i]
                value = process_str(str_to_procces)
                # self.request is the TCP socket connected to the client.
                self.request.sendall(struct.pack('>f', value))

            if len(my_string_parts) > amount_of_linebreaks:
                my_string = my_string_parts[len(my_string_parts)-1]
            else:
                my_string = ''

        elapsed = time.perf_counter() - init_time

        logging.info("File processed in %f seconds.", elapsed)


# Create a TCP Forking Server, binding to localhost on $PORT
with socketserver.ForkingTCPServer((HOST, PORT), MyTCPHandler) as server:
    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
