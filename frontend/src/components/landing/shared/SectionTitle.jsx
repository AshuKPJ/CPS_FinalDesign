// src/components/landing/shared/SectionTitle.jsx

import React from "react";

const SectionTitle = ({ children }) => {
  return (
    <h2 className="text-3xl sm:text-4xl font-extrabold text-gray-900 text-center tracking-tight">
      {children}
    </h2>
  );
};

export default SectionTitle;
