# After receiving a safe address as input, the following process is used to ingest the data into the graph:

## 1) Ingest the main safe node:
Merge an Address node into the graph for the main safe address with the following properties:
address: string // API: address
threshold: int // API: threshold
owners: array (of addresses)// API: owners

## 2) Ingest the multisig owners (aka. signers)
i) For each address in the owners array, merge in an Address node, with the following property:
address: string

ii) Create a relationship HAS_SIGNER between the safe address and each owner address.

## 3) Ingest the transactions
i) For each transaction in the transactions array, merge in a Transaction node with the following properties:
submissionDate: string // API: submissionDate
executionDate: string // API: executionDate
transactionHash: string // API: transactionHash
safeTxHash: string // API: safeTxHash
nonce: int // API: nonce
isExecuted: boolean // API: isExecuted
isSuccessful: boolean // API: isSuccessful
ethGasPrice: int // API: gasPrice
maxFeePerGas: int // API: maxFeePerGas
maxPriorityFeePerGas: int // API: maxPriorityFeePerGas
gasUsed: int // API: gasUsed
fee: int // API: fee
origin: string // API: origin
methods: array // API: dataDecoded.method (get an array of all the methods called in the transaction)
transfers: array (of transactionHash) // API: transfers.transactionHash

ii) Create a relationship HAS_TRANSACTION between the safe address and each transaction.

## 4) Ingest the transfers
i) For each transactionHash in the transfers array, merge in a Transfer node with the following properties:
transactionHash: string // API: transactionHash
type: string // API: type
from: Address // API: from // Represents the safe
to: Address // API: to // Represents the recipient
value: int // API: value
tokenInfo.symbol: string // API: tokenInfo.symbol
tokenInfo.decimals: Address // API: tokenInfo.

ii) Create a relationship HAS_TRANSFER between the transaction and the transfer.

iii) For each transfer, merge in an Address node with the following properties:
address: string // API: transfers.to

iv) Create a relationship SENT_TO between the transfer and the address.

v) For each transfer, merge in an Address node with the following properties:
address: string // API: transfers.from

vi) Create a relationship IS_FROM between the transfer and the address.

vii) For each transfer, merge in an Address node with the following properties:
address: string // API: transfers.proposer

viii) Create a relationship PROPOSED_BY between the transfer and the address.