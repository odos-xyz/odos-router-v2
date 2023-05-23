import math
import random
from typing import NamedTuple

from lib.utils import encode_bytes_string
from web3 import Web3


# watch for updates to signature format
class SignableMessage(NamedTuple):
    version: bytes  # must be length 1
    header: bytes  # aka "version specific data"
    body: bytes  # aka "data to sign"


def token_permissions_hash(token, amount):
    _TOKEN_PERMISSIONS_TYPEHASH = Web3.keccak(
        text="TokenPermissions(address token,uint256 amount)"
    ).hex()

    return Web3.keccak(
        hexstr=_TOKEN_PERMISSIONS_TYPEHASH
        + ("0" * 24)
        + token[2:]
        + encode_bytes_string(amount, 32)
    ).hex()[2:]


def permit_transfer_from_hash(type_hash, permissions_hash, spender, nonce, deadline):
    return Web3.keccak(
        hexstr=(
            type_hash
            + permissions_hash
            + ("0" * 24)
            + spender[2:]
            + encode_bytes_string(nonce, 32)
            + encode_bytes_string(deadline, 32)
        )
    ).hex()


def single_permit2_hash(
    input_token, input_amount, permit2_spender, permit2_nonce, permit2_deadline
):
    _PERMIT_TRANSFER_FROM_TYPEHASH = Web3.keccak(
        text="PermitTransferFrom(TokenPermissions permitted,address spender,uint256 nonce,uint256 deadline)TokenPermissions(address token,uint256 amount)"
    ).hex()

    return permit_transfer_from_hash(
        _PERMIT_TRANSFER_FROM_TYPEHASH,
        token_permissions_hash(input_token, input_amount),
        permit2_spender,
        permit2_nonce,
        permit2_deadline,
    )


def batch_permit2_hash(
    input_tokens, input_amounts, permit2_spender, permit2_nonce, permit2_deadline
):
    _PERMIT_BATCH_TRANSFER_FROM_TYPEHASH = Web3.keccak(
        text="PermitBatchTransferFrom(TokenPermissions[] permitted,address spender,uint256 nonce,uint256 deadline)TokenPermissions(address token,uint256 amount)"
    ).hex()

    # Extract ERC20 (not ETH/native token) token info
    erc20_tokens = []
    erc20_amounts = []
    for t, token in enumerate(input_tokens):
        if token != "0x0000000000000000000000000000000000000000":
            erc20_tokens.append(token)
            erc20_amounts.append(input_amounts[t])

    concatenated_permission_hashes = "0x"

    for t, token in enumerate(erc20_tokens):
        concatenated_permission_hashes += token_permissions_hash(
            token, erc20_amounts[t]
        )

    return permit_transfer_from_hash(
        _PERMIT_BATCH_TRANSFER_FROM_TYPEHASH,
        Web3.keccak(hexstr=concatenated_permission_hashes).hex()[2:],
        permit2_spender,
        permit2_nonce,
        permit2_deadline,
    )
