export interface Transaction {
  amount: number;
  card_number: string;
  card_present: boolean;
  card_type: string;
  channel: string;
  city: string;
  city_size: string;
  country: string;
  currency: string;
  customer_id: string;
  device: string;
  device_fingerprint: string;
  distance_from_home: number;
  high_risk_merchant: boolean;
  ip_address: string;
  merchant: string;
  merchant_category: string;
  merchant_type: string;
  transaction_hour: number;
  timestamp: string;
  velocity_last_hour: {
    num_transactions: number;
    total_amount: number;
    unique_merchants: number;
    unique_countries: number;
    max_single_amount: number;
  };
  weekend_transaction: boolean;
}