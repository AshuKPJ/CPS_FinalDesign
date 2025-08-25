import React, { useEffect, useState } from "react";
import toast from "react-hot-toast";
import { getCaptchaSettings, setCaptchaSettings } from "../services/api";

export default function CaptchaModal({ open, onClose }) {
  const [loading, setLoading] = useState(false);
  const [hasCreds, setHasCreds] = useState(false);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState(""); // plaintext shown back if server returns it
  const [saving, setSaving] = useState(false);
  const [editing, setEditing] = useState(false);

  useEffect(() => {
    if (!open) return;
    (async () => {
      setLoading(true);
      try {
        const data = await getCaptchaSettings();
        const has = !!data?.has_captcha;
        setHasCreds(has);
        setUsername(data?.captcha_username || "");
        setPassword(data?.captcha_password || ""); // server decrypts & returns
        setEditing(!has); // if not set, open in edit mode
      } catch (e) {
        toast.error("Failed to load captcha settings");
      } finally {
        setLoading(false);
      }
    })();
  }, [open]);

  const onSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await setCaptchaSettings({ username, password });
      toast.success("DeathByCaptcha credentials saved");
      setHasCreds(true);
      setEditing(false);
      onClose?.();
    } catch (err) {
      toast.error(err?.response?.data?.detail || "Failed to save credentials");
    } finally {
      setSaving(false);
    }
  };

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4">
      <div className="bg-white rounded-xl w-full max-w-md p-6 shadow-xl">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold">DeathByCaptcha</h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-800">✕</button>
        </div>

        {loading ? (
          <div className="py-8 text-center text-gray-500">Loading…</div>
        ) : (
          <>
            {hasCreds && !editing ? (
              <div className="space-y-3">
                <div className="rounded border bg-green-50 text-green-800 p-3">
                  Credentials already saved for this account.
                </div>
                <div>
                  <div className="text-sm text-gray-600">Username</div>
                  <div className="font-mono">{username || "-"}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-600">Password</div>
                  <div className="font-mono">{password ? "•".repeat(Math.min(12, password.length)) : "-"}</div>
                </div>
                <div className="flex justify-end gap-2 pt-2">
                  <button className="px-4 py-2 rounded bg-gray-100" onClick={() => setEditing(true)}>
                    Edit
                  </button>
                  <button className="px-4 py-2 rounded bg-blue-600 text-white" onClick={onClose}>
                    Close
                  </button>
                </div>
              </div>
            ) : (
              <form onSubmit={onSubmit} className="space-y-3">
                <div>
                  <label className="block text-sm font-medium mb-1">Username</label>
                  <input
                    className="w-full border rounded px-3 py-2"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    autoComplete="off"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Password</label>
                  <input
                    className="w-full border rounded px-3 py-2"
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    autoComplete="new-password"
                    required
                  />
                </div>

                <div className="flex justify-end gap-2 pt-2">
                  {hasCreds && (
                    <button type="button" className="px-4 py-2 rounded bg-gray-100" onClick={() => setEditing(false)}>
                      Cancel
                    </button>
                  )}
                  <button type="submit" disabled={saving} className="px-4 py-2 rounded bg-blue-600 text-white disabled:opacity-60">
                    {saving ? "Saving…" : "Save"}
                  </button>
                </div>
              </form>
            )}
          </>
        )}
      </div>
    </div>
  );
}
