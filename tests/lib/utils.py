import math
import random

from web3 import Web3


def random_hex_string(num_bytes):
    hex_string = "0x"

    for i in range(num_bytes * 2):
        hex_string += random.choice(
            [
                "0",
                "1",
                "2",
                "3",
                "4",
                "5",
                "6",
                "7",
                "8",
                "9",
                "a",
                "b",
                "c",
                "d",
                "e",
                "f",
            ]
        )

    return hex_string


def random_private_key():
    return random_hex_string(32)


def random_address():
    return random_hex_string(20)


# Encodes an unsigned integer as bytes to be decoded by the smart contract
def encode_bytes_list(num, length):
    assert num < (1 << (length * 8)), "Number too big to be encoded"
    return [((num >> ((length - i - 1) * 8)) & 0xFF) for i in range(length)]


def encode_bytes_string(num, length):
    return bytes(encode_bytes_list(num, length)).hex()


def encode_address(address, address_list):

    # If address is cached in the address list, encode its position plus 2 for the two special cases
    if address in address_list:
        return encode_bytes_string(address_list.index(address) + 2, 2)
    elif address == "0x0000000000000000000000000000000000000000":
        return "0000"
    else:
        return "0001" + address[2:]


def encode_amount(amount):
    if amount == 0:
        return "00"
    else:
        byte_length = max(math.ceil(math.log2(amount) / 8), 1)

        return encode_bytes_string(byte_length, 1) + encode_bytes_string(
            amount, byte_length
        )


def encode_bytes(byte_string):
    string_length = len(byte_string[2:])
    padding_length = 64 - (string_length % 64)

    padded_byte_string = byte_string[2:]
    if padding_length < 64:
        padded_byte_string += "0" * padding_length

    num_words = len(padded_byte_string) // 64

    return encode_bytes_string(num_words, 1) + padded_byte_string
