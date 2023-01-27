// SPDX-License-Identifier: MIT
pragma solidity ^0.8.12;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/utils/Counters.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract GenericNFT is ERC721URIStorage, Ownable {
    using Counters for Counters.Counter;
    Counters.Counter private _tokenIds;
    bool public locked;

    constructor(string memory name, string memory symbol)
        ERC721(name, symbol) {
            locked = true;
    }

    function changeAttributes(uint256 tokenId, string memory newTokenURI) public onlyOwner {
        _setTokenURI(tokenId, newTokenURI);
    }

    function destroy(uint256 tokenId) public onlyOwner {
        _burn(tokenId);
    }

    function lock() public onlyOwner {
        locked = true;
    }

    function unlock() public onlyOwner {
        locked = false;
    }

    function _beforeTokenTransfer(
        address from,
        address to,
        uint256,
        uint256 batchSize
    ) internal override {
        require(!locked, "Cannot transfer - currently locked");
    }

    function mintNFT(address recipient, string memory tokenURI)
        public
        virtual
        payable
        returns (uint256)
    {
        _tokenIds.increment();

        uint256 newItemId = _tokenIds.current();
        _mint(recipient, newItemId);
        _setTokenURI(newItemId, tokenURI);

        return newItemId;
    }
}