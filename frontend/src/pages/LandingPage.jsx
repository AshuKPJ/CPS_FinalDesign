// src/pages/LandingPage.jsx

import React, { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import useAuth from "../hooks/useAuth";

import HeroSection from "../components/landing/HeroSection";
import StepsSection from "../components/landing/StepsSection";
import FeaturesSection from "../components/landing/FeaturesSection";
import BenefitsSection from "../components/landing/BenefitsSection";
import TestimonialsSection from "../components/landing/TestimonialsSection";
import GallerySection from "../components/landing/GallerySection";
import IntegrationsSection from "../components/landing/IntegrationsSection";
import FAQSection from "../components/landing/FAQSection";

const LandingPage = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (user?.role === "admin") navigate("/admin");
    else if (user?.role === "owner") navigate("/owner");
    else if (user?.role === "user") navigate("/user");
  }, [user, navigate]);

  return (
    <div className="bg-white text-gray-800">
      <main>
        <HeroSection />
        <StepsSection />
        <FeaturesSection />
        <BenefitsSection />
        <TestimonialsSection />
        <GallerySection />
        <IntegrationsSection />
        <FAQSection />
      </main>
    </div>
  );
};

export default LandingPage;
