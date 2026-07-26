import React from 'react';
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';
import type { UserRole } from '../stores/authStore';

const ROLE_HIERARCHY: Record<UserRole, number> = {
  investigator: 0,
  supervisor: 1,
  admin: 2,
};

const ROUTE_ROLES: Record<string, UserRole> = {
  '/admin': 'admin',
  '/settings': 'supervisor',
};

export const ProtectedRoute: React.FC = () => {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const user = useAuthStore((s) => s.user);
  const location = useLocation();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  const requiredRole = ROUTE_ROLES[location.pathname];
  if (requiredRole && user) {
    const userLevel = ROLE_HIERARCHY[user.role] ?? 0;
    const requiredLevel = ROLE_HIERARCHY[requiredRole] ?? 0;
    if (userLevel < requiredLevel) {
      return <Navigate to="/dashboard" replace />;
    }
  }

  return <Outlet />;
};
