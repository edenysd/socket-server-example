## Introduction

The project implements a concurrent application that uses a socket-based client/server architecture. It generates a file on the client side, then sends this file to the server through a socket and finally the server returns the value of each line previously sent to the client.

## Requirements

- [Python](https://www.python.org/downloads/) >= 3.8.
- POSIX platform that support _`fork()`_.

## `server.py`

`server.py` is the responsible to process the file that `client.py` sends via `socket` and calculates the value of each line. While the server receives the data stream it responds to the client at the same time.

The value is calculated by the formula:

- $(amount\_of\_alphabetic\_characters * 1.5 + amount\_of\_numbers * 2)/amount\_of\_spaces$

But if the string has case insensitive **two** consecutive 'a's the value is remplaced by 1000 and log a message like:

> “Double ‘a’ rule detected >> ‘Aahfiwfbuswbf sdfsibf sdufbas dfysdf‘“.

## `client.py`

`client.py` is the responsible for creating the file with the random lines (_`chains.txt`_) and sending it to the server in another _thread_, then while the server starts receiving the data it will respond in parallel and we don't need to wait for the stream to finish to get the first results.

## How to use

First run `server.py` with python interpreter:

```bash
python server.py
```

Then run `client.py` interpreter:

```bash
python client.py
```

### Default behavior:

The server runs on localhost on port **9999** then the client connects and sends one million lines. You can change that behavior in both apps.

### For example

In the server app you can setup:

- The port.
- The buffer size of the socket.
- The log to the console instead of a file.
- The log file path.

In the client app you can setup:

- The host.
- The port.
- The number of random strings generated.
- The path to the file where the strings will be stored.
- The path log file.
- The log to the console instead of a file.

If you want to know how to do any of the above things you only need to type:

_server case_

```bash
python server.py -h
```

_client case_

```bash
python client.py -h
```

And pass the desired parameters.

_Please note that the project is intended to be used as simple scripts_

## License

[MIT](https://spdx.org/licenses/MIT)
