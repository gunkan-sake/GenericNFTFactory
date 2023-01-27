from brownie import GenericNFTFactory, accounts, exceptions, network
from scripts.helpful_scripts import get_account, deploy_mocks, LOCAL_BLOCKCHAIN_ENVIRONMENTS
from web3 import Web3
from web3 import eth
from scripts.deploy import deploy_generic_factory

import pytest

TEST_URI = "ipfs://bafyreibi5ogzlukr7yuknism6thyvuukmppvnbjk2llt7algvj2pliqs5a/metadata.json"
TEST_URI2 = "ipfs://bafyreibi5ogzlukr7yuknism6thyvuukmppvnbjk2llt7algvj2pliqs5b/metadata.json"
KEPT_BALANCE = Web3.toWei(100, "ether")
ADMISSION_FEE = Web3.toWei(50, "ether")
MINTING_FEE = Web3.toWei(29, "ether")
EDITING_FEE = Web3.toWei(23, "ether")

def test_deploy():
    """
    Testing that the factory can be deployed properly and
    attributes are initialized as expected
    """
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only in local environment")

    factory_owner = get_account(index=1)
    token_owner = get_account(index=2)

    mock_usdt, mock_usdc, mock_nft = deploy_mocks(
        account=token_owner)

    factory = deploy_generic_factory(
        factory_owner,
        ADMISSION_FEE,
        MINTING_FEE,
        EDITING_FEE,
        mock_usdt.address
    )
    
    expected_owner = factory_owner

    assert ADMISSION_FEE == factory.admissionFee()
    assert MINTING_FEE == factory.fee()
    assert EDITING_FEE == factory.editingFee()
    assert mock_usdt.address == factory.depositToken()
    assert expected_owner == factory.owner()



def test_add_to_whitelist():
    """
    Testing that addresses can be added to the whitelist 
    and that only the owner can do so
    """
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
            pytest.skip("Only in local environment")
    
    token_owner = get_account(index=1)
    mock_usdt, mock_usdc, mock_nft = deploy_mocks(account=token_owner)
    
    factory_owner = get_account(index=2)
    factory = deploy_generic_factory(
        factory_owner,
        ADMISSION_FEE,
        MINTING_FEE,
        EDITING_FEE,
        mock_usdt.address
    )

    whitelisted = get_account(index=3)

    factory.addToWhitelist(whitelisted, {'from': factory_owner})
    returned_whitelisted = factory.getFromWhitelist.call(0, {'from': factory_owner})

    assert returned_whitelisted == whitelisted

    not_owner = get_account(index=4)
    whitelisted_2 = get_account(index=5)
    with pytest.raises(Exception):
        factory.addToWhitelist(whitelisted_2, {'from': not_owner})



def test_remove_from_whitelist():
    """
    Testing that addresses can be removed from the whitelist 
    and that only the owner can do so
    """
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
            pytest.skip("Only in local environment")
    
    token_owner = get_account(index=1)
    mock_usdt, mock_usdc, mock_nft = deploy_mocks(account=token_owner)
    
    factory_owner = get_account(index=2)
    factory = deploy_generic_factory(
        factory_owner,
        ADMISSION_FEE,
        MINTING_FEE,
        EDITING_FEE,
        mock_usdt.address
    )

    whitelisted_1 = get_account(index=3)
    factory.addToWhitelist(whitelisted_1, {'from': factory_owner})
    returned_whitelisted_1 = factory.getFromWhitelist.call(0, {'from': factory_owner})
    assert returned_whitelisted_1 == whitelisted_1

    whitelisted_2 = get_account(index=4)
    factory.addToWhitelist(whitelisted_2, {'from': factory_owner})
    returned_whitelisted_2 = factory.getFromWhitelist.call(1, {'from': factory_owner})
    assert returned_whitelisted_2 == whitelisted_2

    factory.removeFromWhitelist(whitelisted_1, {'from': factory_owner})
    # check that now the address that was in position 1 went to position 0
    new_whitelisted_1 = factory.getFromWhitelist.call(0, {'from': factory_owner})
    assert new_whitelisted_1 == whitelisted_2

    # check that the size of the whitelist array was reduced
    with pytest.raises(Exception):
        new_whitelisted_2 = factory.getFromWhitelist.call(1, {'from': factory_owner})



