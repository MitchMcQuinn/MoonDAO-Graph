# Graph Architecture

> Note: The following node properties are derived from the safe.global API unless otherwise specified.

## Nodes

### - Address
#### address: string // API: masterCopy
#### threshold: int // API: threshold

##### For each owner, merge an address node, match it, and then create a relationship HAS_SIGNER.

### - Transaction
#### submissionDate: string // API: submissionDate
#### executionDate: string // API: executionDate
#### transactionHash: string // API: transactionHash
#### safeTxHash: string // API: safeTxHash
#### nonce: int // API: nonce
#### isExecuted: boolean // API: isExecuted
#### isSuccessful: boolean // API: isSuccessful
#### ethGasPrice: int // API: gasPrice
#### maxFeePerGas: int // API: maxFeePerGas
#### maxPriorityFeePerGas: int // API: maxPriorityFeePerGas
#### gasUsed: int // API: gasUsed
#### fee: int // API: fee
#### origin: string // API: origin
#### method: array // API: dataDecoded.method (get an array of all the methods called in the transaction)

##### For each to, proposer, or executor address, create an address node, match it, and then create the appropriate relationships with the transaction.

### - Transfer 
#### type: string // API: type
#### transactionHash: string // API: transactionHash
#### to: Address // API: to
#### value: int // API: value

##### For each to, or token_address, create an address node, match it, and then create the appropriate relationships with the transfer.

## Relationships

### - HAS_TRANSFER
#### From: Transaction
#### To: Transfer

### - OWNS_ADDRESS
#### From: Person
#### To: Address

### - HAS_SIGNER
#### From: Address
#### To: Address

### - HAS_TRANSACTION
#### From: Address
#### To: Transaction

### - HAS_ASSET
#### From: Address
#### To: Address
#### type: (ERC20, ERC721, ERC1155...)
#### amount: int

### - OF_ASSET
#### From: Transfer
#### To: Address

### - IS_FROM
#### From: Transaction
#### To: Address

### - SENT_TO
#### From: Transfer
#### To: Address

### - INTERACTED_WITH
#### From: Transaction
#### To: Address
