# Transaction Fraud Indicators

## Overview
This document provides detailed guidance on specific transaction-level indicators that signal potential fraud, based on analysis of 7.5 million transaction records.

## Amount-Based Indicators

### High-Value Transaction Indicator

**Feature**: `is_high_amount`
**Threshold**: > $1,000 USD equivalent
**Fraud Correlation**: Strong positive correlation

#### Risk Assessment
- **Low Risk**: < $100 USD
- **Medium Risk**: $100 - $1,000 USD
- **High Risk**: $1,000 - $5,000 USD
- **Critical Risk**: > $5,000 USD

#### Context Matters
High amounts are only suspicious when combined with:
- Unusual merchant categories for customer
- Geographic anomalies
- Device/channel changes
- Velocity spikes

**Example**: A $5,000 transaction at a premium restaurant in the customer's home city using their usual device is likely legitimate. The same amount in Nigeria via Magnetic Stripe from a foreign traveler is extremely suspicious.

### Low-Value Transaction Indicator

**Feature**: `is_low_amount`
**Threshold**: < $100 USD equivalent
**Fraud Pattern**: Card testing and validation

#### Card Testing Behavior
Fraudsters often test stolen cards with small transactions before attempting larger fraud:

1. **Initial Test**: $1-$5 transaction at low-risk merchant
2. **Validation**: $10-$50 transaction at different merchant
3. **Exploitation**: Large transaction ($1,000+) at high-value merchant

#### Detection Strategy
Look for micro-transaction patterns:
- Multiple transactions < $50 in short time window
- High `num_transactions` (> 20) with low `total_amount` (< $100)
- Transactions at unusual merchant categories
- Different geographic locations for small amounts

**Feature**: `micro_transaction_risk`
**Formula**: (num_transactions > 20) AND (total_amount < $100)

### Maximum Single Amount Pattern

**Feature**: `max_single_amount`
**Description**: Largest transaction in the last hour

#### Critical Pattern: Amount Equals Max
**When current transaction amount ≈ max_single_amount, investigate immediately**

**Scenarios**:
1. **First Large Transaction**: Customer suddenly makes largest purchase of the hour
   - May indicate account takeover
   - Compare against customer's historical max

2. **Escalating Pattern**: Series of transactions building to a peak
   - Test transaction: $50
   - Validation: $200
   - Exploitation: $3,000 (becomes max_single_amount)

3. **Repeated Maximum**: Multiple transactions at same high amount
   - Fraudster maximizing stolen card value
   - Often at same merchant or merchant category

#### Business Rule
```
IF (current_amount == max_single_amount) AND (max_single_amount > customer_historical_avg * 3):
    FLAG as HIGH RISK
```

### Amount Distribution Characteristics

**Dataset Statistics**:
- Mean: $537.58
- Median: $353.86
- Std Dev: $714.94
- Skewness: 12.01 (highly right-skewed)

**Interpretation**: Most transactions are small to medium, with a long tail of high-value transactions. Fraudulent transactions concentrate in this tail.

#### Percentile-Based Risk Scoring

| Percentile | Amount (USD) | Risk Level |
|------------|--------------|------------|
| 25th | $167.16 | Low |
| 50th | $353.86 | Low-Medium |
| 75th | $621.01 | Medium |
| 90th | $1,200+ | High |
| 95th | $2,500+ | Very High |
| 99th | $8,000+ | Critical |

Transactions above the 90th percentile warrant additional scrutiny.

## Velocity-Based Indicators

### Transaction Frequency (num_transactions)

**Feature**: `num_transactions`
**Description**: Number of transactions in the last hour
**Distribution**: Right-skewed with median around 290-310

#### Fraud Patterns

1. **Burst Pattern**: Sudden spike from customer baseline
   - Normal: 1-3 transactions/hour
   - Suspicious: > 10 transactions/hour
   - Critical: > 20 transactions/hour

2. **Sustained Frequency**: Consistently high transaction rate
   - May indicate account sharing or business use
   - Cross-reference with merchant diversity

#### Combined with Amount
- **High Frequency + High Total**: Account takeover or fraud spree
- **High Frequency + Low Total**: Card testing
- **Low Frequency + High Amount**: Legitimate customer or targeted fraud

### Total Amount Velocity (total_amount)

**Feature**: `USD_converted_total_amount`
**Description**: Cumulative spending in the last hour