def test_set_fee():
    """
    Testing that the deposit / minting fee can be changed properly 
    """
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
            pytest.skip("Only in local environment")
    
    token_owner = get_account(index=1)
    mock_usdt, mock_usdc, mock_nft = deploy_mocks(account=token_owner)
    
    factory_owner = get_account(index=2)
    factory = deploy_generic_factory(
        factory_owner,
        ADMISSION_FEE,
        MINTING_FEE,
        EDITING_FEE,
        mock_usdt.address
    )

    assert MINTING_FEE == factory.fee()

    new_fee = Web3.toWei(89, "ether")
    factory.setFee(new_fee, {'from': factory_owner})

    assert factory.fee() == new_fee



def test_set_deposit_token():
    """
    Testing that the deposit token can be changed properly
    """
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
            pytest.skip("Only in local environment")
    
    token_owner = get_account(index=1)
    mock_usdt, mock_usdc, mock_nft = deploy_mocks(account=token_owner)
    
    factory_owner = get_account(index=2)
    factory = deploy_generic_factory(
        factory_owner,
        ADMISSION_FEE,
        MINTING_FEE,
        EDITING_FEE,
        mock_usdt.address
    )

    assert factory.depositToken() == mock_usdt

    factory.setDepositToken(mock_usdc.address, {'from': factory_owner})
    assert factory.depositToken() == mock_usdc



def test_deposit():
    """
    Testing that users can deposit to the factory contract
    - deploy factory and mocks
    - transfer mock_usdt to users
    - approve spending for user
    - user deposits
    - check that factory balance equals the deposited amount
    """
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
            pytest.skip("Only in local environment")
    
    token_owner = get_account(index=1)
    mock_usdt, mock_usdc, mock_nft = deploy_mocks(account=token_owner)
    
    factory_owner = get_account(index=2)
    factory = deploy_generic_factory(
        factory_owner,
        ADMISSION_FEE,
        MINTING_FEE,
        EDITING_FEE,
        mock_usdt.address
    )

    factory_user = get_account(index=3)
    KEPT_BALANCE = Web3.toWei(100, "ether")
    mock_usdt.transfer(
        factory_user.address, mock_usdt.totalSupply() - KEPT_BALANCE, {"from": token_owner}
    )

    amount = Web3.toWei(100, "ether")
    fc_allowance = mock_usdt.allowance(factory_user.address, factory.address, {"from": factory_user})
    assert fc_allowance == 0

    mock_usdt.approve(factory.address, amount, {"from": factory_user})
    fc_allowance = mock_usdt.allowance(factory_user.address, factory.address, {"from": factory_user})
    assert fc_allowance == amount

    factory.deposit(amount, {"from": factory_user})

    balance_fc = mock_usdt.balanceOf(factory.address, {"from": factory_owner})
    assert  balance_fc == amount



def test_withdraw():
    """
    Testing that the owner can withdraw the token balance of the contract
    - run all the steps for the test_deposit function
    - the factory owner calls the withdraw function
    - check that the deposited amount is now in the balance of the factory owner
    """
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
            pytest.skip("Only in local environment")
    
    token_owner = get_account(index=1)
    mock_usdt, mock_usdc, mock_nft = deploy_mocks(account=token_owner)
    
    factory_owner = get_account(index=2)
    factory = deploy_generic_factory(
        factory_owner,
        ADMISSION_FEE,
        MINTING_FEE,
        EDITING_FEE,
        mock_usdt.address
    )

    factory_user = get_account(index=3)
    KEPT_BALANCE = Web3.toWei(100, "ether")
    mock_usdt.transfer(
        factory_user.address, mock_usdt.totalSupply() - KEPT_BALANCE, {"from": token_owner}
    )

    amount = Web3.toWei(100, "ether")
    fc_allowance = mock_usdt.allowance(factory_user.address, factory.address, {"from": factory_user})
    assert fc_allowance == 0

    mock_usdt.approve(factory.address, amount, {"from": factory_user})
    fc_allowance = mock_usdt.allowance(factory_user.address, factory.address, {"from": factory_user})
    assert fc_allowance == amount

    factory.deposit(amount, {"from": factory_user})

    initial_fc_balance = mock_usdt.balanceOf(factory.address, {"from": factory_owner})
    assert initial_fc_balance == amount

    # now withdraw
    initial_fo_balance = mock_usdt.balanceOf(factory_owner.address, {"from": factory_owner})
    factory.withdraw({"from": factory_owner})

    final_fo_balance = mock_usdt.balanceOf(factory_owner.address, {"from": factory_owner})
    assert final_fo_balance == initial_fo_balance + amount

    final_fc_balance = mock_usdt.balanceOf(factory.address, {"from": factory_owner})
    assert final_fc_balance == initial_fc_balance - amount

    # check that other users cannot withdraw
    with pytest.raises(Exception):
        factory.withdraw({"from": factory_user})

    

