// frontend/src/pages/DashboardPage.jsx

import React from 'react';
import useAuth from '../hooks/useAuth';
import AdminDashboard from './AdminDashboard';
import OwnerDashboard from './OwnerDashboard';
import UserDashboard from './UserDashboard';

const DashboardPage = () => {
  const { user } = useAuth();

  if (!user) return null;

  if (user.role === 'admin') {
    return <AdminDashboard />;
  }

  if (user.role === 'owner') {
    return <OwnerDashboard />;
  }

  return <UserDashboard />;
};

export default DashboardPage;
