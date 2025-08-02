// src/components/landing/BenefitsSection.jsx

import React from "react";
import Section from "./shared/Section";
import SectionTitle from "./shared/SectionTitle";
import SectionSubtitle from "./shared/SectionSubtitle";

const benefits = [
  {
    icon: "🎯",
    title: "Unmatched Deliverability",
    description:
      "Achieve virtually 100% open rate! By delivering your message through the website’s own contact form, you bypass spam filters and email gatekeepers entirely!",
  },
  {
    icon: "🤝",
    title: "Be a Welcome Guest",
    description:
      "Your personalized message is treated as a legitimate inquiry, not unsolicited spam. This builds trust and dramatically increases positive response rates.",
  },
  {
    icon: "🌳",
    title: "Evergreen Contact Data",
    description:
      "Website URLs are stable and don’t go stale. Stop wasting money on decaying email lists and build a permanent asset for your outreach efforts.",
  },
  {
    icon: "🚀",
    title: "Massive, Scalable Reach",
    description:
      "Our multi-threaded engine works 24/7, allowing you to connect with tens of thousands of prospects daily without any manual effort.",
  },
];

const BenefitsSection = () => {
  return (
    <Section id="benefits" className="bg-white">
      <SectionTitle>CPS is a Game-Changer because…</SectionTitle>
      <SectionSubtitle className="text-2xl font-semibold">
        It moves you way beyond traditional emailing, social media, cold calling, and spam marketing — and does it at a fraction of the cost.
      </SectionSubtitle>

      <div className="mt-12 grid gap-8 md:grid-cols-2 lg:grid-cols-4">
        {benefits.map((benefit, index) => (
          <div
            key={index}
            className="p-6 bg-gray-50 rounded-lg shadow hover:shadow-md transition"
          >
            <div className="text-4xl mb-4">{benefit.icon}</div>
            <h3 className="text-lg font-bold text-gray-900">
              {benefit.title}
            </h3>
            <p className="mt-2 text-base text-gray-600">{benefit.description}</p>
          </div>
        ))}
      </div>
    </Section>
  );
};

export default BenefitsSection;
