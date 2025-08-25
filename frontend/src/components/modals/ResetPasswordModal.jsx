// src/components/modals/ResetPasswordModal.jsx
import React, { useEffect, useState } from "react";
import toast from "react-hot-toast";
import useAuth from "../../hooks/useAuth";
import { requestPasswordReset } from "../../services/api";

export default function ResetPasswordModal({ open, onClose }) {
  const { user } = useAuth();
  const [email, setEmail] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [devLink, setDevLink] = useState("");

  useEffect(() => {
    if (open) {
      setEmail(user?.email || "");
      setDevLink("");
    }
  }, [open, user]);

  if (!open) return null;

  const onSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const { ok, reset_url } = await requestPasswordReset(email);
      if (ok) {
        setDevLink(reset_url || "");
        toast.success("Password reset link sent (check email).");
      } else {
        toast.error("Failed to request reset.");
      }
    } catch (e) {
      toast.error(e?.response?.data?.detail || "Failed to request reset.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-[1000] bg-black/50 flex items-center justify-center p-4">
      <div className="bg-white rounded-xl w-full max-w-md p-6 shadow-xl">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold">Reset Password</h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-800">✕</button>
        </div>

        <form onSubmit={onSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Account Email</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full border rounded px-3 py-2"
            />
          </div>

          <div className="flex justify-end gap-2">
            <button type="button" className="px-4 py-2 rounded bg-gray-100" onClick={onClose}>
              Close
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="px-4 py-2 rounded bg-indigo-600 text-white disabled:opacity-60"
            >
              {submitting ? "Sending…" : "Send Reset Link"}
            </button>
          </div>
        </form>

        {/* For dev: your API returns reset_url; show it so you can click it immediately */}
        {devLink && (
          <div className="mt-4 text-xs bg-gray-50 border rounded p-3">
            <div className="font-semibold mb-1">Dev reset URL (shows in dev only):</div>
            <a className="text-indigo-600 break-all" href={devLink}>{devLink}</a>
          </div>
        )}
      </div>
    </div>
  );
}
