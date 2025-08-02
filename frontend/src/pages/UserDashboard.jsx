// src/pages/UserDashboard.jsx

import React from "react";

const stats = [
  { label: "Total Submissions", value: "12,498" },
  { label: "Success Rate", value: "97.2%" },
  { label: "Active Campaigns", value: "5" },
  { label: "Captchas Solved", value: "8,204" },
];

const recentCampaigns = [
  {
    name: "Spring Lead Push",
    date: "2025-07-25",
    total: 2400,
    submitted: 2356,
    status: "Running",
  },
  {
    name: "Tech Outreach",
    date: "2025-07-20",
    total: 1800,
    submitted: 1800,
    status: "Completed",
  },
  {
    name: "Local Biz Blitz",
    date: "2025-07-18",
    total: 920,
    submitted: 871,
    status: "Paused",
  },
];

const UserDashboard = () => {
  return (
    <div className="bg-gray-50 py-10 px-4 sm:px-6 lg:px-8 min-h-screen">
      <div className="max-w-7xl mx-auto">
        {/* Page Title */}
        <h1 className="text-3xl font-bold text-gray-900 mb-8">
          Welcome back 👋
        </h1>

        {/* Stat Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
          {stats.map((stat, idx) => (
            <div
              key={idx}
              className="bg-white shadow-sm border rounded-lg px-6 py-5 text-center"
            >
              <p className="text-gray-500 text-sm font-medium">
                {stat.label}
              </p>
              <p className="text-2xl font-semibold text-indigo-600 mt-1">
                {stat.value}
              </p>
            </div>
          ))}
        </div>

        {/* Recent Campaigns */}
        <div className="bg-white shadow-sm border rounded-lg">
          <div className="px-6 py-4 border-b">
            <h2 className="text-lg font-semibold text-gray-800">
              Recent Campaigns
            </h2>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 text-sm">
              <thead className="bg-gray-100">
                <tr>
                  <th className="px-6 py-3 text-left font-medium text-gray-700">
                    Campaign Name
                  </th>
                  <th className="px-6 py-3 text-left font-medium text-gray-700">
                    Date
                  </th>
                  <th className="px-6 py-3 text-left font-medium text-gray-700">
                    Total URLs
                  </th>
                  <th className="px-6 py-3 text-left font-medium text-gray-700">
                    Submitted
                  </th>
                  <th className="px-6 py-3 text-left font-medium text-gray-700">
                    Status
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 bg-white">
                {recentCampaigns.map((row, idx) => (
                  <tr key={idx}>
                    <td className="px-6 py-4 whitespace-nowrap font-medium text-gray-900">
                      {row.name}
                    </td>
                    <td className="px-6 py-4">{row.date}</td>
                    <td className="px-6 py-4">{row.total}</td>
                    <td className="px-6 py-4">{row.submitted}</td>
                    <td className="px-6 py-4">
                      <span
                        className={`inline-block px-2 py-1 rounded text-xs font-semibold ${
                          row.status === "Completed"
                            ? "bg-green-100 text-green-700"
                            : row.status === "Paused"
                            ? "bg-yellow-100 text-yellow-700"
                            : "bg-blue-100 text-blue-700"
                        }`}
                      >
                        {row.status}
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

export default UserDashboard;
