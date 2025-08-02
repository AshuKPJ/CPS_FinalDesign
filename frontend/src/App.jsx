// src/App.jsx
import React, { useState } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import AppLayout from "./components/layout/AppLayout";
import LandingPage from "./pages/LandingPage";
import DashboardPage from "./pages/DashboardPage";
import CampaignsPage from "./pages/CampaignsPage";
import CampaignDetailPage from "./pages/CampaignDetailPage";
import UserProfileForm from "./pages/UserProfileForm";
import AdminDashboard from "./pages/AdminDashboard";
import OwnerDashboard from "./pages/OwnerDashboard";
import UserDashboard from "./pages/UserDashboard";
import FormSubmitterPage from "./pages/FormSubmitterPage";
import useAuth from "./hooks/useAuth";
import AuthModal from "./components/AuthModal";
import { Toaster } from "react-hot-toast";

const ProtectedRoute = ({ children }) => {
  const { user } = useAuth();
  return user ? children : <Navigate to="/" replace />;
};

const AdminRoute = ({ children }) => {
  const { user } = useAuth();
  return user && (user.role === "admin" || user.role === "owner")
    ? children
    : <Navigate to="/dashboard" replace />;
};

const OwnerRoute = ({ children }) => {
  const { user } = useAuth();
  return user?.role === "owner"
    ? children
    : <Navigate to="/dashboard" replace />;
};

const UserRoute = ({ children }) => {
  const { user } = useAuth();
  return user?.role === "user"
    ? children
    : <Navigate to="/dashboard" replace />;
};

const App = () => {
  const { user, loading, login, register } = useAuth();
  const [showModal, setShowModal] = useState(false);
  const [view, setView] = useState("login");

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen text-lg">
        Loading...
      </div>
    );
  }

  const openModal = (type) => {
    setView(type);
    setShowModal(true);
  };

  return (
    <>
      <Toaster
        position="top-center"
        toastOptions={{
          style: {
            padding: "12px 20px",
            fontSize: "15px",
            background: "#1f2937",
            color: "#fff",
            borderRadius: "8px",
            boxShadow: "0 8px 25px rgba(0,0,0,0.2)",
          },
          success: {
            iconTheme: {
              primary: "#10b981",
              secondary: "#ffffff",
            },
          },
          error: {
            iconTheme: {
              primary: "#ef4444",
              secondary: "#ffffff",
            },
          },
        }}
      />

      <Routes>
        <Route element={<AppLayout />}>
          <Route
            index
            element={
              <LandingPage
                onLogin={() => openModal("login")}
                onRegister={() => openModal("register")}
              />
            }
          />

          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/campaigns"
            element={
              <ProtectedRoute>
                <CampaignsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/campaigns/:campaignId"
            element={
              <ProtectedRoute>
                <CampaignDetailPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/UserProfileForm"
            element={
              <ProtectedRoute>
                <UserProfileForm />
              </ProtectedRoute>
            }
          />
          <Route
            path="/form-submitter"
            element={
              <ProtectedRoute>
                <FormSubmitterPage />
              </ProtectedRoute>
            }
          />

          <Route
            path="/admin"
            element={
              <AdminRoute>
                <AdminDashboard />
              </AdminRoute>
            }
          />
          <Route
            path="/owner"
            element={
              <OwnerRoute>
                <OwnerDashboard />
              </OwnerRoute>
            }
          />
          <Route
            path="/user"
            element={
              <UserRoute>
                <UserDashboard />
              </UserRoute>
            }
          />

          <Route path="*" element={<Navigate to="/" />} />
        </Route>
      </Routes>

      <AuthModal
        show={showModal}
        onClose={() => setShowModal(false)}
        view={view}
        onSwitchView={setView}
        onLogin={login}
        onRegister={register}
      />
    </>
  );
};

export default App;
