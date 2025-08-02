// src/components/landing/TestimonialsSection.jsx

import React from "react";
import Section from "./shared/Section";
import SectionTitle from "./shared/SectionTitle";
import SectionSubtitle from "./shared/SectionSubtitle";

const testimonials = [
  {
    quote:
      "CPS has completely changed our way to contact businesses. We're reaching prospects we could never get to before, and the response has been great.",
    name: "Sarah Johnson",
    title: "Marketing Director",
  },
  {
    quote:
      "The cost savings compared to our old email campaigns are staggering. Not only are we spending less, but the results are 50x better.",
    name: "Gunderson Helscroft",
    title: "CEO",
  },
  {
    quote:
      "We're no longer just another email in a crowded inbox. We're a priority message, and it shows in our conversions.",
    name: "Jessica Simmons",
    title: "Head of Sales",
  },
  {
    quote:
      "I didn't want to give a testimonial because I didn't want anyone to know we use CPS big time. HAHA! It kicks the 💩 outta email and social ads.",
    name: "Johnny Baker",
    title: "Business Ops Manager",
  },
  {
    quote:
      "The ability to automate contacts has freed up so much time for us to focus on closing deals. They have no clue the submissions are automated!",
    name: "Rob Shaw",
    title: "Sales Manager",
  },
  {
    quote:
      "I’ve been marketing for 30 years and nothing has ever performed like this. It's in a league of its own.",
    name: "Kim Gregory",
    title: "Owner",
  },
];

const TestimonialsSection = () => {
  return (
    <Section id="testimonials" className="bg-gray-50">
      <SectionTitle>Since 2018 CPS has been Trusted by Marketing Leaders!</SectionTitle>
      <SectionSubtitle>
        The online CPS is even better — it uses AI, pulls fresh URLs, and gets contact pages confirmed by other users!
      </SectionSubtitle>

      <div className="mt-12 overflow-x-auto pb-4">
        <div className="flex space-x-6 min-w-full">
          {testimonials.map((t, idx) => (
            <div
              key={idx}
              className="flex-shrink-0 w-80 bg-white p-6 rounded-lg shadow-md border"
            >
              <p className="text-gray-600 italic">"{t.quote}"</p>
              <div className="mt-4">
                <p className="font-semibold text-gray-900">{t.name}</p>
                <p className="text-gray-500 text-sm">{t.title}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </Section>
  );
};

export default TestimonialsSection;
