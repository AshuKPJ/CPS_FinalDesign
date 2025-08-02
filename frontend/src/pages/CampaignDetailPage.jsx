// src/pages/CampaignDetailPage.jsx

import React from "react";
import { useParams } from "react-router-dom";

const CampaignDetailPage = () => {
  const { campaignId } = useParams();

  // Dummy campaign data (can be replaced with real API call)
  const campaign = {
    id: campaignId,
    name: "Spring Blast",
    created: "2025-07-12",
    status: "Running",
    totalUrls: 1800,
    submitted: 1435,
    successRate: "96.2%",
    captchaFailures: 71,
    missingForms: 34,
  };

  return (
    <div className="bg-gray-50 py-10 px-4 sm:px-6 lg:px-8 min-h-screen">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          {campaign.name}
        </h1>
        <p className="text-gray-500 text-sm mb-6">Campaign ID: {campaign.id}</p>

        {/* Summary Stats */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 mb-10">
          <div className="bg-white p-6 rounded-lg shadow border">
            <p className="text-sm text-gray-500">Created</p>
            <p className="text-lg font-medium text-gray-800">{campaign.created}</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow border">
            <p className="text-sm text-gray-500">Status</p>
            <p className="text-lg font-medium text-indigo-600">{campaign.status}</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow border">
            <p className="text-sm text-gray-500">Total URLs</p>
            <p className="text-lg font-medium text-gray-800">{campaign.totalUrls}</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow border">
            <p className="text-sm text-gray-500">Submitted</p>
            <p className="text-lg font-medium text-gray-800">{campaign.submitted}</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow border">
            <p className="text-sm text-gray-500">Success Rate</p>
            <p className="text-lg font-medium text-green-600">{campaign.successRate}</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow border">
            <p className="text-sm text-gray-500">CAPTCHA Failures</p>
            <p className="text-lg font-medium text-red-600">{campaign.captchaFailures}</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow border">
            <p className="text-sm text-gray-500">No Contact Forms</p>
            <p className="text-lg font-medium text-yellow-600">{campaign.missingForms}</p>
          </div>
        </div>

        {/* Placeholder: Submission Logs */}
        <div className="bg-white p-6 rounded-lg shadow border">
          <h2 className="text-xl font-semibold text-gray-800 mb-2">
            Submission Logs (coming soon)
          </h2>
          <p className="text-sm text-gray-600">
            This section will display detailed logs for each form submission including status, fallback, retries, and errors.
          </p>
        </div>
      </div>
    </div>
  );
};

export default CampaignDetailPage;
