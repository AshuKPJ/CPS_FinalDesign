import React, { useState, useEffect, useRef } from 'react';
import toast, { Toaster } from 'react-hot-toast';
import axios from 'axios';

const MAX_FILE_SIZE_MB = 10;

const FormSubmitterPage = () => {
  const [csvFile, setCsvFile] = useState(null);
  const [proxy, setProxy] = useState('');
  const [haltOnCaptcha, setHaltOnCaptcha] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [logs, setLogs] = useState([]);
  const fileInputRef = useRef(null);
  const logsContainerRef = useRef(null);
  const eventSourceRef = useRef(null);

  useEffect(() => {
    document.title = 'Campaign Submission Center | CPS';
  }, []);

  useEffect(() => {
    // Close any previous connection before opening a new one
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    const eventSource = new EventSource('http://localhost:8000/submit/logs/stream');
    eventSourceRef.current = eventSource;

    eventSource.onopen = () => {
      toast.success('📡 Connected to log stream');
    };

    eventSource.onmessage = (e) => {
      const newLine = e.data;
      setLogs((prevLogs) => [...prevLogs, newLine]);
    };

    eventSource.onerror = (err) => {
      console.error('❌ SSE error:', err);
      toast.error('❌ Lost connection to log stream');
      eventSource.close();
    };

    return () => {
      eventSource.close();
    };
  }, []);

  useEffect(() => {
    if (logsContainerRef.current) {
      logsContainerRef.current.scrollTop = logsContainerRef.current.scrollHeight;
    }
  }, [logs]);

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      if (file.size > MAX_FILE_SIZE_MB * 1024 * 1024) {
        toast.error(`File exceeds ${MAX_FILE_SIZE_MB}MB limit.`);
        return;
      }
      setCsvFile(file);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files?.[0];
    if (file) {
      if (file.size > MAX_FILE_SIZE_MB * 1024 * 1024) {
        toast.error(`File exceeds ${MAX_FILE_SIZE_MB}MB limit.`);
        return;
      }
      setCsvFile(file);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!csvFile) {
      toast.error('A CSV file is required.');
      return;
    }

    const formData = new FormData();
    formData.append('file', csvFile);
    formData.append('proxy', proxy);
    formData.append('haltOnCaptcha', haltOnCaptcha);

    try {
      setSubmitting(true);
      setLogs([]);
      toast.success('🚀 Submission started!');

      await axios.post('http://localhost:8000/submit/start', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      toast.success('✅ Submission triggered!');
    } catch (err) {
      toast.error('❌ An error occurred.');
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

  const getLogColor = (line) => {
    if (line.includes('✅')) return 'text-green-400';
    if (line.includes('❌') || line.includes('🔥')) return 'text-red-400';
    if (line.includes('⚠️')) return 'text-yellow-400';
    return 'text-gray-200';
  };

  return (
    <div className="bg-gray-100 min-h-screen font-sans">
      <Toaster position="top-right" />
      <div className="p-4 sm:p-6 md:p-8 max-w-7xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-3xl sm:text-4xl font-bold text-gray-900">🎯 Campaign Submission Center</h1>
          <p className="text-gray-600 mt-2">Upload a CSV to launch your automated outreach campaign.</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-5 gap-12">
          <div className="lg:col-span-3">
            <div className="bg-white p-8 rounded-2xl shadow-md">
              <form onSubmit={handleSubmit} className="space-y-8">
                <div>
                  <label className="block text-base font-semibold text-gray-800 mb-2">1. Upload CSV File</label>
                  <div
                    className="mt-1 flex flex-col items-center justify-center px-6 pt-8 pb-8 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer hover:border-indigo-500 bg-gray-50 transition-colors"
                    onClick={() => fileInputRef.current.click()}
                    onDragOver={(e) => e.preventDefault()}
                    onDrop={handleDrop}
                  >
                    <svg className="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth="1.5"
                        d="M7 16a4 4 0 01-4-4V7a4 4 0 014-4h1.6A4 4 0 0115.4 7L12 10.4"
                      />
                    </svg>
                    {csvFile ? (
                      <div className="text-center mt-4">
                        <p className="font-semibold text-indigo-700">{csvFile.name}</p>
                        <p className="text-sm text-gray-500">{(csvFile.size / 1024).toFixed(2)} KB</p>
                      </div>
                    ) : (
                      <div className="text-center mt-4">
                        <p className="text-gray-700">Drag & drop a file here</p>
                        <p className="text-sm text-gray-500">
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
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                  <div>
                    <label htmlFor="proxy" className="block text-base font-semibold text-gray-800">
                      2. Proxy (Optional)
                    </label>
                    <input
                      type="text"
                      id="proxy"
                      value={proxy}
                      onChange={(e) => setProxy(e.target.value)}
                      className="w-full p-3 border border-gray-300 rounded-md shadow-sm"
                      placeholder="http://user:pass@ip:port"
                    />
                  </div>
                  <div>
                    <label className="block text-base font-semibold text-gray-800">3. CAPTCHA Handling</label>
                    <div className="mt-2 flex items-center justify-between bg-gray-50 p-3 border border-gray-300 rounded-md">
                      <span className="text-sm text-gray-700">Halt on CAPTCHA</span>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          className="sr-only peer"
                          checked={haltOnCaptcha}
                          onChange={() => setHaltOnCaptcha(!haltOnCaptcha)}
                        />
                        <div className="w-11 h-6 bg-gray-200 rounded-full peer peer-checked:bg-indigo-600"></div>
                      </label>
                    </div>
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={submitting}
                  className="w-full flex justify-center items-center py-3 px-4 rounded-md text-white font-medium bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50"
                >
                  {submitting ? 'Processing...' : 'Start Submitting'}
                </button>
              </form>
            </div>
          </div>

          <div className="lg:col-span-2">
            <div className="sticky top-8">
              <h2 className="text-xl font-semibold mb-3 text-gray-800">📋 Live Logs</h2>
              <div className="bg-gray-900 rounded-lg shadow-xl overflow-hidden">
                <div className="bg-gray-800 p-3 flex items-center">
                  <div className="flex space-x-1.5">
                    <div className="w-3 h-3 rounded-full bg-red-500"></div>
                    <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
                    <div className="w-3 h-3 rounded-full bg-green-500"></div>
                  </div>
                  <p className="text-center text-sm text-gray-400 font-mono flex-grow">/var/log/submission.log</p>
                </div>
                <div
                  ref={logsContainerRef}
                  className="p-4 h-96 overflow-y-auto text-sm font-mono whitespace-pre-wrap bg-gray-900"
                >
                  {logs.length === 0 ? (
                    <span className="text-gray-500">Awaiting submission to start logs...</span>
                  ) : (
                    logs.map((line, idx) => (
                      <div key={idx} className={`flex items-start ${getLogColor(line)}`}>
                        <span className="text-gray-600 mr-4 select-none">{String(idx + 1).padStart(2, '0')}</span>
                        <span className="flex-1 break-words">{line}</span>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FormSubmitterPage;
