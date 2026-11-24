import { CommonModule, CurrencyPipe } from '@angular/common';
import { Component, inject, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../core/api.service';
import { apiErrorMessage, PaymentMethod, ProductForSale, Sale } from '../core/models';

interface CartLine { product: ProductForSale; quantity: number; }

@Component({
  selector: 'app-pos',
  standalone: true,
  imports: [CommonModule, CurrencyPipe, FormsModule],
  templateUrl: './pos.component.html',
})
export class PosComponent implements OnInit {
  private readonly api = inject(ApiService);
  products: ProductForSale[] = [];
  cart: CartLine[] = [];
  query = '';
  paymentMethod: PaymentMethod = 'cash';
  amountReceived: number | null = null;
  loading = false;
  error = '';
  completedSale: Sale | null = null;

  ngOnInit(): void { this.loadProducts(); }

  get total(): number {
    return this.cart.reduce((sum, line) => sum + Number(line.product.sale_price) * line.quantity, 0);
  }

  get change(): number {
    return Math.max(0, Number(this.amountReceived ?? 0) - this.total);
  }

  loadProducts(): void {
    this.api.catalog(this.query).subscribe({
      next: (products) => this.products = products,
      error: (error: unknown) => this.error = apiErrorMessage(error),
    });
  }

  add(product: ProductForSale): void {
    this.completedSale = null;
    this.error = '';
    const line = this.cart.find((item) => item.product.id === product.id);
    if (line) {
      if (line.quantity >= product.stock) {
        this.error = `Solo quedan ${product.stock} unidades de ${product.name}.`;
        return;
      }
      line.quantity += 1;
    } else {
      this.cart = [...this.cart, { product, quantity: 1 }];
    }
  }

  adjust(productId: string, amount: number): void {
    this.cart = this.cart
      .map((line) => line.product.id === productId ? { ...line, quantity: line.quantity + amount } : line)
      .filter((line) => line.quantity > 0);
    const line = this.cart.find((item) => item.product.id === productId);
    if (line && line.quantity > line.product.stock) line.quantity = line.product.stock;
  }

  remove(productId: string): void { this.cart = this.cart.filter((line) => line.product.id !== productId); }

  checkout(): void {
    if (!this.cart.length || this.loading) return;
    if (this.paymentMethod === 'cash' && Number(this.amountReceived ?? 0) < this.total) {
      this.error = 'El efectivo recibido debe ser igual o mayor al total.';
      return;
    }
    this.loading = true;
    this.error = '';
    const payload = {
      items: this.cart.map((line) => ({ product_id: line.product.id, quantity: line.quantity })),
      payment_method: this.paymentMethod,
      ...(this.paymentMethod === 'cash' ? { amount_received: Number(this.amountReceived) } : {}),
    };
    this.api.createSale(payload).subscribe({
      next: (sale) => {
        this.loading = false;
        this.completedSale = sale;
        this.cart = [];
        this.amountReceived = null;
        this.loadProducts();
      },
      error: (error: unknown) => {
        this.loading = false;
        this.error = apiErrorMessage(error);
        this.loadProducts();
      },
    });
  }
}

