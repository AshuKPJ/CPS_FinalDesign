// src/pages/AdminDashboard.jsx

import React from "react";

const stats = [
  { label: "Total Users", value: "412" },
  { label: "Campaigns Run", value: "8,243" },
  { label: "Forms Submitted", value: "211,875" },
  { label: "CAPTCHA Solves", value: "173,093" },
];

const users = [
  {
    name: "Sarah Johnson",
    email: "sarah@example.com",
    role: "user",
    campaigns: 12,
    lastLogin: "2025-07-29",
  },
  {
    name: "Gunderson Helscroft",
    email: "gunder@example.com",
    role: "user",
    campaigns: 24,
    lastLogin: "2025-07-30",
  },
  {
    name: "Jessica Simmons",
    email: "jessica@example.com",
    role: "owner",
    campaigns: 33,
    lastLogin: "2025-07-29",
  },
];

const AdminDashboard = () => {
  return (
    <div className="bg-gray-50 py-10 px-4 sm:px-6 lg:px-8 min-h-screen">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">
          Admin Dashboard
        </h1>

        {/* Stat Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
          {stats.map((stat, idx) => (
            <div
              key={idx}
              className="bg-white shadow-sm border rounded-lg px-6 py-5 text-center"
            >
              <p className="text-gray-500 text-sm font-medium">{stat.label}</p>
              <p className="text-2xl font-semibold text-indigo-600 mt-1">
                {stat.value}
              </p>
            </div>
          ))}
        </div>

        {/* Users Table */}
        <div className="bg-white shadow-sm border rounded-lg">
          <div className="px-6 py-4 border-b">
            <h2 className="text-lg font-semibold text-gray-800">
              Recent Active Users
            </h2>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 text-sm">
              <thead className="bg-gray-100">
                <tr>
                  <th className="px-6 py-3 text-left font-medium text-gray-700">
                    Name
                  </th>
                  <th className="px-6 py-3 text-left font-medium text-gray-700">
                    Email
                  </th>
                  <th className="px-6 py-3 text-left font-medium text-gray-700">
                    Role
                  </th>
                  <th className="px-6 py-3 text-left font-medium text-gray-700">
                    Campaigns
                  </th>
                  <th className="px-6 py-3 text-left font-medium text-gray-700">
                    Last Login
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 bg-white">
                {users.map((user, idx) => (
                  <tr key={idx}>
                    <td className="px-6 py-4 whitespace-nowrap font-medium text-gray-900">
                      {user.name}
                    </td>
                    <td className="px-6 py-4">{user.email}</td>
                    <td className="px-6 py-4 capitalize">{user.role}</td>
                    <td className="px-6 py-4">{user.campaigns}</td>
                    <td className="px-6 py-4">{user.lastLogin}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
