// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title VeritasEscrow
 * @notice Simple escrow for claim settlements (Base / any EVM chain)
 * @dev This is a basic version. In production add AccessControl, ReentrancyGuard, etc.
 */
contract VeritasEscrow {
    address public owner;

    struct Deposit {
        address payer;
        address payee;
        uint256 amount;
        bool released;
        bool refunded;
        string claimId; // external reference to Veritas claim
    }

    mapping(bytes32 => Deposit) public deposits;
    mapping(string => bytes32) public claimToDeposit;

    event Deposited(bytes32 indexed depositId, string claimId, address payer, address payee, uint256 amount);
    event Released(bytes32 indexed depositId, address payee, uint256 amount);
    event Refunded(bytes32 indexed depositId, address payer, uint256 amount);

    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    function deposit(string calldata claimId, address payee) external payable returns (bytes32) {
        require(msg.value > 0, "Amount must be > 0");
        require(payee != address(0), "Invalid payee");
        require(claimToDeposit[claimId] == bytes32(0), "Claim already has deposit");

        bytes32 depositId = keccak256(abi.encodePacked(claimId, msg.sender, payee, block.timestamp));

        deposits[depositId] = Deposit({
            payer: msg.sender,
            payee: payee,
            amount: msg.value,
            released: false,
            refunded: false,
            claimId: claimId
        });

        claimToDeposit[claimId] = depositId;

        emit Deposited(depositId, claimId, msg.sender, payee, msg.value);
        return depositId;
    }

    function release(bytes32 depositId) external onlyOwner {
        Deposit storage d = deposits[depositId];
        require(d.amount > 0, "Deposit not found");
        require(!d.released && !d.refunded, "Already settled");

        d.released = true;
        (bool success, ) = d.payee.call{value: d.amount}("");
        require(success, "Transfer failed");

        emit Released(depositId, d.payee, d.amount);
    }

    function refund(bytes32 depositId) external onlyOwner {
        Deposit storage d = deposits[depositId];
        require(d.amount > 0, "Deposit not found");
        require(!d.released && !d.refunded, "Already settled");

        d.refunded = true;
        (bool success, ) = d.payer.call{value: d.amount}("");
        require(success, "Transfer failed");

        emit Refunded(depositId, d.payer, d.amount);
    }

    function getDeposit(bytes32 depositId) external view returns (Deposit memory) {
        return deposits[depositId];
    }
}