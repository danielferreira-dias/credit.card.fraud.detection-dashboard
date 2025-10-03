# Exploratory Data Analysis Insights

## Dataset Overview

### Dataset Statistics
- **Total Transactions**: 7,483,766
- **Sample Size (for analysis)**: 250,000 (stratified)
- **Training Set**: 200,000 transactions
- **Test Set**: 50,000 transactions
- **Time Period**: October 2024 (synthetic data)
- **Geographic Coverage**: 12 countries
- **Merchant Coverage**: 105+ unique merchants

### Data Quality
- **Missing Values**: 0 (complete dataset)
- **Data Types**: Mixed (24 original columns)
  - Numeric: 3 (int64), 1 (float64)
  - Boolean: 4
  - Object: 16

### Memory Footprint
- Full dataset: ~1.1 GB
- Sample dataset: ~56.3 MB (after feature engineering)

## Class Distribution

### Fraud vs. Legitimate Transactions

**Class Imbalance**:
- Fraudulent: ~5% (typical of fraud datasets)
- Legitimate: ~95%

**Implications**:
1. **Stratified sampling required**: Maintain fraud ratio in train/test splits
2. **Evaluation metrics**: Focus on Recall, F1-Score, AUC-ROC (not just accuracy)
3. **Model training**: Consider class weights or SMOTE for balancing
4. **Business context**: High recall priority (catch fraud) vs. precision (avoid false positives)

**Stratification Strategy Used**:
```python
train_test_split(X, y, test_size=0.2, stratify=y, random_state=97)
```

## Numerical Variable Analysis

### Amount Variable (Transaction Amount)

**Original Statistics (before USD conversion)**:
- **Distribution**: Highly right-skewed (skew = 12.01)
- **Mean >> Std**: Indicates extreme outliers
- **Outliers**: 38,262 (15.3% of sample)
- **Interpretation**: Majority of transactions are small; few very large transactions

**USD Converted Statistics**:
- **Mean**: $537.58
- **Std Dev**: $714.94
- **Min**: $0.002
- **25th Percentile**: $167.16
- **Median (50th)**: $353.86
- **75th Percentile**: $621.01
- **Max**: $19,154.07

**Skewness Analysis**:
- Original: 12.01 (extreme right skew)
- After log transformation: More normal distribution
- **Decision**: Applied StandardScaler for modeling, log1p for visualization

**Visual Patterns**:
- Long tail extending to high values
- Concentration of transactions in $100-$1,000 range
- Clear separation between fraud (higher) and legitimate (lower) distributions when plotted with log scale

### Transaction Hour Variable

**Statistics**:
- **Range**: 0-23
- **Distribution**: Nearly uniform
- **Skewness**: -0.14 (almost symmetric)
- **Outliers**: 0 (no outliers by definition)

**Fraud vs. Legitimate Patterns**:
- Legitimate: Varies throughout day (higher during business hours)
- Fraud: Consistent high amounts regardless of hour
- **Key Finding**: Fraudsters don't follow typical consumer behavior patterns

### Velocity Metrics (From velocity_last_hour)

#### Number of Transactions (num_transactions)
- **Distribution**: Right-skewed (skew = 1.55)
- **Median**: ~290-310 transactions
- **Outliers**: 6,907 (2.8%)
- **Fraud vs. Legitimate**: Similar medians (~290 vs. ~305)
- **Insight**: Frequency alone doesn't discriminate well; must combine with amounts

#### Total Amount (total_amount)
- **Distribution**: Highly right-skewed (skew = 6.54)
- **Outliers**: 18,546 (7.4%)
- **Range**: Wide variance ($0 to millions)
- **Insight**: Cumulative spending spikes are strong fraud indicators

#### Unique Merchants
- **Distribution**: Left-skewed (skew = -1.17)
- **Median**: 70-105 merchants
- **Outliers**: 4,074 (1.6%)
- **Pattern**: High merchant diversity in short time suggests fraud spree

