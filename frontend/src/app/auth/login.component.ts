import { CommonModule } from '@angular/common';
import { Component, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { AuthService } from '../core/auth.service';
import { apiErrorMessage } from '../core/models';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './login.component.html',
})
export class LoginComponent {
  private readonly fb = inject(FormBuilder);
  private readonly auth = inject(AuthService);
  private readonly router = inject(Router);
  private readonly route = inject(ActivatedRoute);
  readonly form = this.fb.nonNullable.group({
    username: ['', [Validators.required, Validators.minLength(3), Validators.maxLength(50), Validators.pattern(/^[A-Za-z0-9._-]+$/)]],
    password: ['', [Validators.required, Validators.maxLength(128)]],
  });
  loading = false;
  error = '';

  submit(): void {
    if (this.form.invalid || this.loading) {
      this.form.markAllAsTouched();
      return;
    }
    this.error = '';
    this.loading = true;
    const { username, password } = this.form.getRawValue();
    this.auth.login(username.trim(), password).subscribe({
      next: (session) => {
        this.loading = false;
        const redirect = this.route.snapshot.queryParamMap.get('returnUrl');
        this.router.navigateByUrl(redirect || (session.role === 'admin' ? '/app/dashboard' : '/app/pos'));
      },
      error: (error: unknown) => {
        this.loading = false;
        this.error = apiErrorMessage(error);
      },
    });
  }
}

