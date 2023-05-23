// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

interface IEIP712 {

	/// @notice Returns the domain separator for the current chain.
    /// @dev Uses cached version if chainid and address are unchanged from construction.
    function DOMAIN_SEPARATOR() external view returns (bytes32);
}