#### Unique Countries
- **Distribution**: Strongly left-skewed (skew = -2.22)
- **Median**: 6-12 countries
- **Outliers**: 46,363 (18.5% - highest outlier rate)
- **Critical Finding**: Multiple countries in one hour is physically impossible for legitimate customers

#### Max Single Amount
- **Distribution**: Right-skewed (skew = 1.19)
- **Outliers**: 15,286 (6.1%)
- **Correlation with fraud**: Strong positive
- **Key Pattern**: When current transaction equals max, fraud risk spikes

### Card Number Variable
- **Outliers**: 62,491 (24.9%)
- **Note**: High outlier count due to distribution of card numbers
- **Model Treatment**: Dropped from model (PII, high cardinality)
- **Production Use**: Maintain for tracking but don't use as feature

## Categorical Variable Analysis

### Binary Variables Distribution

#### Card Present
- **Not Present (0)**: ~95%
- **Present (1)**: ~5%
- **Interpretation**: Most transactions are online/phone (card-not-present)

#### Distance from Home
- **At Home (0)**: ~70%
- **Away from Home (1)**: ~30%
- **Fraud Pattern**: Travel combined with other factors increases risk

#### High-Risk Merchant
- **Normal Merchant (0)**: ~85%
- **High-Risk Merchant (1)**: ~15%
- **Examples**: Entertainment (gaming, streaming), high-risk categories

#### Weekend Transaction
- **Weekday (0)**: ~70%
- **Weekend (1)**: ~30%
- **Fraud Difference**: Minimal - not a strong discriminator alone

#### Is Fraud (Target Variable)
- **Legitimate (0)**: ~95%
- **Fraud (1)**: ~5%
- **Class Imbalance**: Significant, requires stratified sampling

### Merchant Category

**Categories in Dataset**:
- Restaurant
- Entertainment
- Grocery
- Gas
- Healthcare
- (Others)

**Fraud Patterns by Category**:
- **High-Risk**: Entertainment (gaming, streaming)
- **Medium-Risk**: Restaurant (premium), Travel
- **Low-Risk**: Grocery, Gas (daily necessities)

**Visualization Insight**: When plotted with fraud flag, Entertainment shows highest fraud proportion

### Merchant Type

**Types**:
- Physical
- Online
- Streaming
- Gaming
- Premium
- Casual
- Medical
- Fast food

**Fraud Correlation**:
- **Highest**: Gaming, Streaming (Entertainment sub-categories)
- **Medium**: Premium (high-value merchants)
- **Lowest**: Fast food, Medical

### Currency Distribution

**Currencies in Dataset**:
- EUR, CAD, RUB, NGN, SGD, MXN, BRL, AUD, JPY, GBP, USD

**Fraud by Currency** (reflects country risk):
- **Highest**: NGN (Nigeria), RUB (Russia), MXN (Mexico), BRL (Brazil)
- **Moderate**: CAD, AUD, SGD
- **Lowest**: EUR, GBP, USD, JPY

**Feature Engineering Decision**: Convert all to USD for uniform comparison

### Country Distribution

**Countries Represented**: 12 total
- USA, UK, Germany, France, Canada, Japan, Singapore, Australia
- Brazil, Mexico, Nigeria, Russia (high-risk)

**Fraud Rate Ranking** (highest to lowest):
1. Nigeria
2. Russia
3. Mexico
4. Brazil
5. (Others - significantly lower)

**Geographic Insight**: Fraud concentrates in specific countries, enabling geographic risk stratification

### Device Distribution

**Device Types**:
- **Browsers**: Chrome, Firefox, Safari, Edge
- **Mobile Apps**: iOS App, Android App
- **Physical**: Chip Reader, Magnetic Stripe, NFC Payment

**Fraud Pattern**:
- Physical devices in online/remote contexts = suspicious
- Browser/app consistency = legitimate
- New device for account = potential takeover

### Channel Distribution

**Channels**:
- **Web**: ~60% (browser-based)
- **Mobile**: ~25% (app-based)
- **POS**: ~12% (point-of-sale)
- **Medium**: ~3% (other channels)

