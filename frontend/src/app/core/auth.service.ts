import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
import { environment } from '../../environments/environment';
import { AuthResponse, UserRole } from './models';

const TOKEN_KEY = 'fixtool.access_token';
const ROLE_KEY = 'fixtool.role';
const NAME_KEY = 'fixtool.full_name';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = environment.apiUrl;

  login(username: string, password: string): Observable<AuthResponse> {
    return this.http.post<AuthResponse>(`${this.baseUrl}/auth/login`, { username, password }).pipe(
      tap((session) => {
        localStorage.setItem(TOKEN_KEY, session.access_token);
        localStorage.setItem(ROLE_KEY, session.role);
        localStorage.setItem(NAME_KEY, session.full_name);
      }),
    );
  }

  logout(): void {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(ROLE_KEY);
    localStorage.removeItem(NAME_KEY);
  }

  get token(): string | null { return localStorage.getItem(TOKEN_KEY); }
  get role(): UserRole | null { return localStorage.getItem(ROLE_KEY) as UserRole | null; }
  get fullName(): string { return localStorage.getItem(NAME_KEY) ?? 'Usuario'; }
  get isAuthenticated(): boolean { return Boolean(this.token && this.role); }
  get isAdmin(): boolean { return this.role === 'admin'; }
}

