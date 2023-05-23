// SPDX-License-Identifier: MIT
pragma solidity 0.8.8;

import "OpenZeppelin/openzeppelin-contracts@4.8.3/contracts/token/ERC20/IERC20.sol";
import "../interfaces/IWETH.sol";

contract OdosWETHExecutor {

	//IWETH constant WETH = IWETH(0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2);
	IWETH public immutable WETH;

	constructor(address _weth) {
	    WETH = IWETH(_weth);
	}
	receive() external payable { }

	function executePath (
	    bytes calldata bytecode,
	    uint256[] memory inputAmounts,
	    address msgSender
	) 
		external payable
	{
	  if (uint8(bytecode[0]) == 1) {
        WETH.deposit{value: inputAmounts[0]}();
        WETH.transfer(msg.sender, inputAmounts[0]);
      }
      else {
        WETH.withdraw(inputAmounts[0]);
        payable(msg.sender).transfer(inputAmounts[0]);
      }
	}
}