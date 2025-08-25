import React, { useState } from "react";
import { requestPasswordReset } from "../services/api";
import toast from "react-hot-toast";

export default function RequestReset() {
  const [email, setEmail] = useState("");
  const [sending, setSending] = useState(false);
  const [devUrl, setDevUrl] = useState("");

  const submit = async (e) => {
    e.preventDefault();
    setSending(true);
    try {
      const data = await requestPasswordReset(email);
      toast.success("If the email exists, a reset link has been sent.");
      if (data?.reset_url) setDevUrl(data.reset_url); // dev helper
    } catch {
      toast.error("Could not request reset.");
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="max-w-md mx-auto p-6">
      <h1 className="text-xl font-semibold mb-4">Forgot password</h1>
      <form onSubmit={submit} className="space-y-3">
        <input
          className="w-full border rounded px-3 py-2"
          type="email"
          placeholder="you@example.com"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <button className="px-4 py-2 rounded bg-blue-600 text-white disabled:opacity-60" disabled={sending}>
          {sending ? "Sending…" : "Send reset link"}
        </button>
      </form>

      {devUrl && (
        <div className="mt-4 p-3 rounded border bg-yellow-50 text-yellow-800 text-sm">
          Dev reset URL: <a className="underline" href={devUrl}>{devUrl}</a>
        </div>
      )}
    </div>
  );
}
