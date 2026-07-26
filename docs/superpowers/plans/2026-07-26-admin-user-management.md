# Admin User Management Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add admin-only user management — CRUD API endpoints and a frontend admin page for managing users (add, edit, deactivate).

**Architecture:** Backend: new `admin.py` router with 4 endpoints protected by `require_role("admin")`. Frontend: new `AdminPage.tsx` with user table, add/edit modals, and deactivate toggle. Migration updates default admin password from `admin123` to `admin`.

**Tech Stack:** FastAPI, SQLAlchemy async, Pydantic, React, Zustand, react-i18next, Tailwind CSS

## Global Constraints

- All backend endpoints use `AsyncSession` with `Depends(get_session)`
- All admin endpoints guarded with `Depends(require_role("admin"))`
- Passwords hashed with `hash_password()` from `app.auth`
- Frontend follows existing patterns: Zustand stores, react-i18next, Tailwind utility classes
- Admin cannot deactivate themselves or change their own role
- Default admin credentials: `admin` / `admin`

---

### Task 1: Backend Admin API Endpoints

**Files:**
- Create: `backend/app/api/admin.py`
- Modify: `backend/app/main.py`

**Interfaces:**
- Consumes: `require_role`, `hash_password` from `app.auth`; `User` model from `app.models.user`; `get_session` from `app.db.session`
- Produces: `admin_router` registered in `main.py` with prefix `/admin`

- [ ] **Step 1: Create `backend/app/api/admin.py`**

```python
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user, hash_password, require_role
from app.db.session import get_session
from app.models.user import User

router = APIRouter(prefix="/admin", tags=["admin"])


class UserCreate(BaseModel):
    username: str
    password: str
    employee_id: int
    role: str


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
    created_at: datetime | None = None
    updated_at: datetime | None = None


@router.get("/users", response_model=list[UserOut])
async def list_users(
    _admin: User = Depends(require_role("admin")),
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(select(User).order_by(User.user_id))
    users = result.scalars().all()
    return [
        UserOut(
            user_id=u.user_id,
            employee_id=u.employee_id,
            username=u.username,
            role=u.role,
            active=u.active,
            created_at=u.created_at,
            updated_at=u.updated_at,
        )
        for u in users
    ]


@router.post("/users", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(
    body: UserCreate,
    _admin: User = Depends(require_role("admin")),
    session: AsyncSession = Depends(get_session),
):
    existing = await session.execute(
        select(User).where((User.username == body.username) | (User.employee_id == body.employee_id))
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or employee_id already exists",
        )

    user = User(
        employee_id=body.employee_id,
        username=body.username,
        password_hash=hash_password(body.password),
        role=body.role,
        active=True,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return UserOut(
        user_id=user.user_id,
        employee_id=user.employee_id,
        username=user.username,
        role=user.role,
        active=user.active,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.put("/users/{user_id}", response_model=UserOut)
async def update_user(
    user_id: int,
    body: UserUpdate,
    admin: User = Depends(require_role("admin")),
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(select(User).where(User.user_id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if user.user_id == admin.user_id and body.role is not None and body.role != admin.role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot change your own role",
        )

    if body.username is not None:
        dup = await session.execute(
            select(User).where(User.username == body.username, User.user_id != user_id)
        )
        if dup.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Username already taken"
            )
        user.username = body.username

    if body.password is not None:
        user.password_hash = hash_password(body.password)

    if body.employee_id is not None:
        dup = await session.execute(
            select(User).where(User.employee_id == body.employee_id, User.user_id != user_id)
        )
        if dup.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Employee ID already taken"
            )
        user.employee_id = body.employee_id

    if body.role is not None:
        user.role = body.role

    if body.active is not None:
        if user.user_id == admin.user_id and not body.active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot deactivate yourself",
            )
        user.active = body.active

    await session.commit()
    await session.refresh(user)
    return UserOut(
        user_id=user.user_id,
        employee_id=user.employee_id,
        username=user.username,
        role=user.role,
        active=user.active,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.delete("/users/{user_id}", status_code=status.HTTP_200_OK)
async def deactivate_user(
    user_id: int,
    admin: User = Depends(require_role("admin")),
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(select(User).where(User.user_id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if user.user_id == admin.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot deactivate yourself",
        )

    user.active = False
    await session.commit()
    return {"detail": f"User {user.username} deactivated"}
```

