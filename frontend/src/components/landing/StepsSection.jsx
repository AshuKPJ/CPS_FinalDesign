// src/components/landing/StepsSection.jsx

import React from "react";
import Section from "./shared/Section";
import SectionTitle from "./shared/SectionTitle";
import { UploadCloud, Edit3, Rocket } from "lucide-react";

const steps = [
  {
    icon: UploadCloud,
    title: "1. Upload Your List",
    description:
      "Import a simple CSV file containing the homepage URLs of your prospects.",
  },
  {
    icon: Edit3,
    title: "2. Craft Your Message",
    description:
      "Write your presentation and use [tokens] to personalize it with any data from your CSV.",
  },
  {
    icon: Rocket,
    title: "3. Launch & Automate",
    description:
      "Set your campaign live and let our AI engine work for you 24/7, delivering messages around the clock.",
  },
];

const StepsSection = () => {
  return (
    <Section id="steps" className="bg-white">
      <SectionTitle>3 Simple Steps</SectionTitle>
      <p className="mt-4 max-w-3xl mx-auto text-center text-xl text-gray-500 font-semibold">
        Get your first campaign running in minutes. It’s so user friendly!
      </p>

      <div className="mt-12 grid gap-8 md:grid-cols-3">
        {steps.map((step, idx) => (
          <div key={idx} className="text-center">
            <div className="flex items-center justify-center h-16 w-16 mx-auto bg-indigo-100 text-indigo-600 rounded-full">
              <step.icon className="h-8 w-8" />
            </div>
            <h3 className="mt-5 text-lg font-medium text-gray-900">
              {step.title}
            </h3>
            <p className="mt-2 text-base text-gray-600">{step.description}</p>
          </div>
        ))}
      </div>
    </Section>
  );
};

export default StepsSection;
