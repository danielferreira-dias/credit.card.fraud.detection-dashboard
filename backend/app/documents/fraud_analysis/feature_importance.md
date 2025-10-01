# XGBoost Model Feature Importance Analysis

## Overview
This document details the feature importance analysis from the XGBoost fraud detection model trained on 250,000 transactions (200k training, 50k test) with 38 selected features.

## Model Performance Metrics

### Model Configuration
- **Algorithm**: XGBoost Classifier with StandardScaler
- **Training Set**: 200,000 transactions (stratified)
- **Test Set**: 50,000 transactions (stratified)
- **Features**: 38 engineered features
- **Evaluation Metric**: Log Loss
- **Cross-validation**: Stratified K-Fold

### Performance Results
The XGBoost model demonstrates strong performance on fraud detection with high recall and AUC scores suitable for production deployment.

## Top Features by Importance

Based on XGBoost's gain metric, the following features are ranked by their contribution to fraud prediction:

### Tier 1: Critical Features (Highest Importance)

#### 1. max_single_amount
**Description**: Maximum single transaction amount in the last hour
**Why Important**:
- Captures spending spikes and unusual large transactions
- Fraudsters often make one large transaction after testing with smaller amounts
- When current transaction ≈ max_single_amount, fraud probability increases
**Business Logic**: Indicates potential account takeover or spending pattern change

#### 2. USD_converted_amount
**Description**: Current transaction amount converted to USD
**Why Important**:
- Direct measure of transaction risk
- Fraudulent transactions average 5-7x higher than legitimate ones
- High-value transactions require more scrutiny
**Threshold**: Transactions > $1,000 show elevated fraud rates

#### 3. suspicious_device
**Description**: Binary flag for physical payment methods (NFC, Magnetic Stripe, Chip Reader)
**Why Important**:
- These devices show 100% fraud correlation in high-risk contexts
- Indicates potential card cloning or physical card theft
- Critical when combined with distance_from_home and high-risk countries
**Alert Level**: Highest priority flag

### Tier 2: High Importance Features

#### 4. high_risk_transaction
**Description**: Combined flag for high-risk country + suspicious device
**Why Important**:
- Compound risk indicator
- Captures the most dangerous fraud scenario
- Combines geographic and payment method risks
**Countries**: Brazil, Mexico, Nigeria, Russia

#### 5. channel_pos
**Description**: Transaction made at point-of-sale terminal
**Why Important**:
- Physical POS transactions in wrong context suggest card cloning
- Cross-referenced with card_present and device type
- Unusual when combined with distance from home

#### 6. distance_from_home
**Description**: Binary indicator if transaction is away from home location
**Why Important**:
- Travel + high-risk location = elevated fraud
- Legitimate customers may travel, but pattern differs
- Critical when combined with geographic risk factors
**Pattern**: Distance=1 + high-risk country + physical payment = very high fraud probability

#### 7. card_present
**Description**: Whether physical card was present during transaction
**Why Important**:
- Card-not-present (0) is majority of fraud (online transactions)
- Card-present (1) in suspicious context indicates stolen/cloned card
- Interaction with device type reveals fraud scenarios

### Tier 3: Significant Features

#### 8. USD_converted_total_amount
**Description**: Total amount spent in the last hour (USD)
**Why Important**:
- Velocity indicator - captures spending bursts
- High total_amount with high frequency suggests account compromise
- Complements max_single_amount for pattern detection

#### 9. transaction_hour & hour
**Description**: Hour of day when transaction occurred (0-23)
**Why Important**:
- Off-hours transactions (outside 9 AM - 5 PM) need scrutiny
- Fraud patterns show consistently high amounts across all hours
- Legitimate transactions vary more by time of day
**Peak Fraud Hours**: 9 AM ($6,528 median), 3 PM ($6,760 median)

#### 10. is_high_amount
**Description**: Binary flag for transactions > $1,000 USD
**Why Important**:
- Simple threshold for elevated risk
- High-value transactions warrant additional authentication
- Correlates strongly with fraud label