**Fraud by Channel**:
- Web and Mobile dominate fraud (card-not-present)
- POS fraud indicates physical card compromise

### City and City Size

**Cities**: Predominantly "Unknown City" (~99%)
- Low variability, limited discriminatory power
- Excluded from final feature selection

**City Sizes**:
- Small, Medium, Large
- Even distribution
- Minimal fraud correlation

### Card Type Distribution

**Types** (from highest to lowest tier):
1. Premium Debit
2. Platinum Credit
3. Gold Credit
4. Basic Debit
5. Basic Credit

**Fraud Pattern**: Higher-tier cards targeted more frequently due to higher limits

**Encoding Strategy**: Ordinal encoding (0-4) to capture hierarchy

## Multivariate Analysis

### Correlation Analysis

**Highly Correlated Pairs** (> 0.5 correlation):
- transaction_hour ↔ hour (1.0 - identical)
- USD_converted_amount ↔ is_high_amount (0.85 - by design)
- USD_converted_amount ↔ is_low_amount (-0.62 - inverse threshold)
- suspicious_device ↔ individual device flags (aggregate relationship)

**Feature Selection Impact**:
- Removed redundant hour variable (kept transaction_hour)
- Kept engineered threshold features despite correlation (interpretability value)
- Focused on features with |correlation| > 0.25 with fraud

### Amount vs. Max Single Amount Scatter Plot

**Key Finding**: When plotted with fraud flag:
- **Fraudulent transactions cluster along diagonal** (amount ≈ max_single_amount)
- Legitimate transactions more dispersed
- Interpretation: Fraudsters often make the largest transaction of the hour

**Visual Pattern**:
- Log scale required to visualize full range
- Clear separation between fraud (red) and legitimate (blue)
- Overlap region requires additional features to discriminate

### Country-Specific Deep Dive

#### Nigeria Analysis
**High-Value Transaction Breakdown** (amount > 294,516 NGN):
- **Distance from Home**: Majority are distance = 1 (travelers)
- **Card Present**: Majority are card_present = 0 (online)
- **Pattern**: Foreign travelers making large online purchases in Nigeria

**Fraud Characteristics**:
- Large amounts + distance from home + online = high fraud
- Physical card transactions in Nigeria also suspicious
- Country-specific threshold critical

#### Brazil, Mexico, Russia
Similar patterns observed:
- Higher median amounts for fraud
- Travel + high amount = elevated risk
- Device type matters significantly

### Device vs. Fraud Status

**Median Transaction Amount by Device**:
- All devices show 5-7x higher amounts for fraud
- Physical payment devices (Chip, Magnetic, NFC) have no legitimate baseline in high-risk contexts
- Browser-based (Chrome, Firefox, Safari, Edge) show consistent patterns

**Visualization**: Bar plot shows clear separation between legitimate and fraud median amounts across all devices

### Transaction Hour vs. Amount

**Line Plot Analysis**:
- **Legitimate**: Varies by hour (peaks during business hours, dips at night)
- **Fraud**: Remains consistently high across all hours
- **Insight**: Fraudsters don't follow consumer circadian rhythms

**Banking Hours Overlay**:
- Vertical lines at 9 AM (bank opening) and 5 PM (bank closing)
- Fraud amounts don't correlate with banking hours
- Legitimate transactions show more variation

### Customer-Level Analysis

**Transactions vs. Total Amount Scatter** (by customer):
- Log-log scale plot
- **Fraud customers**: Higher total amounts with fewer transactions
- **Legitimate customers**: More dispersed pattern
- **Finding**: Fraudsters maximize value per transaction

**Pattern Recognition**:
- Top-right quadrant (high transactions, high amount) = possible business use or fraud
- Bottom-right (low transactions, high amount) = high fraud concentration
- Top-left (high transactions, low amount) = card testing

## Data Preprocessing Insights

### Timestamp Decomposition

**Original**: ISO 8601 datetime string
**Extracted Features**:
- year (2024)
- month (10)
- day (1-31)
- hour (0-23)
- day_of_week (0-6, Monday=0)

