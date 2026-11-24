import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { DashboardSummary, PaymentMethod, Product, ProductForSale, ProductPayload, Sale, User } from './models';

@Injectable({ providedIn: 'root' })
export class ApiService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = environment.apiUrl;

  products(q = '', available = false): Observable<Product[]> {
    let params = new HttpParams().set('available', String(available));
    if (q.trim()) params = params.set('q', q.trim());
    return this.http.get<Product[]>(`${this.baseUrl}/products`, { params });
  }

  catalog(q = ''): Observable<ProductForSale[]> {
    let params = new HttpParams().set('available', 'true');
    if (q.trim()) params = params.set('q', q.trim());
    return this.http.get<ProductForSale[]>(`${this.baseUrl}/products/catalog`, { params });
  }

  createProduct(payload: ProductPayload): Observable<Product> {
    return this.http.post<Product>(`${this.baseUrl}/products`, payload);
  }

  updateProduct(id: string, payload: ProductPayload): Observable<Product> {
    return this.http.put<Product>(`${this.baseUrl}/products/${id}`, payload);
  }

  archiveProduct(id: string): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/products/${id}`);
  }

  createSale(payload: { items: { product_id: string; quantity: number }[]; payment_method: PaymentMethod; amount_received?: number }): Observable<Sale> {
    return this.http.post<Sale>(`${this.baseUrl}/sales`, payload);
  }

  sales(limit = 100): Observable<Sale[]> {
    return this.http.get<Sale[]>(`${this.baseUrl}/sales`, { params: new HttpParams().set('limit', String(limit)) });
  }

  dashboard(): Observable<DashboardSummary> {
    return this.http.get<DashboardSummary>(`${this.baseUrl}/dashboard/summary`);
  }

  users(): Observable<User[]> {
    return this.http.get<User[]>(`${this.baseUrl}/users`);
  }

  createSeller(payload: { username: string; full_name: string; password: string }): Observable<User> {
    return this.http.post<User>(`${this.baseUrl}/users`, payload);
  }
}

