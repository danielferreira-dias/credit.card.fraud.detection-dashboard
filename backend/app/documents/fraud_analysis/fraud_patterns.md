# Credit Card Fraud Patterns

## Overview
This document summarizes fraud patterns discovered through analysis of 7.5 million synthetic transaction records, with a focus on behavioral indicators and risk factors.

## High-Risk Geographic Patterns

### High-Risk Countries
The following countries show elevated fraud rates and require enhanced monitoring:

- **Brazil**
- **Mexico**
- **Nigeria**
- **Russia**

### Geographic Risk Indicators

#### Nigeria
- Median transaction amount for fraud: **294,516.61 NGN** (vs. 174,883.12 for legitimate)
- **Pattern**: Large transactions from travelers (distance_from_home = 1) made via online channels
- **Key Indicator**: Foreign customers making high-value transactions in Nigeria show significantly higher fraud rates

#### Other High-Risk Countries
- **Brazil Fraud**: Median 3,811.93 BRL (vs. 2,084.78 legitimate)
- **Mexico Fraud**: Median 14,976.80 MXN (vs. 8,268.82 legitimate)
- **Russia Fraud**: Median 56,978.94 RUB (vs. 31,081.49 legitimate)

**Conclusion**: Fraudulent transactions consistently show higher median amounts across all high-risk countries.

## Payment Method Risk Profiles

### Critical Risk - Physical Payment Methods
The following payment methods show 100% fraud correlation when combined with high-risk countries:

1. **NFC Payment** - Near-field communication payments
2. **Magnetic Stripe** - Traditional card swipe
3. **Chip Reader** - EMV chip transactions

**Important Note**: These payment methods show NO legitimate transactions in the dataset when used in high-risk scenarios. Any transaction using these methods in high-risk countries should be flagged immediately.

### Device-Based Risk Patterns

Fraudulent transactions show significantly higher median amounts across all device types:

| Device | Legitimate Median | Fraud Median | Risk Multiplier |
|--------|-------------------|--------------|-----------------|
| Android App | $854.83 | $5,821.77 | 6.8x |
| Chrome | $973.01 | $6,116.26 | 6.3x |
| Edge | $858.82 | $4,868.61 | 5.7x |
| Firefox | $884.13 | $6,264.61 | 7.1x |
| Safari | $882.82 | $5,396.60 | 6.1x |
| iOS App | $983.02 | $5,385.77 | 5.5x |

## Transaction Amount Patterns

### Amount-Based Indicators

1. **High-Value Threshold**: Transactions > $1,000 USD show increased fraud likelihood
2. **Low-Value Pattern**: Micro-transactions < $100 USD can indicate testing behavior

### Critical Amount Pattern
**When current transaction amount equals or is close to `max_single_amount` in the last hour, fraud likelihood increases significantly.**

This pattern suggests:
- First large transaction in a sequence
- Account testing with progressively larger amounts
- Unusual spending spike

### Amount Distribution
- **Mean Transaction**: $537.58 USD
- **Standard Deviation**: $714.94 USD
- **Distribution**: Highly right-skewed (skew = 12.01)
- **Outliers**: 38,262 outliers detected (15.3% of sample)

## Temporal Fraud Patterns

### Banking Hours Analysis
- **Banking Hours**: 9 AM - 5 PM
- **Off-Hours Risk**: Transactions outside banking hours require additional scrutiny

### Transaction Hour Patterns
Fraudulent transactions show elevated median amounts throughout the day, with notable peaks:
- **9 AM**: $6,528.06 (highest fraud median)
- **15 PM**: $6,760.31 (second highest)
- **12 PM**: $6,347.45

**Pattern**: Fraud maintains consistently high amounts regardless of time, while legitimate transactions vary more by hour.

### Transaction Frequency
- **Median Legitimate**: ~290 transactions/hour
- **Median Fraud**: ~290 transactions/hour
- **Note**: Frequency alone is not a strong discriminator; velocity metrics (amount + frequency) are more valuable

## Velocity-Based Fraud Indicators

### High-Risk Velocity Patterns

#### Micro-Transaction Fraud
**Pattern**: High transaction count (> 20 transactions) with low total amount (< $100)
- Indicates card testing or validation attempts
- Precursor to larger fraudulent transactions

#### Velocity Metrics (Last Hour)
Key indicators derived from customer behavior in the preceding hour:

1. **num_transactions**: Number of transactions
2. **total_amount**: Cumulative spending
3. **unique_merchants**: Merchant diversity
4. **unique_countries**: Geographic spread
5. **max_single_amount**: Largest single transaction

**Red Flags**:
- High unique_countries count (> 5) in one hour
- Max single amount significantly higher than average
- Many transactions across diverse merchant categories

## Distance and Location Patterns

### Distance from Home
- **distance_from_home = 0**: Transaction at home location
- **distance_from_home = 1**: Transaction away from home

**Critical Pattern**: Transactions away from home (distance_from_home = 1) combined with:
- High-risk countries
- Physical payment methods (NFC, Magnetic Stripe, Chip Reader)
- High transaction amounts

**Fraud Scenario**: Foreign travelers making large purchases via physical payment methods in high-risk countries show extremely high fraud rates.

## Card Type and Presence

### Card Presence
- **card_present = 0**: Card-not-present (online/phone transactions)
- **card_present = 1**: Card physically present

**Pattern**: Most fraudulent transactions are card-not-present (online), but physical card presence in high-risk scenarios is a strong fraud indicator.

### Card Type Hierarchy (Risk Order)
1. Premium Debit (Highest value)
2. Platinum Credit
3. Gold Credit
4. Basic Debit
5. Basic Credit

Higher-tier cards are more frequently targeted for fraud due to higher limits.

## Combined Risk Scenarios

### Highest Risk Combination
A transaction is extremely high-risk when it combines:
1. ✓ High-risk country (Brazil, Mexico, Nigeria, Russia)
2. ✓ Physical payment method (NFC, Magnetic Stripe, Chip Reader)
3. ✓ Distance from home = 1
4. ✓ High transaction amount (> median for country)
5. ✓ Card-not-present OR physical card in suspicious context

### Suspicious Device Pattern
Transactions using physical payment methods in online/remote scenarios are inherently suspicious and warrant immediate investigation.

## Fraud vs. Legitimate Distribution

### Class Imbalance
The dataset shows typical fraud detection class imbalance:
- **Legitimate transactions**: ~95%
- **Fraudulent transactions**: ~5%

This imbalance requires:
- Stratified sampling for model training
- Focus on recall (catching fraud) over precision
- Threshold tuning for optimal fraud detection

## Key Takeaways

1. **Geographic + Payment Method**: The combination of high-risk countries with physical payment methods is a near-certain fraud indicator
2. **Amount Patterns**: Fraudulent transactions consistently show 5-7x higher median amounts across all dimensions
3. **Velocity Anomalies**: Multiple countries, merchants, or unusual spending patterns in short timeframes are red flags
4. **Distance Matters**: Travel + high-risk location + physical payment = high fraud probability
5. **Amount Spikes**: When current transaction approaches or equals max_single_amount in last hour, investigate immediately

## Recommendations for Fraud Detection

1. **Immediate Flags**: Block or challenge transactions matching highest-risk combinations
2. **Enhanced Monitoring**: Apply step-up authentication for high-risk country transactions
3. **Velocity Checks**: Monitor rolling hour windows for suspicious patterns
4. **Amount Thresholds**: Dynamic thresholds based on country, card type, and customer history
5. **Device Fingerprinting**: Track device consistency and flag device changes during high-risk transactions
