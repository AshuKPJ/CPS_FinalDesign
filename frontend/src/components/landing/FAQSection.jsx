// src/components/landing/FAQSection.jsx

import React, { useState } from "react";
import Section from "./shared/Section";
import SectionTitle from "./shared/SectionTitle";
import SectionSubtitle from "./shared/SectionSubtitle";
import { ChevronDown } from "lucide-react";

const faqs = [
  {
    question: "Is this just another email spam tool?",
    answer:
      "Absolutely not. CPS is the antithesis of email spam. By using a website's own contact form, your message is treated as a legitimate inquiry — resulting in near-perfect deliverability and higher trust.",
  },
  {
    question: "Do I need to find the contact page URL for each website?",
    answer:
      "No. Just provide the homepage URL (e.g. www.example.com) and our AI will automatically locate the correct contact page for you.",
  },
  {
    question: "How does personalization work?",
    answer:
      "You can use any column header from your CSV as a [token] in your message. CPS will replace it with the right value during each submission.",
  },
  {
    question: "What if a website has a CAPTCHA?",
    answer:
      "CPS integrates with captcha-solving services like DeathByCaptcha.com. You can also skip captcha-protected sites if desired.",
  },
  {
    question: "Can I use this for international outreach?",
    answer:
      "Yes! CPS supports full Unicode, so messages are delivered correctly on foreign language websites.",
  },
  {
    question: "Is there any cost in updating CPS software?",
    answer: "All updates of CPS are free — forever.",
  },
  {
    question: "What criteria can I use to choose the websites I want to target?",
    answer:
      "Search by city/state/zip, SIC/NAICS code, domain (.attorney, .plumber, etc.), or even entire country TLDs like .fr or .in.",
  },
  {
    question: "How many websites can it contact per day?",
    answer:
      "About 15,000 per day per thread if contact pages are known. About 10,000 per thread when discovery is needed.",
  },
];

const FaqItem = ({ q, a }) => {
  const [isOpen, setIsOpen] = useState(false);
  return (
    <div className="border-b border-gray-200 py-6">
      <dt>
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="w-full flex justify-between items-center text-left text-gray-800"
        >
          <span className="font-medium text-lg">{q}</span>
          <ChevronDown
            className={`h-6 w-6 transition-transform duration-300 ${
              isOpen ? "rotate-180" : ""
            }`}
          />
        </button>
      </dt>
      <dd
        className={`mt-2 overflow-hidden transition-all duration-300 ${
          isOpen ? "max-h-96" : "max-h-0"
        }`}
      >
        <p className="text-base text-gray-600">{a}</p>
      </dd>
    </div>
  );
};

const FAQSection = () => {
  return (
    <Section id="faq" className="bg-white">
      <SectionTitle>Frequently Asked Questions</SectionTitle>
      <SectionSubtitle>
        Still have questions? We’ve answered the most common ones below.
      </SectionSubtitle>

      <div className="mt-10 max-w-3xl mx-auto">
        <dl className="divide-y divide-gray-200">
          {faqs.map((item, index) => (
            <FaqItem key={index} q={item.question} a={item.answer} />
          ))}
        </dl>
      </div>
    </Section>
  );
};

export default FAQSection;
