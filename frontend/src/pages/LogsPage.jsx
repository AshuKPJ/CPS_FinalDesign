// src/pages/LogsPage.jsx
import React, { useEffect, useState, useMemo } from "react";
import toast, { Toaster } from "react-hot-toast";
import { useLocation, Link } from "react-router-dom";
import api from "../api"; // use shared axios client (interceptors, baseURL, auth)

// ---- Helpers ----
function useQuery() {
  const loc = useLocation();
  return useMemo(() => new URLSearchParams(loc.search), [loc.search]);
}

export default function LogsPage() {
  const q = useQuery();

  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(false);
  const [jobId, setJobId] = useState("");
  const [campaignId, setCampaignId] = useState("");
  const [level, setLevel] = useState("");
  const [limit, setLimit] = useState(100);
  const [offset, setOffset] = useState(0);
  const [total, setTotal] = useState(null);

  // Pull ?job_id=... from URL on mount & whenever it changes
  useEffect(() => {
    setJobId(q.get("job_id") || "");
    setOffset(0);
  }, [q]);

  useEffect(() => {
    document.title = "Recent Logs | CPS";
  }, []);

  const fetchLogs = async () => {
    try {
      setLoading(true);
      const params = { limit, offset };
      if (jobId) params.job_id = jobId;
      if (campaignId) params.campaign_id = campaignId;
      if (level) params.level = level;

      const { data } = await api.get("/logs", { params });
      setRows(data?.items || data || []);
      setTotal(data?.total ?? null);
    } catch (e) {
      console.error(e);
      toast.error("Failed to fetch logs");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [limit, offset, jobId, campaignId, level]);

  const nextPage = () => setOffset((v) => v + limit);
  const prevPage = () => setOffset((v) => Math.max(0, v - limit));

  const clearFilters = () => {
    setJobId("");
    setCampaignId("");
    setLevel("");
    setOffset(0);
    fetchLogs();
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

      {/* Header / Hero */}
      <div className="relative overflow-hidden">
        <div
          className="absolute inset-0 pointer-events-none"
          aria-hidden
          style={{
            background:
              "radial-gradient(1200px 600px at 50% -10%, rgba(79,70,229,0.08), transparent 60%), radial-gradient(700px 400px at 100% 10%, rgba(16,185,129,0.06), transparent 60%)",
          }}
        />
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 pt-14 pb-6">
          <div className="flex items-start justify-between gap-6">
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-50 text-indigo-700 border border-indigo-100 text-xs font-semibold">
                <span className="inline-block w-1.5 h-1.5 rounded-full bg-indigo-600" />
                Observability
              </div>
              <h1 className="mt-3 text-3xl sm:text-4xl font-bold tracking-tight">
                Recent Logs
              </h1>
              <p className="mt-2 text-gray-600">
                Logs are stored in the database. Use filters below to narrow results or jump back to submit another job.
              </p>
            </div>

            <div className="flex flex-wrap gap-3">
              <Link
                to="/form-submitter"
                className="inline-flex items-center px-4 py-2.5 rounded-xl bg-white border border-gray-300 hover:bg-gray-50 text-gray-900 shadow-sm transition"
              >
                ← Back to Submitter
              </Link>
              <button
                onClick={fetchLogs}
                className="inline-flex items-center px-4 py-2.5 rounded-xl font-semibold text-white bg-indigo-600 hover:bg-indigo-700 shadow-sm transition"
              >
                Refresh
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 pb-16">
        {/* Filters */}
        <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm mb-6">
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            <input
              value={jobId}
              onChange={(e) => {
                setJobId(e.target.value);
                setOffset(0);
              }}
              placeholder="Job ID"
              className="px-4 py-3 rounded-xl bg-white border border-gray-300 focus:ring-4 focus:ring-indigo-100 focus:border-indigo-500 placeholder:text-gray-400 transition"
            />
            <input
              value={campaignId}
              onChange={(e) => {
                setCampaignId(e.target.value);
                setOffset(0);
              }}
              placeholder="Campaign ID"
              className="px-4 py-3 rounded-xl bg-white border border-gray-300 focus:ring-4 focus:ring-indigo-100 focus:border-indigo-500 placeholder:text-gray-400 transition"
            />
            <select
              value={level}
              onChange={(e) => {
                setLevel(e.target.value);
                setOffset(0);
              }}
              className="px-4 py-3 rounded-xl bg-white border border-gray-300 focus:ring-4 focus:ring-indigo-100 focus:border-indigo-500 transition"
            >
              <option value="">Any Level</option>
              <option value="DEBUG">DEBUG</option>
              <option value="INFO">INFO</option>
              <option value="WARN">WARN</option>
              <option value="ERROR">ERROR</option>
            </select>
            <select
              value={limit}
              onChange={(e) => {
                setLimit(parseInt(e.target.value, 10));
                setOffset(0);
              }}
              className="px-4 py-3 rounded-xl bg-white border border-gray-300 focus:ring-4 focus:ring-indigo-100 focus:border-indigo-500 transition"
            >
              {[25, 50, 100, 200].map((n) => (
                <option key={n} value={n}>
                  {n} per page
                </option>
              ))}
            </select>
            <div className="flex gap-2">
              <button
                onClick={() => {
                  setOffset(0);
                  fetchLogs();
                }}
                className="w-full inline-flex items-center justify-center px-4 py-3 rounded-xl font-semibold text-white bg-indigo-600 hover:bg-indigo-700 shadow-sm transition"
              >
                Apply Filters
              </button>
              <button
                onClick={clearFilters}
                className="w-full inline-flex items-center justify-center px-4 py-3 rounded-xl font-semibold bg-white border border-gray-300 hover:bg-gray-50 text-gray-900 shadow-sm transition"
              >
                Clear
              </button>
            </div>
          </div>
        </div>

        {/* Table Card */}
        <div className="rounded-3xl border border-gray-200 bg-white shadow-xl shadow-indigo-50/40 overflow-hidden">
          <div className="px-5 py-3 text-sm text-gray-600 flex items-center justify-between bg-gray-50 border-b border-gray-200">
            <span>
              {loading ? "Loading…" : `Showing ${rows.length}${total ? ` of ${total}` : ""}`}
            </span>
            <div className="space-x-2">
              <button
                disabled={offset === 0 || loading}
                onClick={prevPage}
                className="px-3 py-1.5 rounded-lg bg-white border border-gray-300 hover:bg-gray-50 text-gray-900 disabled:opacity-50 transition"
              >
                Prev
              </button>
              <button
                disabled={loading || (total !== null && offset + limit >= total)}
                onClick={nextPage}
                className="px-3 py-1.5 rounded-lg bg-white border border-gray-300 hover:bg-gray-50 text-gray-900 disabled:opacity-50 transition"
              >
                Next
              </button>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead className="text-gray-700 bg-white border-b border-gray-200">
                <tr>
                  <th className="px-5 py-3 text-left font-semibold">Time</th>
                  <th className="px-5 py-3 text-left font-semibold">Level</th>
                  <th className="px-5 py-3 text-left font-semibold">Job</th>
                  <th className="px-5 py-3 text-left font-semibold">Campaign</th>
                  <th className="px-5 py-3 text-left font-semibold">Message</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {rows.map((r) => (
                  <tr key={r.id}>
                    <td className="px-5 py-3 text-gray-600">{r.ts}</td>
                    <td className="px-5 py-3">
                      <span
                        className={`px-2 py-0.5 rounded-md text-xs font-medium ${
                          r.level === "ERROR"
                            ? "bg-red-100 text-red-700"
                            : r.level === "WARN"
                            ? "bg-amber-100 text-amber-700"
                            : r.level === "DEBUG"
                            ? "bg-slate-100 text-slate-700"
                            : "bg-emerald-100 text-emerald-700"
                        }`}
                      >
                        {r.level}
                      </span>
                    </td>
                    <td className="px-5 py-3 text-gray-800">{r.job_id || "—"}</td>
                    <td className="px-5 py-3 text-gray-800">{r.campaign_id || "—"}</td>
                    <td className="px-5 py-3 text-gray-900">{r.message}</td>
                  </tr>
                ))}
                {rows.length === 0 && !loading && (
                  <tr>
                    <td className="px-5 py-8 text-gray-500" colSpan={5}>
                      No logs found for the selected filters.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Footer help cards */}
        <div className="mt-8 grid grid-cols-1 lg:grid-cols-3 gap-4">
          <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
            <div className="font-semibold mb-1">Filtering</div>
            <p className="text-sm text-gray-600">
              You can deep-link to this page with <span className="font-medium">?job_id=…</span> to share a run.
            </p>
          </div>
          <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
            <div className="font-semibold mb-1">Retention</div>
            <p className="text-sm text-gray-600">
              Log retention follows your backend policy. Export as needed from your DB.
            </p>
          </div>
          <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
            <div className="font-semibold mb-1">Troubleshooting</div>
            <p className="text-sm text-gray-600">
              If nothing appears, verify your access token and confirm the backend <code className="font-mono">/logs</code> endpoint is live.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
