import json
import random

import brownie
import pytest
from brownie import accounts
from eth_account import Account
from hexbytes import HexBytes
from lib import encode_compact, permit2, utils
from web3 import Web3


@pytest.fixture
def router():
    return brownie.OdosRouterV2.deploy(
        {
            "from": accounts[0],
        },
    )


@pytest.fixture
def weth_executor():
    WETH = brownie.WETH9.deploy(
        {
            "from": accounts[0],
        }
    )
    return brownie.OdosWETHExecutor.deploy(
        WETH.address,
        {
            "from": accounts[0],
        },
    )


def test_swap_wrong_msg_value(router, weth_executor):
    weth_address = weth_executor.WETH()
    input_amount = int(1e18)

    with brownie.reverts("Wrong msg.value"):
        router.swap(
            [
                "0x0000000000000000000000000000000000000000",
                input_amount,
                weth_executor.address,
                weth_address,
                input_amount,
                input_amount,
                accounts[0],
            ],
            "0x0100000000000000000000000000000000000000000000000000000000000000",
            weth_executor.address,
            0,
            {
                "value": 0,
                "from": accounts[0],
            },
        )


def test_swap_in_equals_out(router, weth_executor):
    input_amount = int(1e18)

    with brownie.reverts("Arbitrage not supported"):
        router.swap(
            [
                "0x0000000000000000000000000000000000000000",
                input_amount,
                weth_executor.address,
                "0x0000000000000000000000000000000000000000",
                input_amount,
                input_amount,
                accounts[0],
            ],
            "0x0100000000000000000000000000000000000000000000000000000000000000",
            weth_executor.address,
            0,
            {
                "value": input_amount,
                "from": accounts[0],
            },
        )


def test_swap_zero_min_out(router, weth_executor):
    weth_address = weth_executor.WETH()
    input_amount = int(1e18)

    with brownie.reverts("Slippage limit too low"):
        router.swap(
            [
                "0x0000000000000000000000000000000000000000",
                input_amount,
                weth_executor.address,
                weth_address,
                input_amount,
                0,
                accounts[0],
            ],
            "0x0100000000000000000000000000000000000000000000000000000000000000",
            weth_executor.address,
            0,
            {
                "value": input_amount,
                "from": accounts[0],
            },
        )


def test_swap_quote_over_min(router, weth_executor):
    weth_address = weth_executor.WETH()
    input_amount = int(1e18)

    with brownie.reverts("Minimum greater than quote"):
        router.swap(
            [
                "0x0000000000000000000000000000000000000000",
                input_amount,
                weth_executor.address,
                weth_address,
                input_amount,
                input_amount + 1,
                accounts[0],
            ],
            "0x0100000000000000000000000000000000000000000000000000000000000000",
            weth_executor.address,
            0,
            {
                "value": input_amount,
                "from": accounts[0],
            },
        )


def test_swap_slippage_exceeded(router, weth_executor):
    weth_address = weth_executor.WETH()
    input_amount = int(1e18)

    with brownie.reverts("Slippage Limit Exceeded"):
        router.swap(
            [
                "0x0000000000000000000000000000000000000000",
                input_amount,
                weth_executor.address,
                weth_address,
                input_amount + 1,
                input_amount + 1,
                accounts[0],
            ],
            "0x0100000000000000000000000000000000000000000000000000000000000000",
            weth_executor.address,
            0,
            {
                "value": input_amount,
                "from": accounts[0],
            },
        )


def test_swap_output(router, weth_executor):
    weth_address = weth_executor.WETH()
    input_amount = int(1e18)

    WETH = brownie.interface.IWETH(weth_address)
    balance_before = WETH.balanceOf(accounts[0])

    router.swap(
        [
            "0x0000000000000000000000000000000000000000",
            input_amount,
            weth_executor.address,
            weth_address,
            input_amount,
            input_amount,
            accounts[0],
        ],
        "0x0100000000000000000000000000000000000000000000000000000000000000",
        weth_executor.address,
        0,
        {
            "value": input_amount,
            "from": accounts[0],
        },
    )
    assert WETH.balanceOf(accounts[0]) - balance_before == input_amount

    WETH.approve(
        router.address,
        input_amount,
        {
            "from": accounts[0],
        },
    )
    balance_before = accounts[1].balance()

    router.swap(
        [
            weth_address,
            input_amount,
            weth_executor.address,
            "0x0000000000000000000000000000000000000000",
            input_amount,
            input_amount,
            accounts[1],
        ],
        "0x0000000000000000000000000000000000000000000000000000000000000000",
        weth_executor.address,
        0,
        {
            "value": 0,
            "from": accounts[0],
        },
    )
    assert accounts[1].balance() - balance_before == input_amount


