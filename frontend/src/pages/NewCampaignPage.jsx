// frontend/src/pages/NewCampaignPage.jsx

import React, { useState } from 'react';
import api from '../services/api'; // Axios instance with JWT
import { useNavigate } from 'react-router-dom';

const NewCampaignPage = () => {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    name: '',
    message: '',
    proxy: '',
    useCaptcha: false,
    csvFile: null,
  });

  const handleChange = (e) => {
    const { name, value, type, checked, files } = e.target;
    if (type === 'checkbox') {
      setForm({ ...form, [name]: checked });
    } else if (type === 'file') {
      setForm({ ...form, csvFile: files[0] });
    } else {
      setForm({ ...form, [name]: value });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    Object.entries(form).forEach(([key, val]) => {
      if (key === 'csvFile' && val) {
        formData.append('csv_file', val);
      } else {
        formData.append(key, val);
      }
    });
    try {
      const res = await api.post('/campaigns/create', formData);
      navigate(`/campaigns/${res.data.id}`);
    } catch (error) {
      alert('Failed to create campaign');
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">+ New Campaign</h1>
      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label className="block font-medium mb-1">Campaign Name</label>
          <input
            type="text"
            name="name"
            value={form.name}
            onChange={handleChange}
            className="w-full border px-3 py-2 rounded-md"
            required
          />
        </div>

        <div>
          <label className="block font-medium mb-1">Message</label>
          <textarea
            name="message"
            value={form.message}
            onChange={handleChange}
            className="w-full border px-3 py-2 rounded-md"
            rows={5}
            required
          />
        </div>

        <div>
          <label className="block font-medium mb-1">Proxy URL</label>
          <input
            type="text"
            name="proxy"
            value={form.proxy}
            onChange={handleChange}
            className="w-full border px-3 py-2 rounded-md"
            placeholder="http://user:pass@host:port"
          />
        </div>

        <div>
          <label className="block font-medium mb-1">Upload CSV File</label>
          <input
            type="file"
            name="csvFile"
            accept=".csv"
            onChange={handleChange}
            className="w-full"
            required
          />
        </div>

        <div className="flex items-center">
          <input
            type="checkbox"
            name="useCaptcha"
            checked={form.useCaptcha}
            onChange={handleChange}
            className="mr-2"
          />
          <label>Use CAPTCHA</label>
        </div>

        <button
          type="submit"
          className="bg-indigo-600 text-white px-6 py-2 rounded-md hover:bg-indigo-700"
        >
          Create Campaign
        </button>
      </form>
    </div>
  );
};

export default NewCampaignPage;