#### Risk Thresholds by Customer Segment

**Personal Cards**:
- Normal: < $500/hour
- Elevated: $500 - $2,000/hour
- Suspicious: $2,000 - $10,000/hour
- Critical: > $10,000/hour

**Business Cards**:
- Normal: < $5,000/hour
- Elevated: $5,000 - $20,000/hour
- Suspicious: > $20,000/hour

#### Distribution Analysis
- Mean: ~$10M (highly skewed by outliers)
- Skewness: 6.54 (right-skewed)
- Outliers: 18,546 (7.4%)

**Interpretation**: Outliers in total_amount are prime fraud candidates. Investigate any customer spending > 10x their historical hourly average.

### Merchant Diversity (unique_merchants)

**Feature**: `unique_merchants`
**Description**: Count of unique merchants in last hour

#### Fraud Indicators

**Low Diversity (< 5 merchants)**:
- Normal customer behavior
- Legitimate shopping trip
- Low risk alone

**Medium Diversity (5-10 merchants)**:
- Legitimate if consistent with customer pattern
- Suspicious if unusual categories
- Cross-check with customer history

**High Diversity (> 10 merchants)**:
- Highly suspicious - rare in legitimate behavior
- Indicates fraud spree or card testing across merchants
- Combined with high total_amount = likely fraud

**Distribution**: Left-skewed with median around 70-105 unique merchants
- Note: This metric appears to be cumulative across broader time window in dataset

### Geographic Diversity (unique_countries)

**Feature**: `unique_countries`
**Description**: Count of unique countries in last hour

#### Risk Assessment

**Single Country (1)**:
- Normal behavior
- Low risk baseline

**Two Countries (2)**:
- Possible if near border or airport
- Medium risk - verify travel context

**Three+ Countries (≥ 3)**:
- Highly suspicious in one hour
- Physical impossibility for legitimate customer
- Strong fraud indicator
- Suggests credential theft and use across geographic regions

**Distribution**: Left-skewed with median around 6-12 countries
- 46,363 outliers (18.5%) - extremely high diversity

**Critical Rule**:
```
IF (unique_countries >= 3) AND (time_window == 1 hour):
    FLAG as FRAUD - Geographic Impossibility
```

## Temporal Indicators

### Transaction Hour Patterns

**Feature**: `transaction_hour` (0-23)

#### Fraud by Hour of Day

Fraudulent transactions maintain consistently high median amounts across all hours:

**Peak Fraud Hours**:
- 9 AM: $6,528.06 median
- 3 PM: $6,760.31 median
- 12 PM: $6,347.45 median
- 4 AM: $6,273.15 median

**Legitimate Pattern**: Varies more by hour
- Business hours (9-17): Higher volume, moderate amounts
- Evening (18-23): Moderate volume, dining/entertainment
- Night (0-8): Low volume, lower amounts

#### Key Insight
**Fraud doesn't follow typical circadian patterns**. Legitimate customers spend differently throughout the day, but fraudsters maintain high transaction amounts regardless of time.

### Banking Hours Indicator

**Feature**: `is_off_hours`
**Definition**: Transactions outside 9 AM - 5 PM
**Values**:
- 0 = Off-hours (night/evening)
- 1 = Banking hours (9 AM - 5 PM)

#### Risk Context
Off-hours transactions are NOT automatically suspicious, but require context:

**Low Risk Off-Hours**:
- Dining (evening)
- Entertainment (evening/night)
- Gas stations (any time)
- Consistent with customer pattern

**High Risk Off-Hours**:
- Large bank transfers at 3 AM
- New merchant categories at odd hours
- High-value purchases in foreign countries
- Combined with other red flags

### Day of Week Patterns

**Feature**: `weekend_transaction`
**Values**: 1 = Weekend, 0 = Weekday

#### Fraud Distribution
Weekend transactions show similar fraud rates to weekdays in this dataset. Weekend flag alone is not a strong discriminator.

**Context-Dependent Risk**:
- Business card weekend use may be unusual
- Personal card weekend use is normal
- Combine with merchant category for insights

## Geographic and Location Indicators

### Distance from Home

**Feature**: `distance_from_home`
**Values**:
- 0 = At home location
- 1 = Away from home

#### Risk Matrix

