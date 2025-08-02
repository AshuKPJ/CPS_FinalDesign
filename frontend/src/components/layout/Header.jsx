// src/components/layout/Header.jsx

import React, { useState } from "react";
import { Phone, Mail, Menu, X } from "lucide-react";
import useAuth from "../../hooks/useAuth";
import { useNavigate } from "react-router-dom";
import UserMenu from "../UserMenu";

const Header = ({ onLoginClick, onRegisterClick }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [mobileOpen, setMobileOpen] = useState(false);

  const getNavLinks = () => {
    if (!user) {
      return [
        { name: "Features", href: "#features" },
        { name: "Steps", href: "#steps" },
        { name: "Benefits", href: "#benefits" },
        { name: "Testimonials", href: "#testimonials" },
        { name: "Gallery", href: "#gallery" },
        { name: "Integrations", href: "#integrations" },
        { name: "FAQ", href: "#faq" },
      ];
    }

    const baseLinks = [
      { name: "Dashboard", href: "/dashboard" },
      { name: "Campaigns", href: "/campaigns" },
      { name: "User Profile", href: "/UserProfileForm" },
      { name: "Form Submitter", href: "/form-submitter" },
    ];

    if (user.role === "admin" || user.role === "owner") {
      baseLinks.push({ name: "User Management", href: "/admin/users" });
    }

    if (user.role === "owner") {
      baseLinks.push({ name: "Settings", href: "/admin/settings" });
    }

    return baseLinks;
  };

  const navLinks = getNavLinks();

  return (
    <header className="fixed top-0 left-0 right-0 z-50 shadow-sm border-b bg-white">
      <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-20">
          <div className="flex-shrink-0">
            <a href="/" className="flex items-center">
              <img
                className="h-12 w-auto drop-shadow-md hover:scale-105 transition-transform duration-300"
                alt="CPS Logo"
                src="/assets/images/CPS_Header_Logo.png"
              />
            </a>
          </div>

          <div className="hidden md:flex items-center space-x-8">
            <div className="flex items-baseline space-x-4">
              {navLinks.map((link) => (
                <a
                  key={link.name}
                  href={link.href}
                  className="text-gray-700 hover:text-indigo-700 px-3 py-2 text-sm font-medium relative group"
                >
                  <span>{link.name}</span>
                  <span className="absolute left-0 -bottom-1 w-0 h-0.5 bg-indigo-500 transition-all group-hover:w-full"></span>
                </a>
              ))}
            </div>

            {!user && (
              <div className="flex flex-col items-start space-y-1">
                <a
                  href="tel:973-618-9906"
                  className="flex items-center text-sm font-medium text-gray-500 hover:text-indigo-700"
                >
                  <Phone className="h-4 w-4 mr-2" /> 973.618.9906
                </a>
                <a
                  href="mailto:AL@DBE.name"
                  className="flex items-center text-sm font-medium text-gray-500 hover:text-indigo-700"
                >
                  <Mail className="h-4 w-4 mr-2" /> AL@DBE.name
                </a>
              </div>
            )}

            <div className="ml-4">
              {!user ? (
                <>
                  <button
                    onClick={onLoginClick}
                    className="px-4 py-2 text-sm font-medium rounded-md text-indigo-700 bg-indigo-100 hover:bg-indigo-200 transition"
                  >
                    Login
                  </button>
                  <button
                    onClick={onRegisterClick}
                    className="ml-2 px-4 py-2 text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 transition"
                  >
                    Sign Up
                  </button>
                </>
              ) : (
                <UserMenu
                  firstName={user.first_name}
                  lastName={user.last_name}
                  role={user.role}
                  onLogout={logout}
                  enhanced
                />
              )}
            </div>
          </div>

          <div className="md:hidden">
            <button
              onClick={() => setMobileOpen(!mobileOpen)}
              className="text-gray-600 hover:text-gray-900 focus:outline-none"
            >
              {mobileOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </button>
          </div>
        </div>

        {mobileOpen && (
          <div className="md:hidden mt-4 pb-4 border-t border-gray-200">
            <div className="flex flex-col space-y-2">
              {navLinks.map((link) => (
                <a
                  key={link.name}
                  href={link.href}
                  onClick={() => setMobileOpen(false)}
                  className="text-gray-700 hover:text-indigo-600 px-4 py-2 text-sm"
                >
                  {link.name}
                </a>
              ))}
              {!user ? (
                <>
                  <button
                    onClick={() => {
                      setMobileOpen(false);
                      onLoginClick();
                    }}
                    className="text-indigo-600 font-semibold text-sm text-left px-4"
                  >
                    Login
                  </button>
                  <button
                    onClick={() => {
                      setMobileOpen(false);
                      onRegisterClick();
                    }}
                    className="text-indigo-600 font-semibold text-sm text-left px-4"
                  >
                    Sign Up
                  </button>
                </>
              ) : (
                <button
                  onClick={() => {
                    setMobileOpen(false);
                    logout();
                  }}
                  className="text-red-600 font-semibold text-sm text-left px-4"
                >
                  Logout
                </button>
              )}
            </div>
          </div>
        )}
      </nav>
    </header>
  );
};

export default Header;
