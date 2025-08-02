// src/components/layout/AppLayout.jsx

import React, { useState } from "react";
import { Outlet } from "react-router-dom";
import Header from "./Header";
import Footer from "./Footer";
import AuthModal from "../AuthModal";
import useAuth from "../../hooks/useAuth";

const AppLayout = () => {
  const { login, register } = useAuth();

  const [showModal, setShowModal] = useState(false);
  const [view, setView] = useState("login");

  const openLogin = () => {
    setView("login");
    setShowModal(true);
  };

  const openRegister = () => {
    setView("register");
    setShowModal(true);
  };

  return (
    <>
      <Header onLoginClick={openLogin} onRegisterClick={openRegister} />
      <div className="min-h-screen bg-white pt-[130px]">
        <Outlet />
      </div>
      <Footer />
      <AuthModal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        view={view}
        onSwitchView={setView}
        onLogin={login}
        onRegister={register}
      />
    </>
  );
};

export default AppLayout;
