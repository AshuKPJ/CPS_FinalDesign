// frontend/src/components/UserEditModal.jsx

import React, { useEffect, useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from './ui/dialog';
import Input from './ui/input';
import Button from './ui/button';

const UserEditModal = ({ isOpen, onClose, user, onSave }) => {
  const [formData, setFormData] = useState({});

  useEffect(() => {
    if (user) {
      setFormData(user);
    }
  }, [user]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSave = () => {
    onSave(formData);
    onClose();
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>Edit User</DialogTitle>
        </DialogHeader>
        <div className="space-y-4">
          <Input
            label="First Name"
            name="first_name"
            value={formData.first_name || ''}
            onChange={handleChange}
            placeholder="First Name"
          />
          <Input
            label="Last Name"
            name="last_name"
            value={formData.last_name || ''}
            onChange={handleChange}
            placeholder="Last Name"
          />
          <Input
            label="Email"
            name="email"
            value={formData.email || ''}
            onChange={handleChange}
            placeholder="Email"
          />
          <Input
            label="Role"
            name="role"
            value={formData.role || ''}
            onChange={handleChange}
            placeholder="Role (admin, user, owner)"
          />
        </div>
        <div className="flex justify-end mt-6 space-x-3">
          <Button variant="outline" onClick={onClose}>Cancel</Button>
          <Button onClick={handleSave}>Save</Button>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default UserEditModal;
