// src/components/UserMenu.jsx

import React, { useState, useRef, useEffect } from "react";
import {
  ChevronDown,
  Settings,
  KeyRound,
  ShieldPlus,
  LogOut,
} from "lucide-react";

const UserMenu = ({ firstName = "Ashu", lastName = "Jadhav", role = "owner", onLogout }) => {
  const [open, setOpen] = useState(false);
  const menuRef = useRef(null);

  const initials =
    firstName.charAt(0).toUpperCase() + lastName.charAt(0).toUpperCase();

  const toggleMenu = () => setOpen((prev) => !prev);

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (menuRef.current && !menuRef.current.contains(e.target)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <div className="relative inline-block text-left" ref={menuRef}>
      <button
        onClick={toggleMenu}
        className="flex items-center gap-3 px-5 py-2.5 bg-white border border-gray-200 rounded-xl shadow-sm hover:shadow-md transition-all duration-150 focus:outline-none"
      >
        <div className="relative">
          <div className="h-9 w-9 bg-indigo-100 text-indigo-700 font-semibold rounded-full flex items-center justify-center text-sm shadow-inner ring-2 ring-indigo-200">
            {initials}
          </div>
        </div>
        <div className="text-left leading-tight">
          <div className="text-sm font-bold text-gray-800">
            {firstName} {lastName}
          </div>
          <div className="text-[11px] text-gray-500 capitalize">{role}</div>
        </div>
        <ChevronDown
          className={`h-4 w-4 text-gray-400 transition-transform ${
            open ? "rotate-180" : ""
          }`}
        />
      </button>

      {open && (
        <div className="absolute right-0 mt-2 w-64 bg-white/80 backdrop-blur-md border border-gray-200 rounded-xl shadow-2xl z-50 animate-fadeIn">
          {/* Header */}
          <div className="flex items-center px-4 py-4 border-b border-gray-100">
            <div className="h-10 w-10 bg-indigo-200 text-indigo-800 font-bold rounded-full flex items-center justify-center shadow-sm">
              {initials}
            </div>
            <div className="ml-3">
              <div className="text-sm font-semibold text-gray-900">
                {firstName} {lastName}
              </div>
              <div className="text-xs text-gray-500 capitalize">{role}</div>
            </div>
          </div>

          {/* Menu */}
          <ul className="py-2 text-sm text-gray-700 divide-y divide-gray-100">
            <li className="px-4 py-3 flex items-center gap-3 hover:bg-indigo-50 hover:text-indigo-700 cursor-pointer transition">
              <Settings className="h-4 w-4 text-indigo-500" />
              <span>Settings</span>
            </li>
            <li className="px-4 py-3 flex items-center gap-3 hover:bg-indigo-50 hover:text-indigo-700 cursor-pointer transition">
              <KeyRound className="h-4 w-4 text-indigo-500" />
              <span>Reset Password</span>
            </li>
            <li className="px-4 py-3 flex items-center gap-3 hover:bg-indigo-50 hover:text-indigo-700 cursor-pointer transition">
              <ShieldPlus className="h-4 w-4 text-indigo-500" />
              <span>Add DeathByCaptcha</span>
            </li>
            <li
              onClick={onLogout}
              className="px-4 py-3 flex items-center gap-3 hover:bg-red-50 text-red-600 hover:text-red-800 cursor-pointer transition"
            >
              <LogOut className="h-4 w-4" />
              <span>Logout</span>
            </li>
          </ul>
        </div>
      )}
    </div>
  );
};

export default UserMenu;
