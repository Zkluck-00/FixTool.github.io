import { CommonModule, CurrencyPipe, DatePipe } from '@angular/common';
import { Component, inject, OnInit } from '@angular/core';
import { ApiService } from '../core/api.service';
import { apiErrorMessage, Sale } from '../core/models';

@Component({
  selector: 'app-history',
  standalone: true,
  imports: [CommonModule, CurrencyPipe, DatePipe],
  templateUrl: './history.component.html',
})
export class HistoryComponent implements OnInit {
  private readonly api = inject(ApiService);
  sales: Sale[] = [];
  error = '';

  ngOnInit(): void {
    this.api.sales().subscribe({
      next: (sales) => this.sales = sales,
      error: (error: unknown) => this.error = apiErrorMessage(error),
    });
  }
}

