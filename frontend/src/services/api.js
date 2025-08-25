import axios from "axios";

const API_BASE = (process.env.REACT_APP_API_URL || "http://127.0.0.1:8000").replace(/\/$/, "");

const api = axios.create({
  baseURL: API_BASE,
  timeout: 0,
  withCredentials: false,
});

api.interceptors.request.use((config) => {
  const token =
    localStorage.getItem("access_token") ||
    localStorage.getItem("token") ||
    localStorage.getItem("authToken");
  if (token) {
    config.headers = config.headers || {};
    if (!config.headers.Authorization) config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (r) => r,
  (err) => {
    if (err?.response?.status === 401) {
      localStorage.removeItem("access_token");
      localStorage.removeItem("auth_user");
    }
    return Promise.reject(err);
  }
);

// ---- Auth ----
export async function login({ email, password }) {
  const res = await api.post("/auth/login", { email, password }, {
    headers: { "Content-Type": "application/json" },
  });
  if (res?.data?.access_token) localStorage.setItem("access_token", res.data.access_token);
  return res.data;
}
export async function getMe() {
  const res = await api.get("/users/me");
  return res.data;
}

// ---- Logs ----
export async function fetchLogs(params) {
  const res = await api.get("/logs", { params });
  return res.data;
}

// ---- Submit ----
export async function startSubmit({ file, proxy, haltOnCaptcha }) {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("proxy", proxy || "");
  formData.append("haltOnCaptcha", haltOnCaptcha ? "true" : "false");

  const res = await api.post("/submit/start", formData, {
    headers: { "Content-Type": "multipart/form-data" },
    timeout: 0,
  });
  return res.data; // { job_id }
}

export { api };
export default api;