def test_swap_max_output(router, weth_executor):
    weth_address = weth_executor.WETH()
    input_amount = int(1e18)

    WETH = brownie.interface.IWETH(weth_address)
    balance_before = WETH.balanceOf(accounts[0])

    router.swap(
        [
            "0x0000000000000000000000000000000000000000",
            0,
            weth_executor.address,
            weth_address,
            input_amount,
            input_amount,
            accounts[0],
        ],
        "0x0100000000000000000000000000000000000000000000000000000000000000",
        weth_executor.address,
        0,
        {
            "value": input_amount,
            "from": accounts[0],
        },
    )
    assert WETH.balanceOf(accounts[0]) - balance_before == input_amount

    input_amount = WETH.balanceOf(accounts[0])

    WETH.approve(
        router.address,
        input_amount,
        {
            "from": accounts[0],
        },
    )
    balance_before = accounts[1].balance()

    router.swap(
        [
            weth_address,
            0,
            weth_executor.address,
            "0x0000000000000000000000000000000000000000",
            input_amount,
            input_amount,
            accounts[1],
        ],
        "0x0000000000000000000000000000000000000000000000000000000000000000",
        weth_executor.address,
        0,
        {
            "value": 0,
            "from": accounts[0],
        },
    )
    assert accounts[1].balance() - balance_before == input_amount


def test_swap_output_transfer(router, weth_executor):
    weth_address = weth_executor.WETH()
    input_amount = int(1e18)

    WETH = brownie.interface.IWETH(weth_address)
    balance_before = WETH.balanceOf(accounts[0])

    router.swap(
        [
            "0x0000000000000000000000000000000000000000",
            input_amount,
            weth_executor.address,
            weth_address,
            input_amount,
            input_amount,
            accounts[0],
        ],
        "0x0100000000000000000000000000000000000000000000000000000000000000",
        weth_executor.address,
        0,
        {
            "value": input_amount,
            "from": accounts[1],
        },
    )
    assert WETH.balanceOf(accounts[0]) - balance_before == input_amount


def test_swap_referral_fee(router, weth_executor):
    weth_address = weth_executor.WETH()
    input_amount = int(1e18)

    referral_with_fee_threshold = router.REFERRAL_WITH_FEE_THRESHOLD()
    fee_denom = router.FEE_DENOM()

    referral_code = referral_with_fee_threshold + 1
    referral_fee = int(1e14)
    referral_beneficiary = accounts[1]

    router.registerReferralCode(
        referral_code,
        referral_fee,
        referral_beneficiary,
        {
            "from": accounts[0],
        },
    )

    WETH = brownie.interface.IWETH(weth_address)

    expected_user_delta = input_amount * (fee_denom - referral_fee) // fee_denom
    expected_beneficiary_delta = input_amount * 8 * referral_fee // (fee_denom * 10)
    expected_router_delta = (
        input_amount - expected_user_delta - expected_beneficiary_delta
    )

    user_balance_before = WETH.balanceOf(accounts[0])
    router_balance_before = WETH.balanceOf(router.address)
    beneficiary_balance_before = WETH.balanceOf(referral_beneficiary)

    router.swap(
        [
            "0x0000000000000000000000000000000000000000",
            input_amount,
            weth_executor.address,
            weth_address,
            expected_user_delta,
            expected_user_delta,
            accounts[0],
        ],
        "0x0100000000000000000000000000000000000000000000000000000000000000",
        weth_executor.address,
        referral_code,
        {
            "value": input_amount,
            "from": accounts[0],
        },
    )
    assert WETH.balanceOf(accounts[0]) - user_balance_before == expected_user_delta
    assert (
        WETH.balanceOf(referral_beneficiary) - beneficiary_balance_before
        == expected_beneficiary_delta
    )
    assert (
        WETH.balanceOf(router.address) - router_balance_before == expected_router_delta
    )


