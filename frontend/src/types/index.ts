export type Language = 'hi' | 'kn' | 'en';

export interface User {
  id: string;
  name: string;
  mobile: string;
  preferred_language: Language;
  created_at: string;
  shop?: Shop;
}

export interface Shop {
  id: string;
  shop_name: string;
  currency: string;
  created_at: string;
}

export interface Customer {
  id: string;
  shop_id: string;
  name: string;
  mobile?: string;
  address?: string;
  notes?: string;
  created_at: string;
  archived_at?: string;
  outstanding_balance: number;
  total_credit: number;
  total_payment: number;
  transaction_count: number;
  last_transaction_date?: string;
}

export interface Transaction {
  id: string;
  shop_id: string;
  customer_id: string;
  customer_name?: string;
  type: 'CREDIT' | 'PAYMENT';
  amount: number;
  currency: string;
  transaction_date: string;
  created_at: string;
  description?: string;
  input_method: 'VOICE' | 'MANUAL' | 'OFFLINE_SYNC';
  status: 'CONFIRMED' | 'PENDING' | 'REVERSED';
  idempotency_key?: string;
  reversal_of_transaction_id?: string;
}

export interface ParsedEvent {
  event_id: string;
  intent: string;
  customer_id?: string;
  customer_name?: string;
  matched_customers: Array<{ id: string; name: string; mobile?: string }>;
  amount?: number;
  currency: string;
  transaction_date: string;
  date_label: string;
  description?: string;
  confidence: number;
  is_ambiguous: boolean;
  clarification_question?: string;
  missing_fields: string[];
}

export interface VoiceInterpretResult {
  raw_transcript: string;
  detected_language: Language;
  primary_intent: string;
  events: ParsedEvent[];
  requires_clarification: boolean;
  clarification_prompt?: string;
  spoken_clarification?: string;
  can_execute_directly: boolean;
}

export interface VoiceConfirmItem {
  customer_id: string;
  customer_name: string;
  type: 'CREDIT' | 'PAYMENT';
  amount: number;
  transaction_date: string;
  description?: string;
}

export interface VoiceConfirmRequest {
  items: VoiceConfirmItem[];
  language: string;
}

export interface VoiceConfirmResponse {
  success: boolean;
  created_transactions: any[];
  customer_id: string;
  customer_name: string;
  new_outstanding_balance: number;
  formatted_balance: string;
  spoken_response: string;
  text_response: string;
}

export interface DashboardSummary {
  total_outstanding: number;
  today_credit: number;
  today_payment: number;
  total_customers: number;
}

export interface DailyReport {
  report_date: string;
  total_credit: number;
  total_payment: number;
  net_change: number;
  transaction_count: number;
  customers_served: number;
}

export interface MonthlyReport {
  month_name: string;
  year: number;
  total_credit: number;
  total_payment: number;
  net_credit_given: number;
  current_total_outstanding: number;
  active_customers_count: number;
  top_debtors: Array<{
    customer_id: string;
    customer_name: string;
    outstanding_balance: number;
  }>;
  daily_trends: Array<{
    date: string;
    credit: number;
    payment: number;
  }>;
}

export interface OfflineQueueItem {
  operation_id: string;
  operation_type: 'CREATE_TRANSACTION' | 'CREATE_CUSTOMER';
  payload: any;
  client_timestamp: string;
  status: 'SAVED_LOCALLY' | 'PENDING_SYNC' | 'SYNCED' | 'FAILED';
}
