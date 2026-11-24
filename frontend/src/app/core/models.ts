export type UserRole = 'admin' | 'seller';
export type PaymentMethod = 'cash' | 'card' | 'yape' | 'plin' | 'transfer';

export interface AuthResponse {
  access_token: string;
  token_type: 'bearer';
  role: UserRole;
  full_name: string;
}

export interface User {
  id: string;
  username: string;
  full_name: string;
  role: UserRole;
  active: boolean;
  created_at: string;
}

export interface Product {
  id: string;
  name: string;
  sku: string;
  category: string;
  description: string | null;
  cost_price: number;
  sale_price: number;
  stock: number;
  min_stock: number;
  active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ProductForSale {
  id: string;
  name: string;
  sku: string;
  category: string;
  description: string | null;
  sale_price: number;
  stock: number;
  min_stock: number;
  active: boolean;
}

export interface ProductPayload {
  name: string;
  sku: string;
  category: string;
  description: string | null;
  cost_price: number;
  sale_price: number;
  stock: number;
  min_stock: number;
}

export interface SaleItem {
  id: string;
  product_id: string;
  product_name: string;
  sku: string;
  quantity: number;
  unit_price: number;
}

export interface Sale {
  id: string;
  seller_id: string;
  seller_name: string;
  total: number;
  payment_method: PaymentMethod;
  amount_received: number;
  change_due: number;
  created_at: string;
  items: SaleItem[];
}

export interface DashboardSummary {
  active_products: number;
  low_stock_products: number;
  sales_today: number;
  revenue_today: number;
  recent_sales: Sale[];
}

export function apiErrorMessage(error: any): string {
  const detail = error?.error?.detail;
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail)) return detail.map((item) => item.msg).join(' · ');
  return 'No se pudo completar la operación. Verifica la conexión e inténtalo de nuevo.';
}

