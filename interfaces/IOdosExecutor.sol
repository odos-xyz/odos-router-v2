// SPDX-License-Identifier: UNLICENSED

pragma solidity 0.8.8;

interface IOdosExecutor {
  function executePath (
    bytes calldata bytecode,
    uint256[] memory inputAmount,
    address msgSender
  ) external payable;
}