- [ ] **Step 2: Register admin router in `backend/app/main.py`**

Add import and router registration:

```python
from app.api.admin import router as admin_router
# ... after existing router registrations:
app.include_router(admin_router, prefix="/admin")
```

- [ ] **Step 3: Run ruff check and format**

Run: `source .venv/bin/activate && ruff check backend/app/api/admin.py && ruff format backend/app/api/admin.py`
Expected: All checks passed

- [ ] **Step 4: Commit**

```bash
git add backend/app/api/admin.py backend/app/main.py
git commit -m "feat(backend): add admin user management API endpoints"
```

---

### Task 2: Migration — Change Admin Password

**Files:**
- Modify: `backend/alembic/versions/002_add_users_table.py`

**Interfaces:**
- Consumes: existing migration with seeded users
- Produces: admin user with password `admin` instead of `admin123`

- [ ] **Step 1: Update the admin password hash in the migration**

In `backend/alembic/versions/002_add_users_table.py`, change line 60:

```python
# Before:
"password_hash": pwd_context.hash("admin123"),
# After:
"password_hash": pwd_context.hash("admin"),
```

- [ ] **Step 2: Verify ruff passes**

Run: `source .venv/bin/activate && ruff check backend/alembic/versions/002_add_users_table.py`
Expected: All checks passed

- [ ] **Step 3: Commit**

```bash
git add backend/alembic/versions/002_add_users_table.py
git commit -m "fix(backend): change default admin password to 'admin'"
```

---

### Task 3: Frontend AdminPage Component

**Files:**
- Create: `frontend/src/pages/AdminPage.tsx`

**Interfaces:**
- Consumes: `useAuthStore` from `stores/authStore` (for JWT token)
- Produces: `AdminPage` component exported for routing

- [ ] **Step 1: Create `frontend/src/pages/AdminPage.tsx`**

