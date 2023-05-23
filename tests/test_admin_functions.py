import brownie
import pytest
from lib import utils
from brownie import accounts


@pytest.fixture
def router():
    return brownie.OdosRouterV2.deploy(
        "0x0000000000000000000000000000000000000000",
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


def test_swap_protected(router, weth_executor):
    weth_address = weth_executor.WETH()
    input_amount = int(1e18)

    with brownie.reverts("Ownable: caller is not the owner"):
        router.swapRouterFunds(
            [
                [
                    "0x0000000000000000000000000000000000000000",
                    input_amount,
                    weth_executor.address,
                ]
            ],
            [[weth_address, 1, accounts[1]]],
            input_amount,
            "0x0100000000000000000000000000000000000000000000000000000000000000",
            weth_executor.address,
            {
                "value": 0,
                "from": accounts[1],
            },
        )


def test_swap_slippage_exceeded(router, weth_executor):
    weth_address = weth_executor.WETH()
    input_amount = int(1e18)

    accounts[0].transfer(
        router.address,
        input_amount,
    )
    with brownie.reverts("Slippage Limit Exceeded"):
        router.swapRouterFunds(
            [
                [
                    "0x0000000000000000000000000000000000000000",
                    input_amount,
                    weth_executor.address,
                ]
            ],
            [[weth_address, 1, accounts[1]]],
            input_amount + 1,
            "0x0100000000000000000000000000000000000000000000000000000000000000",
            weth_executor.address,
            {
                "value": 0,
                "from": accounts[0],
            },
        )


def test_swap_router_funds(router, weth_executor):
    weth_address = weth_executor.WETH()
    input_amount = int(1e18)

    accounts[0].transfer(
        router.address,
        input_amount,
    )
    WETH = brownie.interface.IWETH(weth_address)
    balance_before = WETH.balanceOf(accounts[1])

    router.swapRouterFunds(
        [
            [
                "0x0000000000000000000000000000000000000000",
                input_amount,
                weth_executor.address,
            ]
        ],
        [[weth_address, 1, accounts[1]]],
        input_amount,
        "0x0100000000000000000000000000000000000000000000000000000000000000",
        weth_executor.address,
        {
            "value": 0,
            "from": accounts[0],
        },
    )
    assert WETH.balanceOf(accounts[1]) - balance_before == input_amount


def test_swap_router_funds_max(router, weth_executor):
    weth_address = weth_executor.WETH()
    input_amount = int(1e18)

    accounts[0].transfer(
        router.address,
        input_amount,
    )
    WETH = brownie.interface.IWETH(weth_address)
    balance_before = WETH.balanceOf(accounts[1])

    router.swapRouterFunds(
        [["0x0000000000000000000000000000000000000000", 0, weth_executor.address]],
        [[weth_address, 1, accounts[1]]],
        input_amount,
        "0x0100000000000000000000000000000000000000000000000000000000000000",
        weth_executor.address,
        {
            "value": 0,
            "from": accounts[0],
        },
    )
    assert WETH.balanceOf(accounts[1]) - balance_before == input_amount


def test_write_address_list_protected(router, weth_executor):
    addresses_to_write = [utils.random_address() for i in range(3)]
    with brownie.reverts("Ownable: caller is not the owner"):
        router.writeAddressList(
            addresses_to_write,
            {
                "from": accounts[1],
            },
        )


def test_write_address_list(router, weth_executor):

    addresses_to_write = [utils.random_address() for i in range(3)]
    router.writeAddressList(
        addresses_to_write,
        {
            "from": accounts[0],
        },
    )
    for i, address in enumerate(addresses_to_write):
        assert address == router.addressList(i)


def test_transfer_funds_protected(router, weth_executor):
    with brownie.reverts("Ownable: caller is not the owner"):
        router.transferRouterFunds(
            [],
            [],
            accounts[0],
            {
                "from": accounts[1],
            },
        )


def test_transfer_funds(router, weth_executor):

    input_amount = int(1e18)

    accounts[0].transfer(
        router.address,
        input_amount,
    )
    balance_before = accounts[1].balance()

    router.transferRouterFunds(
        ["0x0000000000000000000000000000000000000000"],
        [input_amount],
        accounts[1],
        {
            "from": accounts[0],
        },
    )
    assert accounts[1].balance() - balance_before == input_amount


def test_transfer_funds_max(router, weth_executor):

    input_amount = int(1e18)

    accounts[0].transfer(
        router.address,
        input_amount,
    )
    balance_before = accounts[1].balance()

    router.transferRouterFunds(
        ["0x0000000000000000000000000000000000000000"],
        [0],
        accounts[1],
        {
            "from": accounts[0],
        },
    )
    assert accounts[1].balance() - balance_before == input_amount


def test_set_multi_swap_fee_protected(router, weth_executor):
    with brownie.reverts("Ownable: caller is not the owner"):
        router.setSwapMultiFee(
            0,
            {
                "from": accounts[1],
            },
        )


def test_set_multi_swap_fee_too_high(router, weth_executor):
    fee_denom = router.FEE_DENOM()

    with brownie.reverts("Fee too high"):
        router.setSwapMultiFee(
            fee_denom,
            {
                "from": accounts[0],
            },
        )


def test_set_multi_swap_fee(router, weth_executor):
    fee_denom = router.FEE_DENOM()

    new_multi_swap_fee = int(fee_denom * 0.0001)

    router.setSwapMultiFee(
        new_multi_swap_fee,
        {
            "from": accounts[0],
        },
    )
    assert router.swapMultiFee() == new_multi_swap_fee
