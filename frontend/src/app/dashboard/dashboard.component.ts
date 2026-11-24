import { CommonModule, CurrencyPipe, DatePipe } from '@angular/common';
import { Component, inject, OnInit } from '@angular/core';
import { ApiService } from '../core/api.service';
import { DashboardSummary, apiErrorMessage } from '../core/models';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, CurrencyPipe, DatePipe],
  templateUrl: './dashboard.component.html',
})
export class DashboardComponent implements OnInit {
  private readonly api = inject(ApiService);
  summary: DashboardSummary | null = null;
  error = '';
  readonly today = new Date();

  ngOnInit(): void {
    this.api.dashboard().subscribe({
      next: (summary) => this.summary = summary,
      error: (error: unknown) => this.error = apiErrorMessage(error),
    });
  }
}

