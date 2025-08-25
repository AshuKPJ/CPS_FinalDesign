// src/components/modals/SettingsModal.jsx
import React, { useState, useEffect } from "react";

export default function SettingsModal({ open, onClose, initial = {} }) {
  const [template, setTemplate] = useState("");
  const [proxy, setProxy] = useState("");
  const [auto, setAuto] = useState(false);

  useEffect(() => {
    if (open) {
      setTemplate(initial.default_message_template || "");
      setProxy(initial.proxy_url || "");
      setAuto(!!initial.auto_submit);
    }
  }, [open, initial]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-[1000] bg-black/50 flex items-center justify-center p-4">
      <div className="bg-white rounded-xl w-full max-w-2xl p-6 shadow-xl">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold">Settings</h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-800">✕</button>
        </div>

        <div className="grid md:grid-cols-2 gap-4">
          <div className="md:col-span-2">
            <label className="block text-sm font-medium mb-1">Default Message Template</label>
            <textarea
              rows={4}
              className="w-full border rounded px-3 py-2"
              value={template}
              onChange={(e) => setTemplate(e.target.value)}
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Proxy URL</label>
            <input
              className="w-full border rounded px-3 py-2"
              value={proxy}
              onChange={(e) => setProxy(e.target.value)}
              placeholder="http://user:pass@host:port"
            />
          </div>
          <div className="flex items-center gap-2 pt-6">
            <input id="auto" type="checkbox" checked={auto} onChange={(e) => setAuto(e.target.checked)} />
            <label htmlFor="auto" className="text-sm">Auto-submit after upload</label>
          </div>
        </div>

        <div className="flex justify-end gap-2 mt-6">
          <button className="px-4 py-2 rounded bg-gray-100" onClick={onClose}>Close</button>
          {/* Wire this to your real /settings endpoint later */}
          <button className="px-4 py-2 rounded bg-indigo-600 text-white" onClick={onClose}>Save</button>
        </div>
      </div>
    </div>
  );
}