```tsx
import { useEffect, useState, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuthStore } from '../stores/authStore';

interface User {
  user_id: number;
  employee_id: number;
  username: string;
  role: string;
  active: boolean;
  created_at: string | null;
  updated_at: string | null;
}

interface UserFormData {
  username: string;
  password: string;
  employee_id: number | string;
  role: string;
}

const ROLES = ['investigator', 'supervisor', 'admin'];

export function AdminPage() {
  const { t } = useTranslation();
  const token = useAuthStore((s) => s.token);
  const [users, setUsers] = useState<User[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [form, setForm] = useState<UserFormData>({ username: '', password: '', employee_id: '', role: 'investigator' });
  const [formError, setFormError] = useState('');

  const headers = { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' };

  const fetchUsers = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch('/admin/users', { headers });
      if (!res.ok) throw new Error('Failed to fetch users');
      setUsers(await res.json());
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => { fetchUsers(); }, [fetchUsers]);

  const filtered = users.filter((u) =>
    u.username.toLowerCase().includes(search.toLowerCase()) ||
    String(u.employee_id).includes(search)
  );

  const openAdd = () => {
    setEditingUser(null);
    setForm({ username: '', password: '', employee_id: '', role: 'investigator' });
    setFormError('');
    setShowModal(true);
  };

  const openEdit = (u: User) => {
    setEditingUser(u);
    setForm({ username: u.username, password: '', employee_id: String(u.employee_id), role: u.role });
    setFormError('');
    setShowModal(true);
  };

  const handleSubmit = async () => {
    setFormError('');
    if (!form.username || (!editingUser && !form.password) || !form.employee_id) {
      setFormError(t('admin.fill_required'));
      return;
    }
    try {
      if (editingUser) {
        const body: Record<string, unknown> = {};
        if (form.username !== editingUser.username) body.username = form.username;
        if (form.password) body.password = form.password;
        if (Number(form.employee_id) !== editingUser.employee_id) body.employee_id = Number(form.employee_id);
        if (form.role !== editingUser.role) body.role = form.role;
        const res = await fetch(`/admin/users/${editingUser.user_id}`, {
          method: 'PUT', headers, body: JSON.stringify(body),
        });
        if (!res.ok) {
          const data = await res.json();
          throw new Error(data.detail || 'Update failed');
        }
      } else {
        const res = await fetch('/admin/users', {
          method: 'POST', headers,
          body: JSON.stringify({ username: form.username, password: form.password, employee_id: Number(form.employee_id), role: form.role }),
        });
        if (!res.ok) {
          const data = await res.json();
          throw new Error(data.detail || 'Create failed');
        }
      }
      setShowModal(false);
      fetchUsers();
    } catch (e: unknown) {
      setFormError(e instanceof Error ? e.message : 'Unknown error');
    }
  };

  const handleDeactivate = async (u: User) => {
    if (!confirm(t('admin.confirm_deactivate', { username: u.username }))) return;
    try {
      const res = await fetch(`/admin/users/${u.user_id}`, { method: 'DELETE', headers });
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || 'Deactivate failed');
      }
      fetchUsers();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Unknown error');
    }
  };

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-[var(--color-heading-dark)]">{t('admin.user_management')}</h1>
          <p className="text-sm text-[var(--color-gray-text)] mt-1">{t('admin.manage_users')}</p>
        </div>
        <button onClick={openAdd} className="px-4 py-2 bg-[var(--color-primary-blue)] text-white rounded-[var(--radius-btn)] font-medium hover:opacity-90 transition">
          {t('admin.add_user')}
        </button>
      </div>

      <input
        type="text"
        placeholder={t('admin.search_placeholder')}
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        className="w-full px-4 py-2.5 mb-4 border border-[var(--color-border-light)] rounded-[var(--radius-btn)] bg-white text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-primary-blue)]"
      />

      {error && <div className="mb-4 p-3 bg-red-50 text-red-700 rounded-lg text-sm">{error}</div>}

      {loading ? (
        <div className="text-center py-12 text-[var(--color-gray-text)]">{t('common.loading')}</div>
      ) : (
        <div className="bg-white rounded-[var(--radius-card)] border border-[var(--color-border-light)] overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-[var(--color-border-light)] bg-[var(--color-bg-light)]">
                <th className="text-left px-4 py-3 font-medium text-[var(--color-gray-text)]">{t('admin.username')}</th>
                <th className="text-left px-4 py-3 font-medium text-[var(--color-gray-text)]">{t('admin.employee_id')}</th>
                <th className="text-left px-4 py-3 font-medium text-[var(--color-gray-text)]">{t('admin.role')}</th>
                <th className="text-left px-4 py-3 font-medium text-[var(--color-gray-text)]">{t('admin.status')}</th>
                <th className="text-right px-4 py-3 font-medium text-[var(--color-gray-text)]">{t('admin.actions')}</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((u) => (
                <tr key={u.user_id} className="border-b border-[var(--color-border-light)] last:border-b-0 hover:bg-[var(--color-hover-light)]">
                  <td className="px-4 py-3 font-medium">{u.username}</td>
                  <td className="px-4 py-3 text-[var(--color-gray-text)]">{u.employee_id}</td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${u.role === 'admin' ? 'bg-purple-100 text-purple-700' : u.role === 'supervisor' ? 'bg-amber-100 text-amber-700' : 'bg-blue-100 text-blue-700'}`}>
                      {u.role}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${u.active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                      {u.active ? t('admin.active') : t('admin.inactive')}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right space-x-2">
                    <button onClick={() => openEdit(u)} className="text-[var(--color-primary-blue)] hover:underline text-xs font-medium">{t('admin.edit')}</button>
                    <button onClick={() => handleDeactivate(u)} disabled={!u.active} className="text-red-500 hover:underline text-xs font-medium disabled:opacity-40">{t('admin.deactivate')}</button>
                  </td>
                </tr>
              ))}
              {filtered.length === 0 && (
                <tr><td colSpan={5} className="px-4 py-8 text-center text-[var(--color-gray-text)]">{t('admin.no_users')}</td></tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      {showModal && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
          <div className="bg-white rounded-[var(--radius-card)] p-6 w-full max-w-md shadow-xl">
            <h2 className="text-lg font-bold mb-4">{editingUser ? t('admin.edit_user') : t('admin.add_user')}</h2>
            {formError && <div className="mb-3 p-2 bg-red-50 text-red-700 rounded text-sm">{formError}</div>}
            <div className="space-y-3">
              <div>
                <label className="block text-xs font-medium text-[var(--color-gray-text)] mb-1">{t('admin.username')}</label>
                <input type="text" value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} className="w-full px-3 py-2 border border-[var(--color-border-light)] rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-primary-blue)]" />
              </div>
              <div>
                <label className="block text-xs font-medium text-[var(--color-gray-text)] mb-1">{editingUser ? t('admin.new_password_optional') : t('admin.password')}</label>
                <input type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} className="w-full px-3 py-2 border border-[var(--color-border-light)] rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-primary-blue)]" />
              </div>
              <div>
                <label className="block text-xs font-medium text-[var(--color-gray-text)] mb-1">{t('admin.employee_id')}</label>
                <input type="number" value={form.employee_id} onChange={(e) => setForm({ ...form, employee_id: e.target.value })} className="w-full px-3 py-2 border border-[var(--color-border-light)] rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-primary-blue)]" />
              </div>
              <div>
                <label className="block text-xs font-medium text-[var(--color-gray-text)] mb-1">{t('admin.role')}</label>
                <select value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })} className="w-full px-3 py-2 border border-[var(--color-border-light)] rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-primary-blue)]">
                  {ROLES.map((r) => <option key={r} value={r}>{r}</option>)}
                </select>
              </div>
            </div>
            <div className="flex justify-end gap-2 mt-6">
              <button onClick={() => setShowModal(false)} className="px-4 py-2 text-sm text-[var(--color-gray-text)] hover:bg-[var(--color-hover-light)] rounded-lg">{t('common.cancel')}</button>
              <button onClick={handleSubmit} className="px-4 py-2 text-sm bg-[var(--color-primary-blue)] text-white rounded-lg font-medium hover:opacity-90">{editingUser ? t('admin.save') : t('admin.create')}</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 2: Verify build passes**

