// src/components/landing/FeaturesSection.jsx

import React, { useState } from "react";
import Section from "./shared/Section";
import SectionTitle from "./shared/SectionTitle";
import SectionSubtitle from "./shared/SectionSubtitle";
import { Zap, Code, Database, CheckCircle } from "lucide-react";

const featuresData = {
  "AI & Automation": {
    icon: Zap,
    points: [
      "AI-Powered Form Filling: Intelligently completes contact forms as if a human were doing it.",
      "Automated Contact Page Discovery: Just provide a homepage URL, and our AI finds the correct contact page.",
      "Seamless Captcha Solving: Integrates with services like DeathByCaptcha.com to bypass security checks.",
      "24/7/365 Operation: Your outreach campaigns run continuously, even while you sleep.",
      "Multi-Threaded Engine: Submits to tens of thousands of websites daily for massive reach.",
      "Multi-threaded and proxy supported — it is wicked fast to do massive submissions!",
    ],
  },
  "Advanced Personalization": {
    icon: Code,
    points: [
      "Dynamic Token Replacement: Use `[tokens]` for any column in your CSV to create deeply personalized messages.",
      "Unlimited Data Points: Leverage dozens of data values to craft unique, AI-generated presentations on the fly.",
      "Unicode Support: Flawlessly submit messages to foreign language websites without character issues.",
      "Master Profile Setup: Fill in your contact details once, and the AI handles the rest.",
    ],
  },
  "Powerful Data Engine": {
    icon: Database,
    points: [
      "Search the massive database of award-winning DatabaseEmailer.com for highly targeted sales leads, or use your own data!",
      "If there’s no contact page or emails listed, then upload those URLs in List Leaker to verify department emails like sales@ or support@.",
      "Smart Fallback: CPS shows sites that don’t have contact pages. Those sites likely have emails — use Email Fetcher to extract them!",
      "New URL Feed: Import lists of new businesses that just launched — beat your competitors to the inbox!",
    ],
  },
};

const FeaturesSection = () => {
  const [activeTab, setActiveTab] = useState("AI & Automation");

  return (
    <Section id="features" className="bg-gray-50">
      <SectionTitle>An Unfair Advantage for Your Outreach</SectionTitle>
      <SectionSubtitle className="text-xl font-semibold text-gray-600">
        CPS is packed with features that make it look like you manually filled in the contact page. Read each of these 3 categories:
      </SectionSubtitle>

      {/* Tabs */}
      <div className="mt-10 border-b border-gray-200">
        <nav className="flex justify-center space-x-8" aria-label="Feature Tabs">
          {Object.keys(featuresData).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab
                  ? "border-indigo-500 text-indigo-600"
                  : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
              }`}
            >
              {tab}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="mt-8">
        {Object.entries(featuresData).map(([tabName, data]) => (
          <div
            key={tabName}
            className={`${activeTab === tabName ? "block" : "hidden"}`}
          >
            <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-6">
              {data.points.map((point, index) => (
                <div key={index} className="flex items-start">
                  <CheckCircle className="h-6 w-6 text-green-500 flex-shrink-0 mt-1" />
                  <p className="ml-3 text-base text-gray-700">{point}</p>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </Section>
  );
};

export default FeaturesSection;
