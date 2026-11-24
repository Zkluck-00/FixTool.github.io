import { CommonModule, DatePipe } from '@angular/common';
import { Component, inject, OnInit } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { ApiService } from '../core/api.service';
import { apiErrorMessage, User } from '../core/models';

@Component({
  selector: 'app-team',
  standalone: true,
  imports: [CommonModule, DatePipe, ReactiveFormsModule],
  templateUrl: './team.component.html',
})
export class TeamComponent implements OnInit {
  private readonly api = inject(ApiService);
  private readonly fb = inject(FormBuilder);
  users: User[] = [];
  saving = false;
  error = '';
  message = '';
  readonly form = this.fb.nonNullable.group({
    full_name: ['', [Validators.required, Validators.minLength(2), Validators.maxLength(120), Validators.pattern(/.*\S.*/)]],
    username: ['', [Validators.required, Validators.minLength(3), Validators.maxLength(50), Validators.pattern(/^[A-Za-z0-9._-]+$/)]],
    password: ['', [Validators.required, Validators.minLength(10), Validators.maxLength(128)]],
  });

  ngOnInit(): void { this.load(); }

  load(): void {
    this.api.users().subscribe({
      next: (users) => this.users = users,
      error: (error: unknown) => this.error = apiErrorMessage(error),
    });
  }

  create(): void {
    if (this.form.invalid || this.saving) {
      this.form.markAllAsTouched();
      return;
    }
    const raw = this.form.getRawValue();
    this.saving = true;
    this.error = '';
    this.api.createSeller({ ...raw, full_name: raw.full_name.trim(), username: raw.username.trim().toLowerCase() }).subscribe({
      next: () => {
        this.saving = false;
        this.message = 'La cuenta del vendedor se creó correctamente.';
        this.form.reset({ full_name: '', username: '', password: '' });
        this.load();
      },
      error: (error: unknown) => {
        this.saving = false;
        this.error = apiErrorMessage(error);
      },
    });
  }
}

