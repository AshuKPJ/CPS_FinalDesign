// src/pages/FormSubmitterPage.jsx
import React, { useState, useEffect, useRef } from "react";
import toast, { Toaster } from "react-hot-toast";
import axios from "axios";

const MAX_FILE_SIZE_MB = 10;

// ---- Base URL (no change in behavior) ----
const API_BASE = (() => {
  const cra = (typeof process !== "undefined" && process.env && process.env.REACT_APP_API_BASE) || "";
  const win = (typeof window !== "undefined" && window.__API_BASE__) || "";
  let base = cra || win;
  if (!base) {
    const { protocol, hostname, port } = window.location;
    base =
      port === "3000"
        ? `${protocol}//${hostname}:8000`
        : `${protocol}//${hostname}${port ? ":" + port : ""}`;
  }
  return base.replace(/\/$/, "");
})();

function getAccessToken() {
  const keys = ["access_token", "token", "authToken", "accessToken", "id_token", "jwt", "jwt_token"];
  for (const k of keys) {
    const v = localStorage.getItem(k) || sessionStorage.getItem(k);
    if (v) return v;
  }
  const m = document.cookie.match(/(?:^|;\s*)(access_token|token)=([^;]+)/i);
  if (m) return decodeURIComponent(m[2]);
  return "";
}