Run: `cd frontend && npm run build`
Expected: BUILD SUCCESSFUL

- [ ] **Step 3: Commit**

```bash
git add frontend/src/pages/AdminPage.tsx
git commit -m "feat(backend): add admin user management API endpoints"
```

Wait — wrong commit message. Fix:

```bash
git commit --amend -m "feat(frontend): add AdminPage with user table and CRUD modals"
```

Actually, let's do this properly:

```bash
git add frontend/src/pages/AdminPage.tsx
git commit -m "feat(frontend): add AdminPage with user table and CRUD modals"
```

---

### Task 4: Wire Admin Route and Sidebar Link

**Files:**
- Modify: `frontend/src/App.tsx`
- Modify: `frontend/src/components/Sidebar.tsx`

**Interfaces:**
- Consumes: `AdminPage` from `pages/AdminPage`; `useAuthStore` for role check
- Produces: `/admin` route accessible only to admin role; sidebar link visible to admin

- [ ] **Step 1: Add AdminPage import and route in `App.tsx`**

Add import:
```tsx
import { AdminPage } from './pages/AdminPage';
```

Add route inside the `ProtectedRoute` block, after the settings route:
```tsx
<Route path="admin" element={<AdminPage />} />
```

- [ ] **Step 2: Add admin sidebar link in `Sidebar.tsx`**

Add after the Settings link, inside the nav section, wrapped in an admin role check:

```tsx
{user?.role === 'admin' && (
  <NavLink to="/admin" ... >
    {/* Users icon */}
    {t('admin.user_management')}
  </NavLink>
)}
```

Import `useAuthStore` at the top if not already imported:
```tsx
import { useAuthStore } from '../stores/authStore';
```

Add inside the component:
```tsx
const user = useAuthStore((s) => s.user);
```

- [ ] **Step 3: Verify build passes**

Run: `cd frontend && npm run build`
Expected: BUILD SUCCESSFUL

- [ ] **Step 4: Commit**

```bash
git add frontend/src/App.tsx frontend/src/components/Sidebar.tsx
git commit -m "feat(frontend): add admin route and sidebar link"
```

---

### Task 5: Add i18n Keys for Admin UI

**Files:**
- Modify: `frontend/src/i18n/translations/en.ts`
- Modify: `frontend/src/i18n/translations/kn.ts`

**Interfaces:**
- Consumes: existing translation file structure (common/dashboard/chat/network/settings namespaces)
- Produces: `admin` namespace with all admin UI strings

- [ ] **Step 1: Add `admin` namespace to `en.ts`**

Add at the end of the file, inside the default export object:

```typescript
admin: {
  user_management: 'User Management',
  manage_users: 'Add, edit, and deactivate user accounts',
  add_user: 'Add User',
  edit_user: 'Edit User',
  search_placeholder: 'Search by username or employee ID...',
  username: 'Username',
  employee_id: 'Employee ID',
  role: 'Role',
  status: 'Status',
  actions: 'Actions',
  active: 'Active',
  inactive: 'Inactive',
  edit: 'Edit',
  deactivate: 'Deactivate',
  no_users: 'No users found',
  new_password_optional: 'New Password (leave blank to keep current)',
  password: 'Password',
  save: 'Save',
  create: 'Create',
  confirm_deactivate: 'Deactivate user {{username}}?',
  fill_required: 'Please fill in all required fields',
},
```

- [ ] **Step 2: Add `admin` namespace to `kn.ts`**

Add at the end of the file, inside the default export object:

```typescript
admin: {
  user_management: 'ಬಳಕೆದಾರ ನಿರ್ವಹಣೆ',
  manage_users: 'ಬಳಕೆದಾರ ಖಾತೆಗಳನ್ನು ಸೇರಿಸಿ, ಸಂಪಾದಿಸಿ ಮತ್ತು ನಿಷ್ಕ್ರಿಯಗೊಳಿಸಿ',
  add_user: 'ಬಳಕೆದಾರನನ್ನು ಸೇರಿಸಿ',
  edit_user: 'ಬಳಕೆದಾರನನ್ನು ಸಂಪಾದಿಸಿ',
  search_placeholder: 'ಬಳಕೆದಾರ ಹೆಸರು ಅಥವಾ ಉದ್ಯೋಗಿ ಐಡಿಯಿಂದ ಹುಡುಕಿ...',
  username: 'ಬಳಕೆದಾರ ಹೆಸರು',
  employee_id: 'ಉದ್ಯೋಗಿ ಐಡಿ',
  role: 'ಪಾತ್ರ',
  status: 'ಸ್ಥಿತಿ',
  actions: 'ಕ್ರಿಯೆಗಳು',
  active: 'ಸಕ್ರಿಯ',
  inactive: 'ನಿಷ್ಕ್ರಿಯ',
  edit: 'ಸಂಪಾದಿಸಿ',
  deactivate: 'ನಿಷ್ಕ್ರಿಯಗೊಳಿಸಿ',
  no_users: 'ಬಳಕೆದಾರರು ಕಂಡುಬಂದಿಲ್ಲ',
  new_password_optional: 'ಹೊಸ ಪಾಸ್‌ವರ್ಡ್ (ಪ್ರಸ್ತುತವನ್ನು ಉಳಿಸಲು ಖಾಲಿ ಬಿಡಿ)',
  password: 'ಪಾಸ್‌ವರ್ಡ್',
  save: 'ಉಳಿಸಿ',
  create: 'ರಚಿಸಿ',
  confirm_deactivate: '{{username}} ಬಳಕೆದಾರನನ್ನು ನಿಷ್ಕ್ರಿಯಗೊಳಿಸಬೇಕೇ?',
  fill_required: 'ದಯವಿಟ್ಟು ಎಲ್ಲಾ ಅಗತ್ಯ ಕ್ಷೇತ್ರಗಳನ್ನು ಭರ್ತಿ ಮಾಡಿ',
},
```

- [ ] **Step 3: Verify build passes**

Run: `cd frontend && npm run build`
Expected: BUILD SUCCESSFUL

- [ ] **Step 4: Commit**

```bash
git add frontend/src/i18n/translations/en.ts frontend/src/i18n/translations/kn.ts
git commit -m "feat(i18n): add admin UI translation keys for English and Kannada"
```

---

### Task 6: Final Verification

**Files:** None (verification only)

- [ ] **Step 1: Run frontend build**

Run: `cd frontend && npm run build`
Expected: BUILD SUCCESSFUL

- [ ] **Step 2: Run frontend lint**

Run: `cd frontend && npm run lint`
Expected: No errors

- [ ] **Step 3: Run backend ruff**

Run: `source .venv/bin/activate && ruff check backend/ && ruff format --check backend/`
Expected: All checks passed

- [ ] **Step 4: Verify all commits**

Run: `git log --oneline origin/main..HEAD`
Expected: All 6 tasks' commits present

- [ ] **Step 5: Commit (if any fixes needed)**

No commit needed if all checks pass.