def test_mint_nft():
    """
    Testing that the NFT minting process works correctly
    - deploy factory and mocks
    - create user account
    - factory onwer adds user account to whitelist
    - mock_usdt are transferred to the user account
    - the user account calls the mintNFT function
    """
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
            pytest.skip("Only in local environment")
            
    nft_user = get_account(index=1)
    factory_owner = get_account(index=2)

    mock_usdt, mock_usdc, mock_nft = deploy_mocks(account=nft_user)

    factory = deploy_generic_factory(
        factory_owner,
        ADMISSION_FEE,
        MINTING_FEE,
        EDITING_FEE,
        mock_usdt.address
    )

    admission_fee = factory.admissionFee({'from': nft_user})

    tx = mock_usdt.approve(factory.address, admission_fee, {"from": nft_user})
    tx.wait(1)

    tx = factory.applyToWhitelist(
        mock_nft.address,
        admission_fee, 
        {"from": nft_user})
    tx.wait(1)

    # Transfer ownership of NFT contract to factory
    # this allows the factory to mint the NFTs
    owner_mock_nft = mock_nft.owner.call()
    assert owner_mock_nft == nft_user

    tx = mock_nft.transferOwnership(factory.address, {'from': nft_user})
    tx.wait(1)

    owner_mock_nft = mock_nft.owner.call()
    assert owner_mock_nft == factory.address

    fee = factory.fee({'from': nft_user})

    # Approve spending
    tx = mock_usdt.approve(factory.address, fee, {"from": nft_user})
    tx.wait(1)

    # Mint
    initial_fu_balance = mock_usdt.balanceOf(nft_user.address, {"from": nft_user})
    initial_fc_balance = mock_usdt.balanceOf(factory.address, {"from": factory_owner})

    test_uri = TEST_URI
    tx = factory.mintNFTFromAddress(
        nft_user.address,
        mock_nft.address,
        test_uri,
        fee, 
        {"from": nft_user})
    tx.wait(1)

    # Check that balances are updated correctly
    final_fu_balance = mock_usdt.balanceOf(nft_user.address, {"from": nft_user})
    final_fc_balance = mock_usdt.balanceOf(factory.address, {"from": factory_owner})

    assert final_fu_balance == initial_fu_balance - fee
    assert final_fc_balance == initial_fc_balance + fee

    # And that the user received a nft token
    assert mock_nft.ownerOf(1) == nft_user.address



