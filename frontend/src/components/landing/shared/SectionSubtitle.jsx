// src/components/landing/shared/SectionSubtitle.jsx

import React from "react";

const SectionSubtitle = ({ children, className = "" }) => {
  return (
    <p
      className={`mt-4 max-w-3xl mx-auto text-center text-lg text-gray-500 ${className}`}
    >
      {children}
    </p>
  );
};

export default SectionSubtitle;
