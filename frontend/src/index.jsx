// src/main.jsx or src/index.jsx

import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import { AuthProvider } from "./hooks/useAuth";
import { BrowserRouter } from "react-router-dom"; // ✅ Import this
import "./index.css";

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  // <React.StrictMode>
    <BrowserRouter> {/* ✅ Wrap with Router */}
      <AuthProvider>
        <App />
      </AuthProvider>
    </BrowserRouter>
  //</React.StrictMode>
);