def test_changeTokenURI():
    """
    Testing that the owner can change the token URI properly.
    Repeats all the steps of test_minting then tries to change the URI
    """
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
            pytest.skip("Only in local environment")
            
    nft_user = get_account(index=1)
    factory_owner = get_account(index=2)

    mock_usdt, mock_usdc, mock_nft = deploy_mocks(account=nft_user)

    factory = deploy_generic_factory(
        factory_owner,
        ADMISSION_FEE,
        MINTING_FEE,
        EDITING_FEE,
        mock_usdt.address
    )

    admission_fee = factory.admissionFee({'from': nft_user})

    tx = mock_usdt.approve(factory.address, admission_fee, {"from": nft_user})
    tx.wait(1)

    tx = factory.applyToWhitelist(
        mock_nft.address,
        admission_fee, 
        {"from": nft_user})
    tx.wait(1)

    # Transfer ownership of NFT contract to factory
    # this allows the factory to mint the NFTs
    owner_mock_nft = mock_nft.owner.call()
    assert owner_mock_nft == nft_user

    tx = mock_nft.transferOwnership(factory.address, {'from': nft_user})
    tx.wait(1)

    owner_mock_nft = mock_nft.owner.call()
    assert owner_mock_nft == factory.address

    fee = factory.fee({'from': nft_user})

    # Approve spending
    tx = mock_usdt.approve(factory.address, fee, {"from": nft_user})
    tx.wait(1)

    # Mint
    test_uri = TEST_URI
    tx = factory.mintNFTFromAddress(
        nft_user.address,
        mock_nft.address,
        test_uri,
        fee, 
        {"from": nft_user})
    tx.wait(1)

    assert mock_nft.tokenURI(1, {'from': factory_owner}) == test_uri

    # Change URI
    editing_fee = factory.editingFee({'from': nft_user})
    tx = mock_usdt.approve(factory.address, editing_fee, {"from": nft_user})
    tx.wait(1)

    new_test_uri = TEST_URI2
    factory.changeTokenURI(
        mock_nft.address,
        1, 
        new_test_uri, 
        editing_fee,
        {'from': nft_user})

    assert mock_nft.tokenURI(1, {'from': factory_owner}) == new_test_uri



def test_deleteNFT():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
            pytest.skip("Only in local environment")
            
    nft_user = get_account(index=1)
    factory_owner = get_account(index=2)

    mock_usdt, mock_usdc, mock_nft = deploy_mocks(account=nft_user)

    factory = deploy_generic_factory(
        factory_owner,
        ADMISSION_FEE,
        MINTING_FEE,
        EDITING_FEE,
        mock_usdt.address
    )

    admission_fee = factory.admissionFee({'from': nft_user})

    tx = mock_usdt.approve(factory.address, admission_fee, {"from": nft_user})
    tx.wait(1)

    tx = factory.applyToWhitelist(
        mock_nft.address,
        admission_fee, 
        {"from": nft_user})
    tx.wait(1)

    # Transfer ownership of NFT contract to factory
    # this allows the factory to mint the NFTs
    owner_mock_nft = mock_nft.owner.call()
    assert owner_mock_nft == nft_user

    tx = mock_nft.transferOwnership(factory.address, {'from': nft_user})
    tx.wait(1)

    owner_mock_nft = mock_nft.owner.call()
    assert owner_mock_nft == factory.address

    fee = factory.fee({'from': nft_user})

    # Approve spending
    tx = mock_usdt.approve(factory.address, fee, {"from": nft_user})
    tx.wait(1)

    # Mint
    test_uri = TEST_URI
    tx = factory.mintNFTFromAddress(
        nft_user.address,
        mock_nft.address,
        test_uri,
        fee, 
        {"from": nft_user})
    tx.wait(1)

    assert mock_nft.tokenURI(1, {'from': factory_owner}) == test_uri

    # Change URI
    editing_fee = factory.editingFee({'from': nft_user})
    tx = mock_usdt.approve(factory.address, editing_fee, {"from": nft_user})
    tx.wait(1)

    # Delete
    factory.deleteNFT(
        mock_nft.address,
        1,
        editing_fee,
        {"from": nft_user}
        )

    assert mock_nft.balanceOf(nft_user) == 0