def test_swap_permit2(router, weth_executor):
    weth_address = weth_executor.WETH()
    input_amount = int(1e18)

    PERMIT2 = brownie.Permit2.deploy(
        {
            "from": accounts[0],
        }
    )
    WETH = brownie.interface.IWETH(weth_address)

    # Use accounts to sign and send EIP712 signature for Permit2
    private_key = utils.random_private_key()
    this_account = Account.from_key(private_key).address

    # Get WETH into the account
    router.swap(
        [
            "0x0000000000000000000000000000000000000000",
            input_amount,
            weth_executor.address,
            weth_address,
            input_amount,
            input_amount,
            this_account,
        ],
        "0x0100000000000000000000000000000000000000000000000000000000000000",
        weth_executor.address,
        0,
        {
            "value": input_amount,
            "from": accounts[0],
        },
    )
    # Transfer ETH into the account
    accounts[0].transfer(
        this_account,
        int(1e18),
    )
    # Approve WETH for use by Permit2
    WETH.approve(
        PERMIT2.address,
        input_amount,
        {
            "from": this_account,
        },
    )
    # Create Permit2 signature
    permit2_nonce = 0
    permit2_deadline = (1 << 48) - 1
    permit2_sign_hash = permit2.single_permit2_hash(
        weth_address, input_amount, router.address, permit2_nonce, permit2_deadline
    )
    message = permit2.SignableMessage(
        HexBytes("0x1"),
        HexBytes(PERMIT2.DOMAIN_SEPARATOR()),
        HexBytes(permit2_sign_hash),
    )
    signed_message = Account.sign_message(message, private_key=private_key)
    signature = signed_message.signature.hex()

    balance_before = accounts[0].balance()

    router.swapPermit2(
        [PERMIT2.address, permit2_nonce, permit2_deadline, signature],
        [
            weth_address,
            input_amount,
            weth_executor.address,
            "0x0000000000000000000000000000000000000000",
            input_amount,
            input_amount,
            accounts[0],
        ],
        "0x0000000000000000000000000000000000000000000000000000000000000000",
        weth_executor.address,
        0,
        {
            "value": 0,
            "from": this_account,
        },
    )
    assert accounts[0].balance() - balance_before == input_amount


def test_swap_compact_max(router, weth_executor):
    weth_address = weth_executor.WETH()
    input_amount = int(1e18)

    endpoint_uri = "http://localhost:8545"
    w3 = Web3(Web3.HTTPProvider(endpoint_uri, request_kwargs={"timeout": 600}))

    private_key = utils.random_private_key()
    test_account = Account.from_key(private_key)
    w3.eth.default_account = test_account.address

    # Transfer ETH into the account
    accounts[0].transfer(
        test_account.address,
        input_amount,
    )
    WETH = brownie.interface.IWETH(weth_address)
    balance_before = WETH.balanceOf(test_account.address)

    with open("build/contracts/OdosRouterV2.json", "r") as f:
        router_v2_contract = w3.eth.contract(
            abi=json.load(f)["abi"], address=router.address
        )
    compact_router_data = encode_compact.construct_compact_swap_data(
        "0x01",
        "0x0000000000000000000000000000000000000000",
        weth_address,
        0,
        input_amount,
        0.01,
        weth_executor.address,
        weth_executor.address,
        "msg.sender",
        [],
        0,
    )
    swap_compact_txn = router_v2_contract.functions.swapCompact().build_transaction(
        {
            "gas": 10_000_000,
            "gasPrice": 0,
            "value": input_amount,
            "nonce": w3.eth.get_transaction_count(test_account.address),
        }
    )
    swap_compact_txn["data"] += compact_router_data[2:]

    signed_swap_txn = w3.eth.account.sign_transaction(swap_compact_txn, private_key)
    w3.eth.send_raw_transaction(signed_swap_txn.rawTransaction)

    assert WETH.balanceOf(test_account.address) - balance_before == input_amount

    balance_before = w3.eth.get_balance(test_account.address)

    compact_router_data = encode_compact.construct_compact_swap_data(
        "0x00",
        weth_address,
        "0x0000000000000000000000000000000000000000",
        0,
        input_amount,
        0.01,
        weth_executor.address,
        weth_executor.address,
        "msg.sender",
        [],
        0,
    )
    WETH.approve(
        router.address,
        input_amount,
        {
            "from": test_account.address,
        },
    )
    swap_compact_txn = router_v2_contract.functions.swapCompact().build_transaction(
        {
            "gas": 10_000_000,
            "gasPrice": 0,
            "value": 0,
            "nonce": w3.eth.get_transaction_count(test_account.address),
        }
    )
    swap_compact_txn["data"] += compact_router_data[2:]

    signed_swap_txn = w3.eth.account.sign_transaction(swap_compact_txn, private_key)
    w3.eth.send_raw_transaction(signed_swap_txn.rawTransaction)

    assert w3.eth.get_balance(test_account.address) - balance_before == input_amount


