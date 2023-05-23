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


def test_used_code(router):
    beneficiary = utils.random_address()

    with brownie.reverts("Code in use"):
        router.registerReferralCode(
            0,
            0,
            beneficiary,
            {
                "from": accounts[0],
            },
        )


def test_high_fee(router):
    beneficiary = utils.random_address()

    with brownie.reverts("Fee too high"):
        router.registerReferralCode(
            1,
            int(1e18 / 49),
            beneficiary,
            {
                "from": accounts[0],
            },
        )


def test_fee_threshold_under(router):
    referral_with_fee_threshold = router.REFERRAL_WITH_FEE_THRESHOLD()
    beneficiary = utils.random_address()

    with brownie.reverts("Invalid fee for code"):
        router.registerReferralCode(
            referral_with_fee_threshold,
            1,
            beneficiary,
            {
                "from": accounts[0],
            },
        )


def test_fee_threshold_over(router):
    referral_with_fee_threshold = router.REFERRAL_WITH_FEE_THRESHOLD()
    beneficiary = utils.random_address()

    with brownie.reverts("Invalid fee for code"):
        router.registerReferralCode(
            referral_with_fee_threshold + 1,
            0,
            beneficiary,
            {
                "from": accounts[0],
            },
        )


def test_null_beneficiary(router):
    referral_with_fee_threshold = router.REFERRAL_WITH_FEE_THRESHOLD()

    with brownie.reverts("Null beneficiary"):
        router.registerReferralCode(
            referral_with_fee_threshold + 1,
            1,
            "0x0000000000000000000000000000000000000000",
            {
                "from": accounts[0],
            },
        )


def test_register_referral(router):
    referral_with_fee_threshold = router.REFERRAL_WITH_FEE_THRESHOLD()
    beneficiary = utils.random_address()

    router.registerReferralCode(
        referral_with_fee_threshold + 1,
        1_000_000,
        beneficiary,
        {
            "from": accounts[0],
        },
    )
    referral_info = router.referralLookup(referral_with_fee_threshold + 1)

    assert referral_info[0] == 1_000_000
    assert referral_info[1] == beneficiary
    assert referral_info[2] == 1
