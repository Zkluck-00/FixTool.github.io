import { CommonModule, CurrencyPipe } from '@angular/common';
import { Component, inject, OnInit } from '@angular/core';
import { FormBuilder, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { ApiService } from '../core/api.service';
import { apiErrorMessage, Product, ProductPayload } from '../core/models';

@Component({
  selector: 'app-products',
  standalone: true,
  imports: [CommonModule, CurrencyPipe, FormsModule, ReactiveFormsModule],
  templateUrl: './products.component.html',
})
export class ProductsComponent implements OnInit {
  private readonly api = inject(ApiService);
  private readonly fb = inject(FormBuilder);
  products: Product[] = [];
  query = '';
  loading = false;
  modalOpen = false;
  editing: Product | null = null;
  message = '';
  error = '';
  readonly form = this.fb.nonNullable.group({
    name: ['', [Validators.required, Validators.minLength(2), Validators.maxLength(120)]],
    sku: ['', [Validators.required, Validators.minLength(2), Validators.maxLength(40), Validators.pattern(/^[A-Za-z0-9][A-Za-z0-9._-]*$/)]],
    category: ['', [Validators.required, Validators.minLength(2), Validators.maxLength(60)]],
    description: [''],
    cost_price: [0, [Validators.required, Validators.min(0)]],
    sale_price: [0, [Validators.required, Validators.min(0.01)]],
    stock: [0, [Validators.required, Validators.min(0), Validators.max(1000000)]],
    min_stock: [0, [Validators.required, Validators.min(0), Validators.max(1000000)]],
  });

  ngOnInit(): void { this.load(); }

  load(): void {
    this.api.products(this.query).subscribe({
      next: (products) => this.products = products,
      error: (error: unknown) => this.error = apiErrorMessage(error),
    });
  }

  openCreate(): void {
    this.editing = null;
    this.form.reset({ name: '', sku: '', category: '', description: '', cost_price: 0, sale_price: 0, stock: 0, min_stock: 0 });
    this.message = '';
    this.error = '';
    this.modalOpen = true;
  }

  openEdit(product: Product): void {
    this.editing = product;
    this.form.reset({
      name: product.name, sku: product.sku, category: product.category, description: product.description ?? '',
      cost_price: Number(product.cost_price), sale_price: Number(product.sale_price), stock: product.stock, min_stock: product.min_stock,
    });
    this.message = '';
    this.error = '';
    this.modalOpen = true;
  }

  save(): void {
    if (this.form.invalid || this.loading) {
      this.form.markAllAsTouched();
      return;
    }
    const raw = this.form.getRawValue();
    const payload: ProductPayload = {
      ...raw,
      name: raw.name.trim(), sku: raw.sku.trim().toUpperCase(), category: raw.category.trim(),
      description: raw.description.trim() || null,
      cost_price: Number(raw.cost_price), sale_price: Number(raw.sale_price), stock: Number(raw.stock), min_stock: Number(raw.min_stock),
    };
    this.loading = true;
    this.error = '';
    const request = this.editing ? this.api.updateProduct(this.editing.id, payload) : this.api.createProduct(payload);
    request.subscribe({
      next: () => {
        this.loading = false;
        this.modalOpen = false;
        this.message = this.editing ? 'Producto actualizado.' : 'Producto registrado.';
        this.editing = null;
        this.load();
      },
      error: (error: unknown) => {
        this.loading = false;
        this.error = apiErrorMessage(error);
      },
    });
  }

  archive(product: Product): void {
    if (!window.confirm(`¿Retirar “${product.name}” del catálogo? El historial de ventas se conservará.`)) return;
    this.api.archiveProduct(product.id).subscribe({
      next: () => { this.message = 'Producto retirado del catálogo.'; this.load(); },
      error: (error: unknown) => this.error = apiErrorMessage(error),
    });
  }
}