def test_swap_compact_transfer(router, weth_executor):
    weth_address = weth_executor.WETH()
    input_amount = int(1e18)

    endpoint_uri = "http://localhost:8545"
    w3 = Web3(Web3.HTTPProvider(endpoint_uri, request_kwargs={"timeout": 600}))

    private_key = utils.random_private_key()
    test_account = Account.from_key(private_key)
    w3.eth.default_account = test_account.address

    # Transfer ETH into the account
    accounts[0].transfer(
        test_account.address,
        input_amount,
    )
    WETH = brownie.interface.IWETH(weth_address)
    balance_before = WETH.balanceOf(accounts[1].address)

    with open("build/contracts/OdosRouterV2.json", "r") as f:
        router_v2_contract = w3.eth.contract(
            abi=json.load(f)["abi"], address=router.address
        )
    compact_router_data = encode_compact.construct_compact_swap_data(
        "0x01",
        "0x0000000000000000000000000000000000000000",
        weth_address,
        input_amount,
        input_amount,
        0.01,
        weth_executor.address,
        weth_executor.address,
        accounts[1].address,
        [],
        0,
    )
    swap_compact_txn = router_v2_contract.functions.swapCompact().build_transaction(
        {
            "gas": 10_000_000,
            "gasPrice": 0,
            "value": input_amount,
            "nonce": w3.eth.get_transaction_count(test_account.address),
        }
    )
    swap_compact_txn["data"] += compact_router_data[2:]

    signed_swap_txn = w3.eth.account.sign_transaction(swap_compact_txn, private_key)
    w3.eth.send_raw_transaction(signed_swap_txn.rawTransaction)

    assert WETH.balanceOf(accounts[1].address) - balance_before == input_amount


def test_swap_compact_address_list(router, weth_executor):
    weth_address = weth_executor.WETH()
    input_amount = int(1e18)

    endpoint_uri = "http://localhost:8545"
    w3 = Web3(Web3.HTTPProvider(endpoint_uri, request_kwargs={"timeout": 600}))

    private_key = utils.random_private_key()
    test_account = Account.from_key(private_key)
    w3.eth.default_account = test_account.address

    # Transfer ETH into the account
    accounts[0].transfer(
        test_account.address,
        input_amount,
    )
    # Set address list to be used by the compact swap function
    address_list = [weth_address, weth_executor.address]
    router.writeAddressList(
        address_list,
        {
            "from": accounts[0],
        },
    )
    WETH = brownie.interface.IWETH(weth_address)
    balance_before = WETH.balanceOf(test_account.address)

    with open("build/contracts/OdosRouterV2.json", "r") as f:
        router_v2_contract = w3.eth.contract(
            abi=json.load(f)["abi"], address=router.address
        )
    compact_multi_router_data = encode_compact.construct_compact_swap_data(
        "0x01",
        "0x0000000000000000000000000000000000000000",
        weth_address,
        input_amount,
        input_amount,
        0.01,
        weth_executor.address,
        weth_executor.address,
        "msg.sender",
        address_list,
        0,
    )
    swap_compact_txn = router_v2_contract.functions.swapCompact().build_transaction(
        {
            "gas": 10_000_000,
            "gasPrice": 0,
            "value": input_amount,
            "nonce": w3.eth.get_transaction_count(test_account.address),
        }
    )
    swap_compact_txn["data"] += compact_multi_router_data[2:]

    signed_swap_txn = w3.eth.account.sign_transaction(swap_compact_txn, private_key)
    w3.eth.send_raw_transaction(signed_swap_txn.rawTransaction)

    assert WETH.balanceOf(test_account.address) - balance_before == input_amount
