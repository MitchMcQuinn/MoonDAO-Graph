from datetime import datetime

# Constants
INITIAL_MOONEY_GEOMETRIC_RELEASE = Decimal('15000000')
TOTAL_ASSET_PERCENT_RELEASED_QUARTERLY = Decimal('0.05')
QUARTER_END_DATE = datetime.date(2024, 9, 30)
TREASURY_SAFE_ETH = '0xce4a1E86a5c47CD677338f53DA22A91d85cab2c9'
GEOMETRIC_DECREASE_RATE = Decimal('0.95')
COMMUNITY_REWARDS_PERCENTAGE = Decimal('0.10')

## Onchain Labels
SECOND_ASTRONAUT_SUPPORT = '0xFFe1bcF92156f50c78F0B6dE4B5fAa3fAA6AdB52'

def calculate_current_geometric_cycle():
    start_year = 2022
    start_quarter = 4
    current_date = datetime.now()
    current_year = current_date.year
    current_month = current_date.month

    # Calculate the number of quarters since Q4 2022
    quarters_since_start = (current_year - start_year) * 4 + ((current_month - 1) // 3) - (start_quarter - 1)
    return quarters_since_start

def calculate_total_mooney_to_distribute(initial_amount, cycle):
    total = initial_amount * (0.95 ** cycle)
    return total

def fetch_treasury_assets(treasury_address):
    # Implement API calls here
    pass

def calculate_total_eth_to_distribute(assets):
    total_value = sum(asset['value_in_eth'] for asset in assets)
    total_to_distribute = total_value * TOTAL_ASSET_PERCENT_RELEASED_QUARTERLY
    return total_to_distribute

def calculate_community_rewards(total_mooney):
    community_rewards = total_mooney * 0.10
    return community_rewards