| Distance | Amount | High-Risk Country | Risk Level |
|----------|--------|-------------------|------------|
| 0 | Any | No | Low |
| 0 | High | Yes | Medium |
| 1 | Low | No | Low-Medium |
| 1 | Low | Yes | Medium |
| 1 | High | No | Medium-High |
| 1 | High | Yes | **CRITICAL** |

#### Critical Fraud Pattern
**Distance = 1 + High-Risk Country + High Amount + Physical Payment = Near-certain fraud**

**Example Scenario**:
- Customer normally transacts in USA (home)
- Sudden transaction in Nigeria (distance = 1)
- Transaction amount: $5,000+ (high)
- Payment method: Magnetic Stripe (suspicious_device)
- **Conclusion**: Very high probability of card cloning or theft

### Country-Specific Amount Thresholds

Different countries have different baseline transaction amounts due to currency and economic factors. Apply country-specific risk thresholds:

#### Nigeria (NGN)
- Legitimate median: 174,883 NGN (~$105 USD)
- Fraud median: 294,517 NGN (~$177 USD)
- **Threshold**: > 300,000 NGN requires scrutiny

#### Russia (RUB)
- Legitimate median: 31,081 RUB (~$311 USD)
- Fraud median: 56,979 RUB (~$570 USD)
- **Threshold**: > 60,000 RUB requires scrutiny

#### Mexico (MXN)
- Legitimate median: 8,269 MXN (~$405 USD)
- Fraud median: 14,977 MXN (~$734 USD)
- **Threshold**: > 15,000 MXN requires scrutiny

#### Brazil (BRL)
- Legitimate median: 2,085 BRL (~$354 USD)
- Fraud median: 3,812 BRL (~$648 USD)
- **Threshold**: > 4,000 BRL requires scrutiny

## Device and Channel Indicators

### Suspicious Device Flag

**Feature**: `suspicious_device`
**Devices Included**:
- NFC Payment
- Magnetic Stripe
- Chip Reader

#### Critical Importance
This is the **highest-importance engineered feature** in the model.

**Why These Devices Are Suspicious**:
1. **Card Cloning**: Magnetic stripe can be cloned easily
2. **Physical Theft**: Implies fraudster has physical card
3. **Context Mismatch**: These methods shouldn't appear in certain contexts

#### Zero Tolerance in High-Risk Scenarios
When `suspicious_device = 1` AND `high_risk_country = 1`:
- **Fraud rate approaches 100%**
- Immediate block or challenge required
- No legitimate transactions observed in this pattern

### Channel Consistency

**Features**: `channel_web`, `channel_mobile`, `channel_pos`

#### Normal Patterns
Customers typically use consistent channels:
- Online shoppers: Predominantly `channel_web` or `channel_mobile`
- In-person shoppers: Predominantly `channel_pos`

#### Red Flags
- Sudden channel switch (web → POS in foreign country)
- POS transaction when card should be at home
- Multiple channels in short time from different locations

### Device Fingerprint (Excluded from Model)

**Note**: Device fingerprint was excluded from final model due to high cardinality (unique per transaction), but it's valuable for:
- Device consistency checks
- Anomaly detection (new device for account)
- Cross-referencing with IP address

**Production Recommendation**: Maintain device fingerprint history and flag new devices on high-value transactions.

## Card-Based Indicators

### Card Type Risk Hierarchy

**Feature**: `card_type` (ordinal encoding)

**Risk Order (Value in Model)**:
1. Premium Debit (4) - Highest fraud target
2. Platinum Credit (3)
3. Gold Credit (2)
4. Basic Debit (1)
5. Basic Credit (0) - Lowest fraud target

**Why Premium Cards Have Higher Risk**:
- Higher credit limits
- More valuable to fraudsters
- Targets for sophisticated fraud
- Used by high-net-worth individuals

### Card Present vs. Card Not Present

**Feature**: `card_present`

**Distribution of Fraud**:
- **Card Not Present (0)**: Majority of fraud (~80-90%)
  - Online transactions
  - Phone orders
  - Mail orders

- **Card Present (1)**: Lower fraud volume but critical when it occurs
  - Physical card theft
  - Card cloning
  - Counterfeit cards

#### Investigation Strategy

**Card Not Present Fraud**:
- Check CVV validation
- Verify billing address
- Review IP geolocation
- Examine device fingerprint