#### 11. is_low_amount
**Description**: Binary flag for transactions < $100 USD
**Why Important**:
- Captures card testing behavior
- Micro-transactions may be fraud validation attempts
- High count of low amounts precedes large fraudulent transactions

### Tier 4: Geographic Features

#### 12-19. Country Indicators
Features: `country_Nigeria`, `country_Brazil`, `country_Russia`, `country_Mexico`, `country_Singapore`, `country_France`, `country_Japan`, etc.

**Why Important**:
- Geographic risk stratification
- Nigeria, Russia, Mexico, Brazil show highest fraud rates
- Country-specific median amounts help contextualize risk
- Cross-border transactions need enhanced monitoring

**Nigeria Example**:
- Fraud median: 294,516 NGN
- Legitimate median: 174,883 NGN
- Pattern: Foreign travelers making large online purchases

### Tier 5: Channel and Device Features

#### 20-25. Channel Features
- `channel_web`: Online browser-based transactions
- `channel_mobile`: Mobile app transactions
- `channel_pos`: Point-of-sale terminal
- `channel_medium`: Medium-risk channel classification

**Why Important**:
- Channel consistency checks
- Web/mobile are majority of fraud (card-not-present)
- POS in wrong context suggests physical card compromise

#### 26-32. Device Features
- `device_Chrome`, `device_Firefox`, `device_Safari`, `device_Edge`
- `device_Android App`, `device_iOS App`
- `device_NFC Payment`, `device_Magnetic Stripe`, `device_Chip Reader`

**Why Important**:
- Device fingerprinting for consistency
- Physical devices (NFC, Magnetic, Chip) are red flags in certain contexts
- Browser/app consistency indicates legitimate customer behavior

## Feature Engineering Insights

### Engineered Features That Proved Valuable

1. **suspicious_device**: Aggregates three physical payment methods into single binary flag
2. **high_risk_transaction**: Compound indicator combining country and device risk
3. **is_high_amount / is_low_amount**: Simple thresholds that improve interpretability
4. **is_off_hours**: Banking hours vs. non-banking hours classification
5. **USD_converted_***: Currency normalization enables cross-currency comparison

### Currency Conversion
All amount-based features are converted to USD using fixed exchange rates:
- EUR: 1.06, CAD: 0.72, RUB: 0.01, NGN: 0.0006, SGD: 0.75
- MXN: 0.049, BRL: 0.17, AUD: 0.65, JPY: 0.0065, GBP: 1.28

**Impact**: Enables model to learn amount patterns across different currencies uniformly.

### Velocity Features (from velocity_last_hour)
Parsed from JSON into individual columns:
- `num_transactions`: Transaction count in last hour
- `total_amount`: Cumulative spending in last hour
- `unique_merchants`: Merchant diversity
- `unique_countries`: Geographic spread
- `max_single_amount`: Peak transaction in last hour

**Impact**: These temporal features capture behavioral changes and spending spikes critical for fraud detection.

## Feature Correlation Analysis

### High Correlation Pairs (> 0.5)
1. **transaction_hour ↔ hour**: Perfect correlation (same feature extracted twice)
2. **USD_converted_amount ↔ is_high_amount**: By design (threshold-based)
3. **USD_converted_amount ↔ is_low_amount**: By design (inverse threshold)
4. **suspicious_device ↔ device_NFC/Magnetic/Chip**: By design (aggregation)

### Low Correlation with Fraud (< 0.25)
- Most individual country flags (except high-risk countries)
- Individual device types (except suspicious devices)
- City indicators
- Card type ordinal encoding

**Conclusion**: Engineered compound features (suspicious_device, high_risk_transaction) outperform individual flags significantly.

## Feature Selection Process

### Initial Features: 113
After one-hot encoding of categorical variables:
- Merchant categories
- Merchant types
- Countries
- Cities
- Devices
- Channels
- Card types

### Selection Criteria
1. Correlation with fraud > 0.25 (absolute value)
2. Feature importance from preliminary models
3. Business logic and interpretability
4. Multicollinearity reduction

