import { useEffect, useState, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { apiFetch } from '../api/client';

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
  const [users, setUsers] = useState<User[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [form, setForm] = useState<UserFormData>({ username: '', password: '', employee_id: '', role: 'investigator' });
  const [formError, setFormError] = useState('');

  const fetchUsers = useCallback(async () => {
    setLoading(true);
    try {
      const data = await apiFetch<User[]>('/admin/users');
      setUsers(data);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  }, []);

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
        await apiFetch(`/admin/users/${editingUser.user_id}`, {
          method: 'POST',
          headers: { 'X-HTTP-Method-Override': 'PUT' },
          json: body,
        });
      } else {
        await apiFetch('/admin/users', {
          method: 'POST',
          json: { username: form.username, password: form.password, employee_id: Number(form.employee_id), role: form.role },
        });
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
      await apiFetch(`/admin/users/${u.user_id}`, {
        method: 'POST',
        headers: { 'X-HTTP-Method-Override': 'DELETE' },
      });
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