**Rationale**: Capture temporal patterns at different granularities

**Findings**:
- Year: Constant (removed from model)
- Month: Low variance (October only)
- Day: Some variation, but not strong predictor
- Hour: Strong predictor (kept)
- Day of week: Moderate predictor (weekend flag)

### Velocity Last Hour Parsing

**Original Format**: JSON string
```json
{
  "num_transactions": 1197,
  "total_amount": 33498556.08,
  "unique_merchants": 105,
  "unique_countries": 12,
  "max_single_amount": 1925480.63
}
```

**Parsing Strategy**:
```python
import ast
parsed = ast.literal_eval(velocity_string)
```

**Extracted Features**: 5 new numeric columns
**Impact**: Significant improvement in model performance - velocity metrics are top predictors

### Boolean to Integer Conversion

**Rationale**: Some models handle integers better than booleans

**Converted Features**:
- card_present: True/False → 1/0
- distance_from_home: True/False → 1/0
- high_risk_merchant: True/False → 1/0
- weekend_transaction: True/False → 1/0
- is_fraud: True/False → 1/0

**Alternative**: Keep as boolean for tree-based models; convert for linear models

### One-Hot Encoding

**Applied to**:
- merchant (top 20 + "Other")
- merchant_type
- merchant_category
- country
- city
- device
- channel
- city_size
- card_type (ordinal encoding instead)

**Result**: Explosion from 24 to 113 columns
**Post-Selection**: Reduced to 38 columns based on correlation and importance

**Consideration**: High cardinality (merchant, device_fingerprint, IP) excluded to prevent overfitting

### Currency Conversion

**Conversion Rates Applied**:
| Currency | Rate to USD |
|----------|-------------|
| EUR | 1.06 |
| CAD | 0.72 |
| RUB | 0.01 |
| NGN | 0.0006 |
| SGD | 0.75 |
| MXN | 0.049 |
| BRL | 0.17 |
| AUD | 0.65 |
| JPY | 0.0065 |
| GBP | 1.28 |

**Impact**:
- Enables cross-currency pattern learning
- Standardizes amount-based thresholds
- Critical for global fraud detection

**Limitation**: Static rates; production system should use real-time FX rates

### Outlier Treatment

**Philosophy**: Retain outliers in fraud detection
- Outliers often ARE the fraud
- Removing them eliminates the signal
- Scaling/transformation handles extreme values

**Approach Taken**:
1. Identify outliers (IQR method)
2. Document outlier counts
3. **Do NOT remove** outliers
4. Apply StandardScaler to handle scale
5. Model learns to handle extremes

**Alternative Considered**: Winsorization (cap extremes at percentile)
**Decision**: Retained all values for maximum fraud signal

## Feature Engineering Rationale

### Why These Features Work

#### suspicious_device
- **Aggregates**: NFC Payment, Magnetic Stripe, Chip Reader
- **Rationale**: All three indicate physical card access
- **Result**: Single binary feature vs. three sparse columns
- **Impact**: Became top-3 most important feature

#### high_risk_transaction
- **Combines**: high_risk_country AND suspicious_device
- **Rationale**: Compound risk factors amplify each other
- **Result**: Near-perfect fraud indicator
- **Impact**: Top-5 most important feature

#### is_high_amount / is_low_amount
- **Thresholds**: $1,000 and $100
- **Rationale**: Simple, interpretable business rules
- **Result**: Easy to explain to stakeholders
- **Impact**: Moderate importance, high business value

#### is_off_hours
- **Threshold**: Outside 9 AM - 5 PM
- **Rationale**: Behavioral pattern detection
- **Result**: Context for time-based anomalies
- **Impact**: Low direct importance, but valuable in combinations

#### USD Conversion
- **Normalizes**: All currencies to single standard
- **Rationale**: Enable global pattern learning
- **Result**: Unified amount-based features
- **Impact**: Essential for model to learn amount thresholds

#### micro_transaction_risk
- **Formula**: (num_transactions > 20) AND (total_amount < $100)
- **Rationale**: Detect card testing behavior
- **Result**: Early warning system
- **Impact**: Catches fraud before major loss

