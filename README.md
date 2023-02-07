# GenericNFTFactory

This contract allows to mint NFTs using the factory contrac as a proxy.
In order to make use of the factory the steps below can be followed:

1. Create a NFT contract that inherits from GenericNFT.sol
2. Deploy the NFT contract
3. Apply to the factory indicating which contract should be used
4. Transfer the ownership of the NFT ontract to the factory contract. This step is needed to make the factory able to operate on the NFT contract. The ownership can be claimed back at any point in time using the `claimOwnership` function
5. Mint new NFTs using the `mintNFTFromAddress` function, indicating which NFT contract address you want to make use of

## Notes
When future versions of the contract will be deployed, the current user will be enabled automatically, without the need to reapply. 
The user will have to update the address used to operate on the NFTs. The factory owner will take care of migrating existing contract manually. In future versions this will be automated.


Now the users can check the latest version using the `getLatestVersion` function. The contracts can be locked or unlocked through the `lockContract` and `unlockContract` functions.

## Important
Make sure to use the right factory address:
  * Polygon Mainnet: 0x7F5f93C45fcd92736C22C3738b7D18B0895A7c69
  * Polygon Testnet: 0xB988eF8769135feb746563e4a983C64FA7D85924

Other versions of the factory have been deployed in the past for testing purposes. Please ignore those versions and make sure to use only the latest one.
Check this page to keep up to date about the new releases.

## License
Users are allowed to make use of the code to learn how to use it and for testing purposes. For any commercial use the latest version of the contract needs to be used.
For what is not specified, the conditions of the GPL-3.0 license apply.

## Copyright 
&copy;2023 gunkan-sake :sushi: (Yes, I know they are nighiri, unfortunately there is no emoji for gunkan)

## Older versions
* Polygon Mainnet: 
  * 0xd16b824f0aF723971528272dd09EC234B134ad55
* Polygon Testnet: 
  * 0x7F5f93C45fcd92736C22C3738b7D18B0895A7c69
