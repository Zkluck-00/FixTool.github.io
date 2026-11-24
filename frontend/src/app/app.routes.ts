import { Routes } from '@angular/router';
import { authGuard, adminGuard } from './core/auth.guard';

export const routes: Routes = [
  { path: 'login', loadComponent: () => import('./auth/login.component').then((m) => m.LoginComponent) },
  {
    path: 'app',
    canActivate: [authGuard],
    loadComponent: () => import('./layout/shell.component').then((m) => m.ShellComponent),
    children: [
      { path: '', pathMatch: 'full', redirectTo: 'pos' },
      { path: 'dashboard', canActivate: [adminGuard], loadComponent: () => import('./dashboard/dashboard.component').then((m) => m.DashboardComponent) },
      { path: 'products', canActivate: [adminGuard], loadComponent: () => import('./products/products.component').then((m) => m.ProductsComponent) },
      { path: 'team', canActivate: [adminGuard], loadComponent: () => import('./team/team.component').then((m) => m.TeamComponent) },
      { path: 'pos', loadComponent: () => import('./sales/pos.component').then((m) => m.PosComponent) },
      { path: 'history', canActivate: [adminGuard], loadComponent: () => import('./sales/history.component').then((m) => m.HistoryComponent) },
    ],
  },
  { path: '', pathMatch: 'full', redirectTo: 'login' },
  { path: '**', redirectTo: 'app' },
];