export default function FormSubmitterPage() {
  const [csvFile, setCsvFile] = useState(null);
  const [proxy, setProxy] = useState("");
  const [haltOnCaptcha, setHaltOnCaptcha] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [lastJobId, setLastJobId] = useState(null);

  const fileInputRef = useRef(null);

  useEffect(() => {
    document.title = "Campaign Submission Center | CPS";
  }, []);

  const pickFile = () => fileInputRef.current?.click();

  const validateCsv = (file) => {
    if (!file) return "Please choose a CSV file.";
    if (!file.name.toLowerCase().endsWith(".csv")) return "Please select a .csv file.";
    if (file.size > MAX_FILE_SIZE_MB * 1024 * 1024)
      return `File exceeds ${MAX_FILE_SIZE_MB}MB limit.`;
    return "";
  };

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    const err = validateCsv(file);
    if (err) return toast.error(err);
    setCsvFile(file);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files?.[0];
    const err = validateCsv(file);
    if (err) return toast.error(err);
    setCsvFile(file);
  };

  const clearFile = (e) => {
    e.preventDefault();
    setCsvFile(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!csvFile) return toast.error("A CSV file is required.");

    const token = getAccessToken();
    if (!token) return toast.error("You must be logged in. No access token found.");

    const formData = new FormData();
    formData.append("file", csvFile);
    formData.append("proxy", proxy || "");
    formData.append("haltOnCaptcha", haltOnCaptcha ? "true" : "false");

    try {
      setSubmitting(true);
      toast.success("🚀 Submission started!");

      // Expect backend to return { job_id, campaign_id?, message }
      const { data } = await axios.post(`${API_BASE}/submit/start`, formData, {
        headers: {
          "Content-Type": "multipart/form-data",
          Authorization: `Bearer ${token}`,
        },
        timeout: 0,
      });

      const jobId = data?.job_id || data?.campaign_id || data?.id;
      if (jobId) {
        setLastJobId(jobId);
        toast.success(`✅ Submission triggered (Job: ${jobId})`);
      } else {
        toast.success("✅ Submission triggered!");
      }
    } catch (err) {
      console.error(err);
      const msg = err?.response?.data?.detail || err?.message || "Error starting submission.";
      toast.error(`❌ ${msg}`);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="bg-white min-h-screen text-gray-900">
      <Toaster
        position="top-center"
        toastOptions={{
          style: {
            padding: "12px 20px",
            fontSize: "15px",
            background: "#111827",
            color: "#fff",
            borderRadius: "10px",
            boxShadow: "0 10px 25px rgba(0,0,0,0.14)",
          },
          success: { iconTheme: { primary: "#10b981", secondary: "#ffffff" } },
          error:   { iconTheme: { primary: "#ef4444", secondary: "#ffffff" } },
        }}
      />

      {/* Hero / Header */}
      <div className="relative overflow-hidden">
        <div className="absolute inset-0 pointer-events-none"
             aria-hidden
             style={{
               background:
                 "radial-gradient(1200px 600px at 50% -10%, rgba(79,70,229,0.08), transparent 60%), radial-gradient(700px 400px at 100% 10%, rgba(16,185,129,0.06), transparent 60%)"
             }} />
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 pt-14 pb-8">
          <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-6">
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-50 text-indigo-700 border border-indigo-100 text-xs font-semibold">
                <span className="inline-block w-1.5 h-1.5 rounded-full bg-indigo-600" />
                Automation Suite
              </div>
              <h1 className="mt-3 text-3xl sm:text-4xl font-bold tracking-tight">
                Campaign Submission Center
              </h1>
              <p className="mt-2 text-gray-600">
                Upload a CSV and launch your automated outreach campaign. Logs are saved to your
                account and can be viewed later in <span className="font-medium">Logs</span>.
              </p>
            </div>

            <div className="flex flex-wrap items-center gap-3">
              <a
                href={lastJobId ? `/logs?job_id=${encodeURIComponent(lastJobId)}` : "/logs"}
                className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-white border border-gray-200 hover:bg-gray-50 text-gray-800 shadow-sm transition"
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden>
                  <path d="M4 6h16M4 12h16M4 18h16" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
                </svg>
                View Recent Logs {lastJobId ? `(Job ${lastJobId})` : ""}
              </a>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 pb-16">
        {/* Step cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
            <div className="flex items-center gap-3">
              <span className="inline-flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-600 text-white text-sm font-bold">1</span>
              <div className="font-semibold">Upload CSV</div>
            </div>
            <p className="mt-2 text-sm text-gray-600">
              Provide a .csv file containing websites to process.
            </p>
          </div>
          <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
            <div className="flex items-center gap-3">
              <span className="inline-flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-600 text-white text-sm font-bold">2</span>
              <div className="font-semibold">Options</div>
            </div>
            <p className="mt-2 text-sm text-gray-600">
              Optional proxy and whether to halt when a CAPTCHA is detected.
            </p>
          </div>
          <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
            <div className="flex items-center gap-3">
              <span className="inline-flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-600 text-white text-sm font-bold">3</span>
              <div className="font-semibold">Start</div>
            </div>
            <p className="mt-2 text-sm text-gray-600">
              Submit the job and monitor progress from the Logs page.
            </p>
          </div>
        </div>

        {/* Main Form Card */}
        <div className="rounded-3xl border border-gray-200 bg-white shadow-xl shadow-indigo-50/40">
          <div className="p-6 sm:p-10">
            <form onSubmit={handleSubmit} className="space-y-10">
              {/* CSV upload */}
              <section>
                <div className="flex items-center justify-between mb-3">
                  <label className="text-base font-semibold">1. Upload CSV File</label>
                  {csvFile && (
                    <button
                      onClick={clearFile}
                      className="text-sm text-rose-600 hover:text-rose-700 underline underline-offset-4"
                      type="button"
                    >
                      Remove
                    </button>
                  )}
                </div>

                <div
                  className="group relative border-2 border-dashed rounded-2xl p-8 bg-gray-50 hover:bg-gray-100/70 border-gray-300 transition-colors cursor-pointer"
                  onClick={pickFile}
                  onDragOver={(e) => e.preventDefault()}
                  onDrop={handleDrop}
                  role="button"
                  tabIndex={0}
                >
                  <div className="flex flex-col items-center text-center">
                    <div className="h-14 w-14 rounded-2xl bg-white shadow-sm border border-gray-200 flex items-center justify-center group-hover:shadow-md transition">
                      <svg className="w-6 h-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.8"
                              d="M3 15a4 4 0 004 4h10a4 4 0 004-4V9a4 4 0 00-4-4h-1.6A4 4 0 0010.6 7L7 10.6" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.8"
                              d="M7 10l5 5m0 0l5-5m-5 5V3" />
                      </svg>
                    </div>

                    {csvFile ? (
                      <div className="mt-4">
                        <p className="font-semibold text-gray-900">{csvFile.name}</p>
                        <p className="text-xs text-gray-500">
                          {(csvFile.size / 1024).toFixed(2)} KB
                        </p>
                      </div>
                    ) : (
                      <div className="mt-4">
                        <p className="text-gray-800 font-medium">Drag & drop your .csv here</p>
                        <p className="text-sm text-gray-600">
                          or <span className="font-semibold text-indigo-600">browse</span> to upload
                        </p>
                      </div>
                    )}

                    <input
                      ref={fileInputRef}
                      type="file"
                      accept=".csv"
                      className="sr-only"
                      onChange={handleFileChange}
                    />
                  </div>

                  {!csvFile && (
                    <p className="absolute bottom-3 right-4 text-[11px] text-gray-500">
                      Max size: {MAX_FILE_SIZE_MB}MB
                    </p>
                  )}
                </div>

                <div className="mt-3 text-xs text-gray-500">
                  Tip: Ensure the file contains a <span className="font-medium">website</span> column.
                </div>
              </section>

              {/* Options */}
              <section className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div>
                  <label htmlFor="proxy" className="block text-base font-semibold mb-2">
                    2. Proxy (Optional)
                  </label>
                  <input
                    id="proxy"
                    type="text"
                    value={proxy}
                    onChange={(e) => setProxy(e.target.value)}
                    placeholder="http://user:pass@ip:port"
                    className="w-full px-4 py-3 rounded-xl bg-white border border-gray-300 focus:ring-4 focus:ring-indigo-100 focus:border-indigo-500 placeholder:text-gray-400 transition"
                  />
                  <p className="text-xs text-gray-500 mt-2">
                    Leave blank to use the default outbound connection.
                  </p>
                </div>

                <div>
                  <label className="block text-base font-semibold mb-2">
                    3. CAPTCHA Handling
                  </label>

                  <div className="flex items-center justify-between px-4 py-3 rounded-xl bg-gray-50 border border-gray-200">
                    <span className="text-sm text-gray-800">Halt on CAPTCHA</span>

                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        className="sr-only peer"
                        checked={haltOnCaptcha}
                        onChange={() => setHaltOnCaptcha(!haltOnCaptcha)}
                      />
                      <span className="w-12 h-7 rounded-full bg-gray-300 peer-checked:bg-indigo-600 transition-colors"></span>
                      <span className="absolute left-1 top-1 w-5 h-5 rounded-full bg-white shadow-sm transform transition-transform peer-checked:translate-x-5" />
                    </label>
                  </div>
                  <p className="text-xs text-gray-500 mt-2">
                    When enabled, the run pauses if a CAPTCHA is encountered.
                  </p>
                </div>
              </section>

              {/* CTA */}
              <div className="pt-2 flex flex-col sm:flex-row gap-3">
                <button
                  type="submit"
                  disabled={submitting}
                  className={`inline-flex items-center justify-center gap-2 px-5 py-3 rounded-xl font-semibold text-white shadow-md transition w-full sm:w-auto
                    ${submitting ? "bg-indigo-400 cursor-not-allowed" : "bg-indigo-600 hover:bg-indigo-700 shadow-indigo-200"}`}
                >
                  {submitting ? (
                    <>
                      <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24" fill="none" aria-hidden>
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
                      </svg>
                      Processing…
                    </>
                  ) : (
                    <>
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden>
                        <path d="M5 12h14M12 5l7 7-7 7" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
                      </svg>
                      Start Submitting
                    </>
                  )}
                </button>

                <a
                  href={lastJobId ? `/logs?job_id=${encodeURIComponent(lastJobId)}` : "/logs"}
                  className="inline-flex items-center justify-center gap-2 px-5 py-3 rounded-xl font-semibold bg-white border border-gray-300 hover:bg-gray-50 text-gray-900 shadow-sm transition w-full sm:w-auto"
                >
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden>
                    <path d="M4 6h16M4 12h16M4 18h16" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
                  </svg>
                  View Recent Logs {lastJobId ? `(Job ${lastJobId})` : ""}
                </a>
              </div>

              {lastJobId && (
                <div className="text-xs text-gray-500 mt-2">
                  Tip: Monitor DB-persisted logs on the Logs page. Share the Job ID with your team if needed.
                </div>
              )}
            </form>
          </div>
        </div>

        {/* Help / Notes */}
        <div className="mt-8 grid grid-cols-1 lg:grid-cols-3 gap-4">
          <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
            <div className="font-semibold mb-1">CSV Requirements</div>
            <p className="text-sm text-gray-600">
              Include a <span className="font-medium">website</span> column. Optional columns are okay.
            </p>
          </div>
          <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
            <div className="font-semibold mb-1">Security</div>
            <p className="text-sm text-gray-600">
              Your job runs under your authenticated account and logs are tenant-scoped.
            </p>
          </div>
          <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
            <div className="font-semibold mb-1">Troubleshooting</div>
            <p className="text-sm text-gray-600">
              If a run fails to start, verify token, CSV size, and server availability, then check <a href="/logs" className="text-indigo-600 hover:text-indigo-700 font-medium">Logs</a>.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
