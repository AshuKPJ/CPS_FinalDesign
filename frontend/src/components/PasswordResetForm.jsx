// frontend/src/components/PasswordResetForm.jsx

import React, { useState } from 'react';
import api from '../services/api';
import Input from './ui/input';
import Button from './ui/button';

const PasswordResetForm = () => {
  const [formData, setFormData] = useState({
    password: '',
    new_password: '',
    confirm_password: '',
  });

  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(null);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);
    try {
      const response = await api.post('/auth/update-password', formData);
      setSuccess(response.data.message);
      setFormData({ password: '', new_password: '', confirm_password: '' });
    } catch (err) {
      setError(err.response?.data?.message || 'Error updating password');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6 bg-white p-6 rounded-lg shadow-md max-w-xl mx-auto">
      <h2 className="text-xl font-semibold text-gray-800">🔐 Reset Password</h2>

      <Input
        label="Current Password"
        type="password"
        name="password"
        value={formData.password}
        onChange={handleChange}
        required
      />

      <Input
        label="New Password"
        type="password"
        name="new_password"
        value={formData.new_password}
        onChange={handleChange}
        required
      />

      <Input
        label="Confirm New Password"
        type="password"
        name="confirm_password"
        value={formData.confirm_password}
        onChange={handleChange}
        required
      />

      {success && <p className="text-green-600 text-sm">{success}</p>}
      {error && <p className="text-red-600 text-sm">{error}</p>}

      <div className="text-right">
        <Button type="submit" disabled={loading}>
          {loading ? 'Updating...' : 'Update Password'}
        </Button>
      </div>
    </form>
  );
};

export default PasswordResetForm;
