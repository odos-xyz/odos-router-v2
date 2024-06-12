import math
import random

from lib.utils import decode_address, decode_amount, decode_bytes, decode_amount_with_length


def decode_compact_swap_data(
    compact_swap_data,
    address_list
):
    input_token, index = decode_address(0, compact_swap_data, address_list)
    output_token, index = decode_address(index, compact_swap_data, address_list)

    input_amount, index = decode_amount(index, compact_swap_data)
    output_quote, index = decode_amount(index, compact_swap_data)

    max_slippage_int, index = decode_amount_with_length(index, compact_swap_data, 3)
    max_slippage_percent = max_slippage_int / int(0xFFFFFF)

    executor, index = decode_address(index, compact_swap_data, address_list)

    if compact_swap_data[index:index+4] == "0000":
        input_dest = executor
        index += 4
    else:
        input_dest, index = decode_address(index, compact_swap_data, address_list)

    if compact_swap_data[index:index+4] == "0000":
        output_dest = "msg.sender"
        index += 4
    else:
        output_dest, index = decode_address(index, compact_swap_data, address_list)

    referral_code, index = decode_amount_with_length(index, compact_swap_data, 4)
    path_def_bytes, index = decode_bytes(index, compact_swap_data)

    return (
        path_def_bytes,
        input_token,
        output_token,
        input_amount,
        output_quote,
        max_slippage_percent,
        executor,
        input_dest,
        output_dest,
        referral_code
    )

