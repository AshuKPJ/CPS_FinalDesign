// src/components/landing/IntegrationsSection.jsx

import React from "react";
import Section from "./shared/Section";
import SectionTitle from "./shared/SectionTitle";
import SectionSubtitle from "./shared/SectionSubtitle";

const integrations = [
  {
    name: "DatabaseEmailer.com",
    description:
      "Fuel your campaigns with access to an award-winning database of over 80 million business URLs.",
    logo: "/images/database-logo.png",
  },
  {
    name: "CSVMIX.com",
    description:
      "Clean, enrich, and prepare your data for maximum impact. Append valuable socio-economic data for hyper-targeted presentations.",
    logo: "/images/csvmix-logo.png",
  },
  {
    name: "SavingsCRM.com",
    description:
      "CPS imports data from the feature-rich Savings CRM, then auto-returns the CPS results back to the CRM!",
    logo: "/images/savings-crm-logo.png", // You can replace this placeholder
  },
];

const IntegrationsSection = () => {
  return (
    <Section id="integrations" className="bg-gray-900 text-white">
      <SectionTitle>A Powerful, Connected Ecosystem</SectionTitle>
      <SectionSubtitle className="text-indigo-200 text-xl font-medium">
        CPS integrates with industry leaders to supercharge your campaigns from start to finish — from data sourcing to personalized delivery and CRM sync.
      </SectionSubtitle>

      <div className="mt-12 grid gap-8 md:grid-cols-3">
        {integrations.map((integration, index) => (
          <div
            key={index}
            className="flex flex-col items-center text-center p-6 bg-white text-gray-800 rounded-lg shadow"
          >
            <img
              src={integration.logo}
              alt={`${integration.name} Logo`}
              className="h-12 mb-4"
            />
            <h3 className="text-lg font-semibold">{integration.name}</h3>
            <p className="mt-2 text-base text-gray-600">
              {integration.description}
            </p>
          </div>
        ))}
      </div>
    </Section>
  );
};

export default IntegrationsSection;
