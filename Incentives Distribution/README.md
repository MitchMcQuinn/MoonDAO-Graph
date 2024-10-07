# Quarterly Reward Pool Calculation Script
Overview
This script is designed to calculate the total quarterly reward pools for distribution. It determines the amount of ETH and MOONEY tokens to be distributed each quarter based on predefined logic and the current state of the treasury.

## Logic for Calculating the Reward Pools
### Total Quarterly Reward Calculation
The total amount of rewards each quarter is calculated as follows:
ETH Reward: 5% of the liquid non-MOONEY assets (NMA) (e.g., ETH, DAI, and other stablecoins) is allocated for distribution, paid in the form of ETH. Assets with fluctuating prices will be valued at midnight of the last day of the quarter.
vMOONEY Reward: A geometric series of MOONEY tokens will be released each quarter, decreasing by 5% each time. The distribution schedule is as follows:
Q4 2022: 15,000,000 MOONEY
Q1 2023: 14,250,000 MOONEY
Q2 2023: 13,537,500 MOONEY
Q3 2023: 12,860,625 MOONEY
And so on, infinitely decreasing by a factor of 0.95 every quarter.
Community Rewards: Of the total vMOONEY reward, 10% will automatically go to a Contributor Circle for the community. Throughout the quarter, anyone in the community can post contributions that can be accepted by any of the top five contributors from the last quarter.

## Approach
The script performs the following steps:
1. Define Static Variables
    INITIAL_MOONEY_GEOMETRIC_RELEASE: 15,000,000
    TOTAL_ASSET_PERCENT_RELEASED_QUARTERLY: 0.05 (5%)
    QUARTER_END_DATE: 30/09/2024
    TREASURY_SAFE_ETH: 0xce4a1E86a5c47CD677338f53DA22A91d85cab2c9
2. Calculate Dynamic Variables
current_geometric_cycle: Calculated by counting the number of quarters since the end of Q4 2022.
total_mooney_to_distribute: The total amount of MOONEY to distribute this quarter, determined by the current geometric cycle.
total_eth_to_distribute: The sum of the value of all tokens in the treasury on the QUARTER_END_DATE. If the QUARTER_END_DATE has not yet occurred, use current rates.
community_rewards: 10% of the value of total_mooney_to_distribute.

3. Logging and Output
The script will log and return all the calculated variables to confirm the output:
current_geometric_cycle
total_mooney_to_distribute
total_eth_to_distribute
community_rewards

Requirements
Python 3.x
Safe.Global API Access: To retrieve the treasury assets and balances.
Etherscan API Access: To get current token prices and other on-chain data.

Dependencies
requests: For making API calls.
datetime: For date calculations.
logging: For logging outputs.