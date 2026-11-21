import {
  Customer,
  Transaction,
  VoiceInterpretResult,
  VoiceConfirmRequest,
  VoiceConfirmResponse,
  DashboardSummary,
  DailyReport,
  MonthlyReport,
  OfflineQueueItem,
  ReceiptScanResult,
  ConversationalTurnResponse
} from '../types';

const API_BASE = import.meta.env.VITE_API_URL || '/api';

export function getAuthToken(): string | null {
  return localStorage.getItem('bolkhata_token');
}

export function setAuthToken(token: string): void {
  localStorage.setItem('bolkhata_token', token);
}

export function clearAuthToken(): void {
  localStorage.removeItem('bolkhata_token');
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const token = getAuthToken();
  const headers = new Headers(options.headers || {});
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }
  if (!headers.has('Content-Type') && !(options.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json');
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (response.status === 401 && token && !endpoint.startsWith('/auth/')) {
    // Expired session: the backend no longer falls back to the demo shop, so log in again.
    clearAuthToken();
    window.location.href = '/welcome';
  }

  if (!response.ok) {
    let errMsg = `Request failed (${response.status})`;
    try {
      const errData = await response.json();
      errMsg = errData.detail || errData.message || errMsg;
    } catch {}
    throw new Error(errMsg);
  }

  return response.json();
}

export const api = {
  // Auth
  login: (credentials: { mobile: string; password: string }) =>
    request<any>('/auth/login', { method: 'POST', body: JSON.stringify(credentials) }),

  register: (data: any) =>
    request<any>('/auth/register', { method: 'POST', body: JSON.stringify(data) }),

  demoLogin: () =>
    request<any>('/auth/demo', { method: 'POST' }),

  getMe: () =>
    request<any>('/auth/me'),

  logout: () => {
    clearAuthToken();
    return request<any>('/auth/logout', { method: 'POST' }).catch(() => {});
  },

  // Customers
  getCustomers: (search?: string, hasBalanceOnly?: boolean) => {
    const params = new URLSearchParams();
    if (search) params.append('search', search);
    if (hasBalanceOnly) params.append('has_balance_only', 'true');
    const qs = params.toString();
    return request<Customer[]>(`/customers${qs ? `?${qs}` : ''}`);
  },

  getCustomer: (id: string) =>
    request<Customer>(`/customers/${id}`),

  createCustomer: (data: { name: string; mobile?: string; address?: string; notes?: string }) =>
    request<Customer>('/customers', { method: 'POST', body: JSON.stringify(data) }),

  updateCustomer: (id: string, data: Partial<Customer>) =>
    request<Customer>(`/customers/${id}`, { method: 'PUT', body: JSON.stringify(data) }),

  archiveCustomer: (id: string) =>
    request<{ message: string }>(`/customers/${id}`, { method: 'DELETE' }),

  getCustomerLedger: (id: string) =>
    request<{
      customer_id: string;
      customer_name: string;
      outstanding_balance: number;
      total_credit: number;
      total_payment: number;
      transactions: Transaction[];
    }>(`/customers/${id}/ledger`),

  // Transactions
  getTransactions: (filters: {
    customer_id?: string;
    type?: string;
    period?: string;
    status?: string;
    sort?: string;
    limit?: number;
    offset?: number;
  } = {}) => {
    const params = new URLSearchParams();
    if (filters.customer_id) params.append('customer_id', filters.customer_id);
    if (filters.type) params.append('type', filters.type);
    if (filters.period) params.append('period', filters.period);
    if (filters.status) params.append('status', filters.status);
    if (filters.sort) params.append('sort', filters.sort);
    if (filters.limit) params.append('limit', filters.limit.toString());
    if (filters.offset) params.append('offset', filters.offset.toString());
    const qs = params.toString();
    return request<Transaction[]>(`/transactions${qs ? `?${qs}` : ''}`);
  },

  createTransaction: (data: {
    customer_id: string;
    type: 'CREDIT' | 'PAYMENT';
    amount: number;
    transaction_date?: string;
    description?: string;
    input_method?: string;
    idempotency_key?: string;
  }) =>
    request<Transaction>('/transactions', { method: 'POST', body: JSON.stringify(data) }),

  correctTransaction: (id: string, data: { corrected_amount: number; reason?: string }) =>
    request<Transaction>(`/transactions/${id}/correct`, { method: 'POST', body: JSON.stringify(data) }),

  reverseTransaction: (id: string, data: { reason?: string }) =>
    request<{ message: string; original_transaction_id: string; reversal_transaction_id: string }>(
      `/transactions/${id}/reverse`,
      { method: 'POST', body: JSON.stringify(data) }
    ),

  // Voice AI
  interpretVoice: (text: string, language?: string) =>
    request<VoiceInterpretResult>('/voice/interpret', {
      method: 'POST',
      body: JSON.stringify({ text, language, input_source: 'VOICE' }),
    }),

  conversationalTurn: (data: { session_id?: string; text: string; language?: string }) =>
    request<ConversationalTurnResponse>('/voice/conversational-turn', {
      method: 'POST',
      body: JSON.stringify({ session_id: data.session_id || 'default', text: data.text, language: data.language }),
    }),

  confirmVoiceTransactions: (data: VoiceConfirmRequest) =>
    request<VoiceConfirmResponse>('/voice/confirm', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  transcribeAudioBlob: async (audioBlob: Blob, language?: string) => {
    const formData = new FormData();
    formData.append('file', audioBlob, 'voice_recording.webm');
    if (language) formData.append('language', language);
    return request<{ transcript: string; provider: string; confidence: number }>('/voice/transcribe', {
      method: 'POST',
      body: formData,
    });
  },

  // Receipt & Bill OCR
  scanReceipt: async (file: File | Blob) => {
    const formData = new FormData();
    formData.append('file', file, 'receipt.jpg');
    return request<ReceiptScanResult>('/receipt/scan', {
      method: 'POST',
      body: formData,
    });
  },

  confirmReceipt: (data: {
    vendor_or_customer_name: string;
    amount: number;
    type?: string;
    transaction_date?: string;
    description?: string;
  }) =>
    request<{
      success: boolean;
      transaction_id: string;
      customer_id: string;
      customer_name: string;
      amount: number;
      type: string;
      new_balance: number;
      message: string;
    }>('/receipt/confirm', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // Assistant Query
  queryAssistant: (query: string, language?: string) =>
    request<{ query: string; answer: string; spoken_answer: string; data?: any }>('/assistant/query', {
      method: 'POST',
      body: JSON.stringify({ query, language }),
    }),

  // Reports
  getDashboardSummary: () =>
    request<DashboardSummary>('/reports/outstanding'),

  getWeeklyReport: () =>
    request<any>('/reports/weekly'),

  getDailyReport: (date?: string) => {
    const qs = date ? `?target_date=${date}` : '';
    return request<DailyReport>(`/reports/daily${qs}`);
  },

  getMonthlyReport: (year?: number, month?: number) => {
    const params = new URLSearchParams();
    if (year) params.append('year', year.toString());
    if (month) params.append('month', month.toString());
    const qs = params.toString();
    return request<MonthlyReport>(`/reports/monthly${qs ? `?${qs}` : ''}`);
  },

  // Sync
  pushOfflineQueue: (items: OfflineQueueItem[]) =>
    request<{ processed_count: number; results: any[] }>('/sync/push', {
      method: 'POST',
      body: JSON.stringify({ items }),
    }),

  // Reset Demo
  resetDemoData: () =>
    request<{ message: string }>('/seed/reset', { method: 'POST' }),
};
