# Admin User Management — Design Spec

## Overview

Add an admin-only user management system. The admin user's sole responsibility is managing other users: creating accounts, updating credentials/roles, and deactivating users. Default admin credentials: `admin` / `admin`.

## Scope

- Backend CRUD API for user management (admin-only endpoints)
- Frontend admin page with user table, add/edit modals, deactivate toggle
- Migration to change default admin password from `admin123` to `admin`
- i18n keys for admin UI in English and Kannada

## Backend

### New file: `backend/app/api/admin.py`

**Endpoints (all require `role="admin"`):**

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/admin/users` | List all users |
| `POST` | `/admin/users` | Create a new user |
| `PUT` | `/admin/users/{user_id}` | Update user fields |
| `DELETE` | `/admin/users/{user_id}` | Soft-delete (set `active=False`) |

**Request/Response models:**

```python
class UserCreate(BaseModel):
    username: str
    password: str
    employee_id: int
    role: str  # "investigator" | "supervisor" | "admin"

class UserUpdate(BaseModel):
    username: str | None = None
    password: str | None = None
    employee_id: int | None = None
    role: str | None = None
    active: bool | None = None

class UserOut(BaseModel):
    user_id: int
    employee_id: int
    username: str
    role: str
    active: bool
    created_at: datetime | None
    updated_at: datetime | None
```

**Guard:** All endpoints use `Depends(require_role("admin"))`.

### Migration update

Modify `002_add_users_table.py` to seed admin with password `admin` instead of `admin123`.

### Router registration

Add `admin_router` to `backend/app/main.py` with prefix `/admin`.

## Frontend

### New file: `frontend/src/pages/AdminPage.tsx`

**Layout:**
- Header: "User Management" with "Add User" button
- Search bar to filter users by username
- Table: username, employee_id, role, status (active/inactive), actions (edit, deactivate)
- Add User modal: username, password, employee_id, role dropdown
- Edit User modal: pre-filled fields, optional password reset, role dropdown, active toggle

**Behavior:**
- Fetches users from `GET /admin/users` on mount
- Create: `POST /admin/users` then refresh list
- Edit: `PUT /admin/users/{id}` then refresh list
- Deactivate: `DELETE /admin/users/{id}` (soft delete) then refresh list
- All API calls include JWT token from auth store
- Error handling: toast/alert on API errors

### Route changes

- Add `/admin` route in `App.tsx` under `ProtectedRoute`
- Add sidebar link for admin role only (check `user.role === 'admin'`)

### i18n keys

Add `admin` namespace to `en.ts` and `kn.ts` with keys for:
- Page title, table headers, modal labels, buttons, status labels, error messages

## Files

| Action | Path |
|--------|------|
| Create | `backend/app/api/admin.py` |
| Modify | `backend/app/main.py` |
| Modify | `backend/alembic/versions/002_add_users_table.py` |
| Create | `frontend/src/pages/AdminPage.tsx` |
| Modify | `frontend/src/App.tsx` |
| Modify | `frontend/src/components/Sidebar.tsx` |
| Modify | `frontend/src/i18n/translations/en.ts` |
| Modify | `frontend/src/i18n/translations/kn.ts` |

## Constraints

- Admin cannot deactivate themselves
- Admin cannot change their own role
- Passwords hashed with bcrypt via existing `hash_password()`
- All endpoints async with SQLAlchemy `AsyncSession`
- Frontend follows existing patterns (Zustand, react-i18next, Tailwind)
