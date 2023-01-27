// SPDX-License-Identifier: MIT
pragma solidity ^0.8.12;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract MockUSDC is ERC20 {
    constructor() public ERC20("Mock USDC", "USDC"){
        _mint(msg.sender, 10000000000000000000000); // 10k USDT
    }
}