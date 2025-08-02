// src/pages/CampaignsPage.jsx

import React from "react";
import { useNavigate } from "react-router-dom";

const campaigns = [
  {
    id: 1,
    name: "Spring Blast",
    created: "2025-07-12",
    totalUrls: 1800,
    submitted: 1764,
    status: "Running",
  },
  {
    id: 2,
    name: "Tech Outreach",
    created: "2025-07-05",
    totalUrls: 2000,
    submitted: 2000,
    status: "Completed",
  },
  {
    id: 3,
    name: "July Trial Leads",
    created: "2025-07-01",
    totalUrls: 500,
    submitted: 360,
    status: "Paused",
  },
];

const CampaignsPage = () => {
  const navigate = useNavigate();

  return (
    <div className="bg-gray-50 py-10 px-4 sm:px-6 lg:px-8 min-h-screen">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Your Campaigns</h1>
          <button
            className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700 transition"
            onClick={() => alert("Campaign creation flow coming soon")}
          >
            + New Campaign
          </button>
        </div>

        {/* Campaign Table */}
        <div className="bg-white shadow-sm border rounded-lg">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 text-sm">
              <thead className="bg-gray-100">
                <tr>
                  <th className="px-6 py-3 text-left font-medium text-gray-700">Name</th>
                  <th className="px-6 py-3 text-left font-medium text-gray-700">Created</th>
                  <th className="px-6 py-3 text-left font-medium text-gray-700">Total URLs</th>
                  <th className="px-6 py-3 text-left font-medium text-gray-700">Submitted</th>
                  <th className="px-6 py-3 text-left font-medium text-gray-700">Status</th>
                  <th className="px-6 py-3 text-left font-medium text-gray-700">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 bg-white">
                {campaigns.map((c) => (
                  <tr key={c.id}>
                    <td className="px-6 py-4 font-medium text-gray-900">{c.name}</td>
                    <td className="px-6 py-4">{c.created}</td>
                    <td className="px-6 py-4">{c.totalUrls}</td>
                    <td className="px-6 py-4">{c.submitted}</td>
                    <td className="px-6 py-4">
                      <span
                        className={`inline-block px-2 py-1 rounded text-xs font-semibold ${
                          c.status === "Completed"
                            ? "bg-green-100 text-green-700"
                            : c.status === "Paused"
                            ? "bg-yellow-100 text-yellow-700"
                            : "bg-blue-100 text-blue-700"
                        }`}
                      >
                        {c.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 space-x-2">
                      <button
                        onClick={() => navigate(`/campaigns/${c.id}`)}
                        className="text-sm text-indigo-600 hover:underline"
                      >
                        View
                      </button>
                      <button
                        onClick={() => alert("Pause/Resume coming soon")}
                        className="text-sm text-yellow-600 hover:underline"
                      >
                        Pause
                      </button>
                      <button
                        onClick={() => alert("Delete confirmation coming soon")}
                        className="text-sm text-red-600 hover:underline"
                      >
                        Delete
                      </button>
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

export default CampaignsPage;