## Statistical Distribution Summary

### Skewness Analysis

| Variable | Skewness | Interpretation |
|----------|----------|----------------|
| amount | 12.01 | Extreme right skew |
| total_amount | 6.54 | Strong right skew |
| num_transactions | 1.55 | Moderate right skew |
| max_single_amount | 1.19 | Mild right skew |
| unique_merchants | -1.17 | Mild left skew |
| unique_countries | -2.22 | Strong left skew |
| transaction_hour | -0.14 | Nearly symmetric |
| card_number | -0.81 | Mild left skew |

**Right-Skewed Variables** (long tail to right):
- Indicate rare high values
- Require log transformation for visualization
- StandardScaler handles for modeling

**Left-Skewed Variables** (long tail to left):
- Indicate concentration at high end
- unique_countries: Most have many countries (cumulative metric)
- unique_merchants: Similar pattern

**Symmetric Variables**:
- transaction_hour: By design (24-hour cycle)
- No transformation needed

## Model-Ready Dataset Characteristics

### Final Dataset Shape
- **Rows**: 250,000 transactions
- **Columns**: 38 features
- **Train**: 200,000 (80%)
- **Test**: 50,000 (20%)
- **Stratification**: Yes (maintains 5% fraud rate)

### Data Types (Final)
- **Float64**: 4 (amount-based features)
- **Int64**: 30 (binary flags, counts, one-hot encoded)
- **Int32**: 5 (datetime-derived)
- **Object**: 0 (all encoded)

### Missing Values: 0
**Quality Assurance**:
- No imputation required
- Complete dataset
- High data quality

### Memory Usage
- **Train**: ~41 MB (200k × 38)
- **Test**: ~10 MB (50k × 38)
- **Total**: ~51 MB (manageable for any system)

## Key Insights for Production

1. **Stratified Sampling Essential**: Maintains fraud rate across splits
2. **Feature Engineering Drives Performance**: Compound features outperform raw
3. **Currency Normalization Critical**: Enables global pattern learning
4. **Outliers Are Signal**: Don't remove in fraud detection
5. **Cardinality Matters**: Exclude ultra-high cardinality (device fingerprint, IP)
6. **Temporal Decomposition Valuable**: Hour matters, date less so
7. **Velocity Metrics Powerful**: Parsed JSON provides top features
8. **Geographic Risk Real**: Country-specific patterns exist
9. **Amount Distribution Skewed**: Log scale required for visualization
10. **Class Imbalance Standard**: Typical of fraud datasets, handle with stratification

## Visualization Recommendations

### Required Plots for Fraud Analysis
1. **Distribution Plots**: Histogram + KDE for amount variables
2. **Box Plots**: Outlier detection for numeric features
3. **Bar Plots**: Fraud rate by categorical features
4. **Scatter Plots**: Amount vs. max_single_amount (log scale)
5. **Line Plots**: Temporal patterns (hour of day)
6. **Heatmap**: Correlation matrix (filtered > 0.5)
7. **Feature Importance**: Bar chart of top features
8. **ROC Curve**: Model performance visualization
9. **Confusion Matrix**: Classification results

### Visualization Best Practices
- **Use log scale** for right-skewed amount variables
- **Color by fraud status** to show separation
- **Filter correlations** to focus on strong relationships (> 0.5)
- **Annotate thresholds** on plots (e.g., banking hours on time plots)
- **Show sample sizes** on categorical plots

## Next Steps from EDA

1. **Model Selection**: XGBoost chosen based on feature types and performance
2. **Hyperparameter Tuning**: Grid search on best-performing model
3. **Threshold Optimization**: Adjust fraud probability cutoff for business needs
4. **Feature Monitoring**: Track distribution drift in production
5. **A/B Testing**: Compare model versions in production
6. **Explainability**: Implement SHAP for instance-level explanations
7. **Real-Time Scoring**: Deploy model with sub-second inference
8. **Continuous Learning**: Retrain on new fraud patterns regularly
