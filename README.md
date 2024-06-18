# Odos Router V2

## Overview

The Odos Router’s primary purpose is to serve as a security wrapper around the arbitrary execution of contract interactions to facilitate efficient token swaps. The Router holds user approvals and is in charge of ensuring that tokens are only transferred from the user in the specified amount when the user is executing a swap, and ensuring that the user gets at least the specified minimum amount out. The router accommodates different variations of swaps, including both single-to-single and multi-to-multi swaps, as well as a few different approval mechanisms. The router also collects and holds revenue (via positive slippage and/or fees) from the swapping activity.

## Features

### Swapping

The primary functions of the router are the user-facing swap functions that facilitate token exchange for users. The router supports atomic multi-input and multi-output swaps via the internal `_swapMulti` function, but also supports slightly more gas-efficient single-to-single swaps through the internal `_swap` function. The two functions also have different methods of revenue collection. The `_swap` function collects positive slippage when it occurs (defined as the difference between the executed and quoted output when the executed output is higher), while the `_swapMulti` function collects a flat fee defined by `swapMultiFee` on all swaps (and not positive slippage).

Both `_swap` and `_swapMulti` have several externally facing functions that can be called. For accessing the user's ERC20s, both variants allow for traditional approvals made directly to the router, as well as the use of Uniswap's Permit2 contract (as seen here: https://github.com/Uniswap/permit2). Both variants also have a `compact` option, which uses a custom decoder written in Yul to allow for significantly less calldata to be necessary to describe the swap than the normal endpoints. Although Yul typically has low readability, security assumptions for these two functions are low since they make a call to the same internal function that is callable with arbitrary parameters via the normal endpoint. These compact variants can also make use of an immutable address list when `SLOAD` opcodes are cheaper than paying for the calldata needed to pass a full value in.

### Referrals

The router supports referral codes to track usage and, optionally, an additional fee that can be charged in conjunction with this referral code being used. New referral codes can be permissionlessly registered with the `registerReferralCode` function. A referral registration will consist of mapping a referral code to a `referralInfo` struct, which specifies the additional fee (if any), the beneficiary of the fee (again if any), and a boolean value specifying whether that code has already been registered. The largest half of the space of possible referral codes is eligible for an additional fee to be registered, while the lower half is strictly for tracking purposes in order to avoid extra storage reads. Once registered, `referralInfo` is immutable - if a change is needed, a new referral code will need to be registered.

A referral code can be used by passing it into the swap function as an argument when a swap is executed. If specified, the swap will then charge the referral fee on the output(s) of the swap and send 80% of the fee to the specified beneficiary immediately, retaining the remaining 20% as router revenue similar to positive slippage and multi-swap fees. The referral code will then be emitted in the swap event in order to track the activity.

### Owner Functionality

Through positive slippage and swap fees, the router collects and holds revenue generated from swap fees. This revenue is held in the router in order to avoid extra gas fees during the user's swap for additional transfers. Therefore, all funds held in the router are considered revenue already owned by the `owner` role. To manage this revenue, the router has several `owner`-protected functions. `writeAddressList` allows the owner to append new addresses (never change/remove) to the list for use in the compact decoders. `setSwapMultiFee` allows the swapMultiFee to be set by the owner, with an absolute maximum at 0.5% to prevent major abuse.

The owner can also use two remaining functions to access the collected revenue, `transferRouterFunds` and `swapRouterFunds`. `transferRouterFunds` allows for any ERC20 or ether held in the router to be transferred to a specified destination. `swapRouterFunds`, meanwhile, allows for funds held in the router to be directly used in a swap before being transferred - this is particularly useful for transferring out revenue in a single denomination (e.g. USDC) despite it originally being collected in many denominations.

## Setup

The Odos Router V2 uses Python with Brownie as the testing framework. Brownie can be installed using the preferred method as outlined in their installation documentation here: [Brownie Installation Documentation](https://eth-brownie.readthedocs.io/en/stable/install.html)

The project relies on v4.8.3 of OpenZeppelin's contract dependencies. With Brownie installed, these can be installed with:


```bash
brownie pm install OpenZeppelin/openzeppelin-contracts@4.8.3
```

Brownie also relies on Ganache to simulate transactions. If not already installed, Ganache CLI can be installed with npm:

```bash
npm install -g ganache-cli
```

Some tests utilize the Web3.py framework for additional functionality. This and any other Python dependencies are documented in `requirements.txt` and can be installed via:

```bash
pip install -r requirements.txt
```

## Running Tests

To test the Router's functionality, `OdosWethExecutor.sol` is provided as an example Odos Executor (production executors will be much more complex but will interact with the router in the same way). The `WETH` and `Permit2` contract directories are also provided as examples of what contracts the router may be interacting with. With the above dependencies installed, the full suite of tests can be run with:

```bash
brownie test
```

## Chain Deployments

### Mainnets

| Chain | Router Address |
| :-: | :-: |
| <img src="https://assets.odos.xyz/chains/ethereum.png" width="50" height="50"><br>Ethereum | [`0xCf5540fFFCdC3d510B18bFcA6d2b9987b0772559`](https://etherscan.io/address/0xcf5540fffcdc3d510b18bfca6d2b9987b0772559) |
| <img src="https://assets.odos.xyz/chains/arbitrum.png" width="50" height="50"><br>Arbitrum | [`0xa669e7A0d4b3e4Fa48af2dE86BD4CD7126Be4e13`](https://arbiscan.io/address/0xa669e7a0d4b3e4fa48af2de86bd4cd7126be4e13) |
| <img src="https://assets.odos.xyz/chains/base.png" width="50" height="50"><br>Base | [`0x19cEeAd7105607Cd444F5ad10dd51356436095a1`](https://basescan.org/address/0x19ceead7105607cd444f5ad10dd51356436095a1) |
| <img src="https://assets.odos.xyz/chains/optimism.png" width="50" height="50"><br>Optimism | [`0xCa423977156BB05b13A2BA3b76Bc5419E2fE9680`](https://optimistic.etherscan.io/address/0xca423977156bb05b13a2ba3b76bc5419e2fe9680) |
| <img src="https://assets.odos.xyz/chains/linea.png" width="50" height="50"><br>Linea | [`0x2d8879046f1559E53eb052E949e9544bCB72f414`](https://lineascan.build/address/0x2d8879046f1559E53eb052E949e9544bCB72f414) |
| <img src="https://assets.odos.xyz/chains/scroll.png" width="50" height="50"><br>Scroll | [`0xbFe03C9E20a9Fc0b37de01A172F207004935E0b1`](https://scrollscan.com/address/0xbFe03C9E20a9Fc0b37de01A172F207004935E0b1) |
| <img src="https://assets.odos.xyz/chains/mantle.png" width="50" height="50"><br>Mantle | [`0xD9F4e85489aDCD0bAF0Cd63b4231c6af58c26745`](https://mantlescan.xyz/address/0xD9F4e85489aDCD0bAF0Cd63b4231c6af58c26745) |
| <img src="https://assets.odos.xyz/chains/zksync.png" width="50" height="50"><br>ZKSync Era | [`0x4bBa932E9792A2b917D47830C93a9BC79320E4f7`](https://era.zksync.network/address/0x4bBa932E9792A2b917D47830C93a9BC79320E4f7) |
| <img src="https://assets.odos.xyz/chains/mode.png" width="50" height="50"><br>Mode | [`0x7E15EB462cdc67Cf92Af1f7102465a8F8c784874`](https://explorer.mode.network/address/0x7E15EB462cdc67Cf92Af1f7102465a8F8c784874) |
| <img src="https://assets.odos.xyz/chains/polygon.png" width="50" height="50"><br>Polygon PoS | [`0x4E3288c9ca110bCC82bf38F09A7b425c095d92Bf`](https://polygonscan.com/address/0x4e3288c9ca110bcc82bf38f09a7b425c095d92bf) |
| <img src="https://assets.odos.xyz/chains/avalanche.png" width="50" height="50"><br>Avalanche | [`0x88de50B233052e4Fb783d4F6db78Cc34fEa3e9FC`](https://snowscan.xyz/address/0x88de50B233052e4Fb783d4F6db78Cc34fEa3e9FC) |
| <img src="https://assets.odos.xyz/chains/bnb.png" width="50" height="50"><br>BNB | [`0x89b8AA89FDd0507a99d334CBe3C808fAFC7d850E`](https://bscscan.com/address/0x89b8aa89fdd0507a99d334cbe3c808fafc7d850e) |
| <img src="https://assets.odos.xyz/chains/fantom.png" width="50" height="50"><br>Fantom | [`0xD0c22A5435F4E8E5770C1fAFb5374015FC12F7cD`](https://ftmscan.com/address/0xd0c22a5435f4e8e5770c1fafb5374015fc12f7cd) |

## Audit

This contract was audited by [Zellic](https://zellic.io) in June 2023. A link to the report can be found in the [Zellic Publications GitHub Repository](https://github.com/Zellic/publications/blob/master/Odos%20-%20Zellic%20Audit%20Report.pdf). A copy of the report is included in this repository.