### Final Features: 38
Selected based on:
- Top 40 features by correlation with fraud
- Removal of redundant year feature
- Removal of raw fraud label
- Balance between model performance and interpretability

## Outlier Handling

### Outlier Counts (IQR Method)
- `card_number`: 62,491 outliers (24.9%)
- `amount`: 38,262 outliers (15.3%)
- `unique_countries`: 46,363 outliers (18.5%)
- `total_amount`: 18,546 outliers (7.4%)
- `max_single_amount`: 15,286 outliers (6.1%)

### Handling Strategy
**Log Transformation Applied**: Used for right-skewed distributions
- `np.log1p(amount)` for visualization
- StandardScaler normalization for modeling
- Outliers retained (not removed) as they contain fraud signals

**Rationale**: In fraud detection, outliers are often fraudulent transactions. Removing them would eliminate the very patterns we want to detect.

## Model Interpretation Guidelines

### Using Feature Importance for Investigation

When investigating a flagged transaction, prioritize features in this order:

1. **Check suspicious_device**: If true, investigate immediately
2. **Evaluate max_single_amount**: Compare to customer history
3. **Assess USD_converted_amount**: Against country-specific thresholds
4. **Review high_risk_transaction**: Geographic + device combination
5. **Examine distance_from_home**: Travel context matters
6. **Consider temporal factors**: transaction_hour, is_off_hours

### SHAP Values (Recommended)
For production deployment, implement SHAP (SHapley Additive exPlanations) to provide:
- Instance-level explanations
- Feature contribution to specific predictions
- Counterfactual reasoning ("what would make this legitimate?")

## Recommendations for Feature Monitoring

### Production Deployment Checklist

1. **Feature Drift Monitoring**: Track distribution changes over time
   - Alert if suspicious_device rate increases significantly
   - Monitor country distribution shifts
   - Track amount distribution evolution

2. **Feature Importance Tracking**: Retrain model periodically and compare feature importance
   - Ensure top features remain stable
   - Investigate if importance shifts dramatically

3. **New Feature Candidates**:
   - Customer age/tenure
   - Historical fraud rate by customer
   - Time since last transaction
   - Merchant fraud history
   - Email/phone verification status

4. **Feature Interaction Terms**:
   - amount × distance_from_home
   - suspicious_device × high_risk_country
   - num_transactions × total_amount (velocity ratio)

## Technical Notes

### Preprocessing Pipeline
```
1. Currency conversion (all amounts → USD)
2. Timestamp decomposition (datetime → hour, day, month, etc.)
3. Boolean to integer conversion (True/False → 1/0)
4. One-hot encoding (categorical → binary columns)
5. Feature engineering (compound indicators)
6. Feature selection (correlation + importance)
7. Train/test split (stratified, 80/20)
8. StandardScaler fitting (on train only)
9. Model training (XGBoost with scaled features)
```

### Important Note on Scaling
**Tree-based models (XGBoost, Random Forest) typically don't require scaling**, but this pipeline uses StandardScaler for:
- Consistent preprocessing if switching to neural networks
- Improved convergence if using regularization
- Fair comparison across different model types

In production, test both scaled and unscaled versions to optimize performance.

## Key Takeaways

1. **Compound features outperform individual flags**: suspicious_device and high_risk_transaction are top performers
2. **Amount-based features dominate**: max_single_amount and USD_converted_amount are most predictive
3. **Geographic context matters**: High-risk countries combined with other factors create strong signals
4. **Velocity indicators work**: Transaction counts and amounts over time windows catch behavioral changes
5. **Simple thresholds help**: is_high_amount and is_low_amount improve interpretability without sacrificing performance
6. **Feature engineering is critical**: Raw features alone are insufficient; domain knowledge drives performance

## Next Steps for Improvement

1. Implement SHAP for explainability
2. Add customer-level historical features
3. Engineer feature interaction terms
4. Build merchant-level risk scores
5. Incorporate real-time velocity calculations
6. Add device fingerprint consistency checks
7. Test non-linear feature transformations
8. Explore deep learning for automatic feature learning
