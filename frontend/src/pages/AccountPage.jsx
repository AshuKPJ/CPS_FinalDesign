// frontend/src/pages/AccountPage.jsx

import React, { useEffect, useState } from 'react';
import api from '../services/api';
import Card, { CardContent } from '../components/ui/card';
import Input from '../components/ui/input';
import Button from '../components/ui/button';


const AccountPage = () => {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('');

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const res = await api.get('/usercontactprofile/contact-answers');
        setProfile(res.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchProfile();
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setProfile((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await api.post('/usercontactprofile/upsert', profile);
      setMessage('Profile updated successfully!');
    } catch (err) {
      console.error(err);
      setMessage('Failed to update profile.');
    }
  };

  if (loading) return <div className="p-6">Loading...</div>;

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-4">🧾 Account Info</h1>
      {message && <div className="mb-4 text-green-600 font-medium">{message}</div>}
      <form onSubmit={handleSubmit} className="space-y-4">
        <Card>
          <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4 py-6">
            <Input label="First Name" name="first_name" value={profile.first_name || ''} onChange={handleChange} />
            <Input label="Last Name" name="last_name" value={profile.last_name || ''} onChange={handleChange} />
            <Input label="Email" name="email" value={profile.email || ''} onChange={handleChange} type="email" />
            <Input label="Phone Number" name="phone_number" value={profile.phone_number || ''} onChange={handleChange} />
            <Input label="Job Title" name="job_title" value={profile.job_title || ''} onChange={handleChange} />
            <Input label="Company" name="company_name" value={profile.company_name || ''} onChange={handleChange} />
            <Input label="Website" name="website_url" value={profile.website_url || ''} onChange={handleChange} />
            <Input label="LinkedIn URL" name="linkedin_url" value={profile.linkedin_url || ''} onChange={handleChange} />
          </CardContent>
        </Card>
        <div className="flex justify-end">
          <Button type="submit">💾 Save Changes</Button>
        </div>
      </form>
    </div>
  );
};

export default AccountPage;
