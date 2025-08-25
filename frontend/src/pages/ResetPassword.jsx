import React, { useState, useMemo } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { resetPassword } from "../services/api";
import toast from "react-hot-toast";

export default function ResetPassword() {
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const token = useMemo(() => params.get("token") || "", [params]);
  const [pw, setPw] = useState("");
  const [pw2, setPw2] = useState("");
  const [saving, setSaving] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    if (pw !== pw2) return toast.error("Passwords do not match");
    setSaving(true);
    try {
      await resetPassword(token, pw);
      toast.success("Password updated. Please log in.");
      navigate("/");
    } catch (e) {
      toast.error(e?.response?.data?.detail || "Reset failed");
    } finally {
      setSaving(false);
    }
  };

  if (!token) {
    return <div className="max-w-md mx-auto p-6 text-red-600">Missing reset token.</div>;
  }

  return (
    <div className="max-w-md mx-auto p-6">
      <h1 className="text-xl font-semibold mb-4">Set a new password</h1>
      <form onSubmit={submit} className="space-y-3">
        <input className="w-full border rounded px-3 py-2" type="password" placeholder="New password" value={pw} onChange={(e) => setPw(e.target.value)} required />
        <input className="w-full border rounded px-3 py-2" type="password" placeholder="Confirm password" value={pw2} onChange={(e) => setPw2(e.target.value)} required />
        <button className="px-4 py-2 rounded bg-blue-600 text-white disabled:opacity-60" disabled={saving}>
          {saving ? "Updating…" : "Update password"}
        </button>
      </form>
    </div>
  );
}
