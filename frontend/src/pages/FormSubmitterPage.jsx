import React, { useState, useEffect, useRef } from "react";
import toast, { Toaster } from "react-hot-toast";
import { startSubmit } from "../api";

const MAX_FILE_SIZE_MB = 10;

export default function FormSubmitterPage() {
  const [csvFile, setCsvFile] = useState(null);
  const [proxy, setProxy] = useState("");
  const [haltOnCaptcha, setHaltOnCaptcha] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [lastJobId, setLastJobId] = useState(null);
  const fileInputRef = useRef(null);

  useEffect(() => { document.title = "Campaign Submission Center | CPS"; }, []);

  const pickFile  = () => fileInputRef.current?.click();
  const clearFile = () => { setCsvFile(null); if (fileInputRef.current) fileInputRef.current.value = ""; };
  const validateCsv = (f) => {
    if (!f) return "Please choose a CSV file.";
    if (!f.name.toLowerCase().endsWith(".csv")) return "Please select a .csv file.";
    if (f.size > MAX_FILE_SIZE_MB * 1024 * 1024) return `File exceeds ${MAX_FILE_SIZE_MB}MB limit.`;
    return "";
  };

  const onFile = (f) => {
    const err = validateCsv(f);
    if (err) return toast.error(err);
    setCsvFile(f);
  };

  const handleFileChange = (e) => onFile(e.target.files?.[0]);
  const handleDrop = (e) => { e.preventDefault(); onFile(e.dataTransfer.files?.[0]); };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!csvFile) return toast.error("A CSV file is required.");
    try {
      setSubmitting(true);
      toast.success("🚀 Submission started! Check the Logs page for steps.");
      const data = await startSubmit({ file: csvFile, proxy, haltOnCaptcha });
      if (data?.job_id) {
        setLastJobId(data.job_id);
        toast.success(`✅ Job queued (ID: ${data.job_id})`);
      } else {
        toast.success("✅ Job queued");
      }
    } catch (err) {
      console.error(err);
      toast.error(err?.response?.data?.detail || err?.message || "Failed to start submission.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="bg-gradient-to-b from-indigo-50 to-white min-h-screen text-gray-900">
      <Toaster position="top-center" />
      {/* Your header / hero can stay; below is the main uploader card */}
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="rounded-3xl border border-indigo-100 bg-white/90 backdrop-blur shadow-2xl shadow-indigo-100">
          <div className="p-6 sm:p-10">
            <form onSubmit={handleSubmit} className="space-y-10">
              <section>
                <div className="flex items-center justify-between mb-3">
                  <label className="text-base font-semibold">1. Upload CSV File</label>
                  {csvFile && <button type="button" onClick={clearFile} className="text-sm text-rose-600 underline">Remove</button>}
                </div>
                <div
                  className="group border-2 border-dashed rounded-2xl p-8 bg-gray-50 hover:bg-gray-100 border-gray-300 cursor-pointer transition"
                  onClick={() => fileInputRef.current?.click()}
                  onDragOver={(e)=>e.preventDefault()}
                  onDrop={handleDrop}
                >
                  <div className="text-center">
                    <p className="font-medium">
                      {csvFile ? csvFile.name : "Drag & drop your .csv here, or click to browse"}
                    </p>
                    <input ref={fileInputRef} type="file" accept=".csv" className="sr-only" onChange={handleFileChange}/>
                  </div>
                </div>
              </section>

              <section className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div>
                  <label className="block text-base font-semibold mb-2">2. Proxy (Optional)</label>
                  <input
                    value={proxy}
                    onChange={(e)=>setProxy(e.target.value)}
                    placeholder="http://user:pass@ip:port"
                    className="w-full px-4 py-3 rounded-xl bg-white border border-gray-300"
                  />
                </div>
                <div>
                  <label className="block text-base font-semibold mb-2">3. CAPTCHA Handling</label>
                  <label className="inline-flex items-center gap-3">
                    <input type="checkbox" checked={haltOnCaptcha} onChange={()=>setHaltOnCaptcha(!haltOnCaptcha)} />
                    <span>Halt on CAPTCHA</span>
                  </label>
                </div>
              </section>

              <div className="pt-2 flex flex-col sm:flex-row gap-3">
                <button type="submit" disabled={submitting} className={`px-5 py-3 rounded-xl text-white font-semibold ${submitting?"bg-indigo-400":"bg-indigo-600 hover:bg-indigo-700"}`}>
                  {submitting ? "Processing…" : "Start Submitting"}
                </button>
                <a href={lastJobId ? `/logs?job_id=${encodeURIComponent(lastJobId)}` : "/logs"} className="px-5 py-3 rounded-xl bg-white border border-gray-300">
                  View Recent Logs {lastJobId ? `(Job ${lastJobId})` : ""}
                </a>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}
