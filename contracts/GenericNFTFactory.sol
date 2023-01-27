// SPDX-License-Identifier: MIT
pragma solidity ^0.8.12;

import "./GenericNFT.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
This is version 1 of the GenericNFTFactory contract
Please migrate from the previous version:
Main-net: 0x0dF2D689fb677EF95CcBd2766692b3f8c747B34B
Mumbai: 0x2FfbAe543566fdbC6438cE4628fE200028452748
The contracts admitted in the previous version will be automatically
admitted to the new version.
 */

contract GenericNFTFactory is Ownable {

    IERC20 public depositToken;
    uint256 public fee;
    uint256 public admissionFee;
    uint256 public editingFee;
    address[] private whitelist;

    // Associates each NFT contrac address to its user
    mapping(address => address) private nftContractToUser;
    // Associate the user address to the amount of registered contracts
    mapping(address => uint256) private contractNumberOfUsers;

    // Events
    event Approved(address indexed _owner,
                address indexed _spender,
                uint256 _value);

    event Deposit(address indexed _from,
                address indexed _to,
                uint256 _value);

    event FeeChanged(uint256 oldValue, 
                uint256 newValue);  

    event TokenChanged(address oldToken, 
                address newToken);  
            
    event AttributesUpdated(uint256 tokenId, 
                string oldURI,
                string newURI);  
        
    event NFTCreated(uint256 tokenId);  

    event NFTDeleted(uint256 tokenId);  


    modifier onlyWhitelist() {
        bool isInWhitelist = false;
        for(uint256 index=0; index < whitelist.length; index++) {
            if(whitelist[index] == msg.sender){
                isInWhitelist = true;
            }
        }
        
        // Owner can do what users in whitelist can do
        if(msg.sender == this.owner()){
            isInWhitelist = true;
        }

        require(isInWhitelist == true);
        _;
    }
   

    constructor(uint256 _admissionFee, uint256 _fee, uint256 _editingFee, address _depositToken) {
        admissionFee = _admissionFee;
        fee = _fee;
        editingFee = _editingFee;
        depositToken = IERC20(_depositToken);
    }

    /**
    * Whitelist management
    */

    /** 
    * Allows users to become part of the whitelist
    * nftContractAddress -> The GenericNFT contract address that the user wants to mint
    * _admissionFee -> The fee to pay for entering the whitelist
    */
    function applyToWhitelist(address nftContractAddress, uint256 _admissionFee) public payable {

        deposit(_admissionFee);  

        nftContractToUser[nftContractAddress] = msg.sender;
        contractNumberOfUsers[msg.sender] += 1;

        bool alreadyInWhitelist = checkWhitelistAdmission();
        if(!alreadyInWhitelist){
            whitelist.push(msg.sender);
        }
 
    }

    /**
    * Allows the user to check if it has been already admitted to
    * the whitelist 
    */
    function checkWhitelistAdmission() public returns (bool) {
        bool isInWhitelist = false;
        for(uint256 index=0; index < whitelist.length; index++) {
            if(whitelist[index] == msg.sender){
                isInWhitelist = true;
            }
        }
        return isInWhitelist;
    }

    /**
    Allows the owner to check if an address is  admitted to
    the whitelist 
    */
    function checkWhitelistAdmission(address addressToCheck) public onlyOwner returns (bool) {
        bool isInWhitelist = false;
        for(uint256 index=0; index < whitelist.length; index++) {
            if(whitelist[index] == addressToCheck){
                isInWhitelist = true;
            }
        }
        return isInWhitelist;
    }

    /**
    Allows the owner to retrieve an element from the whitelist
    */
    function getFromWhitelist(uint256 index) public onlyOwner returns (address) {
        require(index >= 0 && index < whitelist.length, "Index is not valid.");
        return whitelist[index];
    }

    /** 
    * Allows a user to claim back the ownership of the NFT contract
    * Then it removes the user from the whitelist
    * nftContractAddress -> The NFT contract address for which the user wants to claim the ownership
    */
    function claimOwnership(address nftContractAddress) public onlyWhitelist {

        require(contractNumberOfUsers[msg.sender] > 0, "The user has not applied for any contract.");
        require(nftContractToUser[nftContractAddress] == msg.sender, "Only the same user who applied for the contract can claim the ownership.");

        GenericNFT targetNFTContract = GenericNFT(nftContractAddress);
        targetNFTContract.transferOwnership(msg.sender);

        contractNumberOfUsers[msg.sender] -= 1;
        delete nftContractToUser[nftContractAddress];

        if(contractNumberOfUsers[msg.sender] == 0) {
            for(uint256 index=0; index < whitelist.length; index++){
                if(whitelist[index] == msg.sender){
                    _burn(index, whitelist);
                }
            }
        }
    }

    /** 
    * Adds the address passed as argument to the whitelist
    * newAddress -> The address to be added to the whitelist
    */
    function addToWhitelist(address newAddress) public onlyOwner {
        bool alreadyInWhitelist = checkWhitelistAdmission(newAddress);
        if(!alreadyInWhitelist){
            whitelist.push(newAddress);
        }
    }

    /** 
    * Removes the element at index specified as first argument
    * from the array specified as second argument
    * the array is the resized and the last item takes the 
    * position of the removed one
    * index -> The index of the element to be removed
    * array -> The array to manipulate
    */
    function _burn(uint256 index, address[] storage array) internal {
        require(index < array.length);
        array[index] = array[array.length-1];
        array.pop();
    }

    /** 
    * Removes the address specified as argument from the whitelist
    * addressToRemove -> the address to be removed
    */
    function removeFromWhitelist(address addressToRemove) public onlyOwner {
        for(uint256 index=0; index < whitelist.length; index++){
            if(whitelist[index] == addressToRemove){
                _burn(index, whitelist);
            }
        }
    }


    /**
    * Contract management
    */

    /**
    Allows the owner to check who is the applicant for the contract passed
    as argument
    */
    function getUserOfContract(address contractAddress) public onlyOwner returns (address) {
        return nftContractToUser[contractAddress];
    }

    /**
    Allows the owner to check how many contracts the user has applied for
    */
    function getContractsOfUser(address userAddress) public onlyOwner returns (uint256) {
        return contractNumberOfUsers[userAddress];
    }

    /** 
    Sets a new value to the fee for minting
    newFee -> The new value for the fee
    */
    function setFee(uint256 newFee) public onlyOwner {
        uint256 oldFee = fee;
        fee = newFee;
        emit FeeChanged(oldFee, fee);
    }

    /** 
    * Sets a new value to the fee for admission
    * newFee -> The new value for the fee
    */
    function setAdmissionFee(uint256 newFee) public onlyOwner {
        uint256 oldFee = admissionFee;
        admissionFee = newFee;
        emit FeeChanged(oldFee, admissionFee);
    }

    /** 
    * Sets a new value to the fee for editing
    * newFee -> The new value for the fee
    */
    function setEditingFee(uint256 newFee) public onlyOwner {
        uint256 oldFee = editingFee;
        editingFee = newFee;
        emit FeeChanged(oldFee, editingFee);
    }

    /** 
    * Sets a new token to be used for deposit
    * tokenAddress -> The address of the new token to be used for fees
    */
    function setDepositToken(address tokenAddress) public onlyOwner {
        address oldAddress = address(depositToken);
        depositToken = IERC20(tokenAddress);
        emit TokenChanged(oldAddress, address(depositToken));
    }

    /** 
    * Allows users to deposit the amount of depositToken
    * amount -> The amount to be deposited
    */
    function deposit(uint256 amount) public {
        require(amount > 0, "Amount must be more than 0");
        
        uint256 allowance = depositToken.allowance(msg.sender, address(this));
        require(allowance >= amount, "Check the token allowance");
        
        bool deposited = depositToken.transferFrom(msg.sender, address(this), amount);
        require(deposited);

        emit Deposit(msg.sender, address(this), amount);
    }


    /** 
    * Transfers the contract balance of the depost token to the owner
    */
    function withdraw() public onlyOwner {        
        uint256 balance = depositToken.balanceOf(address(this));
        depositToken.transfer(msg.sender, balance);
    }

    /* 
    * Transfers the contract balance of the base currency to the owner
    */
    function withdrawBaseCurrency() public onlyOwner {        
        uint256 balance = address(this).balance;
        depositToken.transfer(msg.sender, balance);
    }


    /**
    * NFT Creation
    */

    /** 
    * Allows users in whitelist to create a new token for the contract
    * passed as argument
    * recipient -> The address that to which the token will be assigned
    * nftContractAddress -> The address to be used for the NFT contract
    * tokenURI -> The token URI to be provided by the user
    * _fee -> the fee to be paid for minting 
    */ 
    function mintNFTFromAddress(address recipient, address nftContractAddress, string memory tokenURI, uint256 _fee) public onlyWhitelist returns (uint256) {
        require(_fee >= fee, "Minting fee is higher, check the fee value");
        deposit(_fee);        

        require(nftContractToUser[nftContractAddress] == msg.sender, "Only the same user who applied for the contract can mint NFTs.");
        
        GenericNFT nftContract = GenericNFT(nftContractAddress);
        nftContract.unlock();
        uint256 tokenId = nftContract.mintNFT(recipient, tokenURI);
        emit NFTCreated(tokenId);
        nftContract.lock();

        return tokenId;
    }

    
    /** 
    * Allows the owner to change the token URI for the asset with the given token ID
    * tokenId -> The id of the token to be updated
    * nftContractAddress -> The address of the token address to be used
    * newTokenURI -> New URI to be applied
    * _editingFee -> The fee to be paid for editing
    */
    function changeTokenURI(address nftContractAddress, uint256 tokenId, string memory newTokenURI, uint256 _editingFee) public onlyWhitelist {
        
        require(_editingFee >= editingFee, "Editing fee is higher, check the fee value");
        deposit(_editingFee);   

        require(nftContractToUser[nftContractAddress] == msg.sender, "Only the same user who applied for the contract can change URI.");
        
        GenericNFT nftContract = GenericNFT(nftContractAddress);
        string memory oldURI = nftContract.tokenURI(tokenId);
        nftContract.changeAttributes(tokenId, newTokenURI);
        
        emit AttributesUpdated(tokenId, oldURI, newTokenURI);
    }


    /** 
    * Allows the owner to remove the NFT
    * tokenId -> The id of the token to remove
    * nftContractAddress -> The address of the token address to be used
    * _editingFee -> The fee to be paid to remove the NFT
    */
    function deleteNFT(address nftContractAddress, uint256 tokenId, uint256 _editingFee) public onlyWhitelist {

        require(_editingFee >= editingFee, "Editing fee is higher, check the fee value");
        deposit(_editingFee);   

        require(nftContractToUser[nftContractAddress] == msg.sender, "Only the same user who applied for the contract can delete a NFT.");

        GenericNFT nftContract = GenericNFT(nftContractAddress);
        nftContract.unlock();
        nftContract.destroy(tokenId);
        nftContract.lock();
        emit NFTDeleted(tokenId);
    }

}