def test_apply_to_whitelist():
    """
    Testing that a user can apply to the whitelist correctly
    """
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only in local environment")

    factory_user = get_account(index=1)
    mock_usdt, mock_usdc, mock_nft = deploy_mocks(account=factory_user)
    
    factory_owner = get_account(index=2)

    factory = deploy_generic_factory(
        factory_owner,
        ADMISSION_FEE,
        MINTING_FEE,
        EDITING_FEE,
        mock_usdt.address
    )

    initial_balance = mock_usdt.balanceOf(factory.address)

    admitted = factory.checkWhitelistAdmission.call({"from": factory_user})
    assert not admitted

    admission_fee = factory.admissionFee({'from': factory_user})

    tx = mock_usdt.approve(factory.address, admission_fee, {"from": factory_user})
    tx.wait(1)

    tx = factory.applyToWhitelist(
        mock_nft.address,
        admission_fee, 
        {"from": factory_user})
    tx.wait(1)

    admitted = factory.checkWhitelistAdmission.call({"from": factory_user})
    assert admitted

    assert mock_usdt.balanceOf(factory.address) == initial_balance + admission_fee

    # Check that lower fees are not accepted
    poor_factory_user = get_account(index=4)
    
    insufficient_admission_fee = Web3.toWei(0.5, "ether")

    admitted = factory.checkWhitelistAdmission.call({"from": poor_factory_user})
    assert not admitted

    # check that other users cannot withdraw
    with pytest.raises(Exception):
        tx = factory.applyToWhitelist(
            mock_nft.address,
            insufficient_admission_fee, 
            {"from": factory_user})
        tx.wait(1)


    admitted = factory.checkWhitelistAdmission.call({"from": poor_factory_user})
    assert not admitted



def test_claim_ownership():
    """
    Testing that someone who applied to the whitelist and granted
    ownership to the factory contract should be able to call the
    function to get the ownership back
    """
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only in local environment")

    factory_user = get_account(index=1)
    mock_usdt, mock_usdc, mock_nft = deploy_mocks(account=factory_user)
    _, _, mock_nft2 = deploy_mocks(account=factory_user)

    factory_owner = get_account(index=2)

    factory = deploy_generic_factory(
        factory_owner,
        ADMISSION_FEE,
        MINTING_FEE,
        EDITING_FEE,
        mock_usdt.address
    )

    initial_balance = mock_usdt.balanceOf(factory.address)

    admitted = factory.checkWhitelistAdmission.call({"from": factory_user})
    assert not admitted

    admission_fee = factory.admissionFee({'from': factory_user})

    tx = mock_usdt.approve(factory.address, 2*admission_fee, {"from": factory_user})
    tx.wait(1)

    tx = factory.applyToWhitelist(
        mock_nft.address,
        admission_fee, 
        {"from": factory_user})
    tx.wait(1)

    tx = factory.applyToWhitelist(
        mock_nft2.address,
        admission_fee, 
        {"from": factory_user})
    tx.wait(1)

    assert factory.getContractsOfUser.call(factory_user, {"from": factory_owner}) == 2

    admitted = factory.checkWhitelistAdmission.call({"from": factory_user})
    assert admitted

    assert mock_usdt.balanceOf(factory.address) == initial_balance + 2*admission_fee

    owner_mock_nft = mock_nft.owner.call()
    assert owner_mock_nft == factory_user

    tx = mock_nft.transferOwnership(factory.address, {'from': factory_user})
    tx.wait(1)
    tx = mock_nft2.transferOwnership(factory.address, {'from': factory_user})
    tx.wait(1)

    owner_mock_nft = mock_nft.owner.call()
    assert owner_mock_nft == factory.address

    # Check that the user must be correct
    with pytest.raises(Exception):
        another_user = get_account(index=3)
        factory.claimOwnership(
            mock_nft.address,
            {'from': another_user})

    # Now the user wants the ownership back
    factory.claimOwnership(
        mock_nft.address,
        {'from': factory_user})

    owner_mock_nft = mock_nft.owner.call()
    assert owner_mock_nft == factory_user

    assert factory.getContractsOfUser.call(factory_user, {"from": factory_owner}) == 1

    admitted = factory.checkWhitelistAdmission.call({"from": factory_user})
    assert admitted

    factory.claimOwnership(
        mock_nft2.address,
        {'from': factory_user})

    owner_mock_nft2 = mock_nft2.owner.call()
    assert owner_mock_nft2 == factory_user

    assert factory.getContractsOfUser.call(factory_user, {"from": factory_owner}) == 0

    admitted = factory.checkWhitelistAdmission.call({"from": factory_user})
    assert not admitted

