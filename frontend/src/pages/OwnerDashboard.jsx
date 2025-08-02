// src/pages/OwnerDashboard.jsx

import React from "react";

const stats = [
  { label: "Total Revenue", value: "$48,200" },
  { label: "Active Subscriptions", value: "132" },
  { label: "New Signups (30d)", value: "41" },
  { label: "Resellers", value: "7" },
];

const subAdmins = [
  {
    name: "Tom Mack",
    email: "tom@example.com",
    assigned: "East Region",
    status: "Active",
  },
  {
    name: "Kim Gregory",
    email: "kim@example.com",
    assigned: "Marketing",
    status: "Active",
  },
  {
    name: "Dan Ewing",
    email: "dan@example.com",
    assigned: "Trial Accounts",
    status: "Suspended",
  },
];

const OwnerDashboard = () => {
  return (
    <div className="bg-gray-50 py-10 px-4 sm:px-6 lg:px-8 min-h-screen">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">
          Owner Dashboard
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

        {/* Sub-admins Table */}
        <div className="bg-white shadow-sm border rounded-lg">
          <div className="px-6 py-4 border-b">
            <h2 className="text-lg font-semibold text-gray-800">
              Team / Sub-Admins
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
                    Assigned
                  </th>
                  <th className="px-6 py-3 text-left font-medium text-gray-700">
                    Status
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 bg-white">
                {subAdmins.map((user, idx) => (
                  <tr key={idx}>
                    <td className="px-6 py-4 font-medium text-gray-900">
                      {user.name}
                    </td>
                    <td className="px-6 py-4">{user.email}</td>
                    <td className="px-6 py-4">{user.assigned}</td>
                    <td className="px-6 py-4">
                      <span
                        className={`inline-block px-2 py-1 rounded text-xs font-semibold ${
                          user.status === "Active"
                            ? "bg-green-100 text-green-700"
                            : "bg-yellow-100 text-yellow-700"
                        }`}
                      >
                        {user.status}
                      </span>
                    </td>
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

export default OwnerDashboard;
