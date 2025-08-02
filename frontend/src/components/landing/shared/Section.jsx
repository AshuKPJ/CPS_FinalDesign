// src/components/landing/shared/Section.jsx

import React from "react";

const Section = ({ id, children, className = "" }) => {
  return (
    <section
      id={id}
      className={`py-20 px-4 sm:px-6 lg:px-8 ${className}`}
    >
      <div className="max-w-7xl mx-auto">{children}</div>
    </section>
  );
};

export default Section;