**Card Present Fraud**:
- Physical card status (reported stolen?)
- Geographic impossibility (last online transaction elsewhere?)
- Device type consistency
- Merchant reputation

## Compound Indicators

### High-Risk Transaction Flag

**Feature**: `high_risk_transaction`
**Formula**: (country IN [Brazil, Mexico, Nigeria, Russia]) AND (device IN [NFC, Magnetic Stripe, Chip Reader])

#### Why This Works
Combines two independent risk factors that amplify each other:

1. **Geographic Risk**: These countries have elevated fraud rates
2. **Device Risk**: Physical payment methods suggest card possession
3. **Combined Risk**: Foreign traveler with physical card in high-risk country making large purchase

**Fraud Rate**: Near 100% when this flag is true

**Legitimate Cases**: Extremely rare
- Business travelers with corporate cards
- Expatriates with local cards
- Should still trigger step-up authentication

### Micro-Transaction Risk

**Feature**: `micro_transaction_risk`
**Formula**: (num_transactions > 20) AND (total_amount < $100)

#### Fraud Scenario
Card testing phase before main fraud:
1. Fraudster obtains card details
2. Tests with many small transactions to validate
3. Once confirmed active, makes large purchases

**Detection Value**:
- Early warning system
- Catches fraud before major loss
- Enables proactive card freezing

## Alert Prioritization Matrix

### Critical Alerts (Investigate Immediately)
1. `suspicious_device = 1` AND `high_risk_transaction = 1`
2. `unique_countries >= 3` in last hour
3. `USD_converted_amount > $10,000`
4. `current_amount == max_single_amount` AND `amount > 5x customer average`

### High Priority Alerts (Investigate Within 1 Hour)
1. `distance_from_home = 1` AND `country` in high-risk list
2. `num_transactions > 20` AND `total_amount < $100`
3. `USD_converted_amount > $5,000` AND `is_off_hours = 1`
4. Device fingerprint never seen before on account

### Medium Priority Alerts (Review Within 24 Hours)
1. `is_high_amount = 1` with unusual merchant category
2. `unique_merchants > 10` in last hour
3. Transaction in new country for customer
4. Amount > 90th percentile for customer history

### Low Priority (Automated Monitoring)
1. `is_low_amount = 1` transactions
2. Transactions at home location with usual device
3. Amounts within customer's normal range
4. Consistent merchant categories

## Real-Time Scoring Recommendation

### Composite Risk Score Formula
```
risk_score = (
    suspicious_device * 30 +
    high_risk_transaction * 25 +
    (distance_from_home * country_risk_score) * 15 +
    amount_percentile_score * 10 +
    velocity_score * 10 +
    geographic_diversity_score * 5 +
    time_anomaly_score * 5
)

IF risk_score >= 80: BLOCK
IF risk_score >= 60: CHALLENGE (2FA)
IF risk_score >= 40: MONITOR
IF risk_score < 40: APPROVE
```

### Dynamic Thresholds
Adjust thresholds based on:
- Customer risk profile
- Historical fraud rate
- Current fraud trends
- Business impact tolerance

## Key Takeaways

1. **Amount alone is insufficient**: Context (country, device, velocity) is critical
2. **Velocity matters**: Sudden spikes in frequency or amount are red flags
3. **Geographic impossibility**: Multiple countries in one hour = fraud
4. **Device + Geography combination**: Strongest signal for fraud
5. **Micro-transactions precede major fraud**: Early detection saves money
6. **Time patterns differ**: Fraud maintains consistent high amounts across all hours
7. **Compound indicators outperform single flags**: Engineered features like high_risk_transaction are most valuable

## Recommended Actions by Indicator

| Indicator | Action | Reason |
|-----------|--------|--------|
| suspicious_device + high_risk_country | BLOCK | 100% fraud rate |
| unique_countries >= 3 | BLOCK | Physical impossibility |
| amount > $10,000 | CHALLENGE | High value at risk |
| micro_transaction_risk | MONITOR | Card testing phase |
| distance_from_home + high amount | CHALLENGE | Unusual pattern |
| New device fingerprint + high amount | CHALLENGE | Account security |
| Off-hours + new merchant category | MONITOR | Pattern deviation |
| Normal indicators | APPROVE | Low risk |

Use these indicators in combination with the XGBoost model predictions for optimal fraud detection.
