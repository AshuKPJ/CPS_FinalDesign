// src/components/landing/GallerySection.jsx

import React, { useState } from "react";
import Section from "./shared/Section";
import SectionTitle from "./shared/SectionTitle";
import SectionSubtitle from "./shared/SectionSubtitle";

const gallery = [
  { title: "Dashboard", imageUrl: "/images/dash-graphics.png" },
  { title: "User Info", imageUrl: "/images/cps-answers-to-questions.png" },
  { title: "Submission Results", imageUrl: "/images/submission-results.png" },
  { title: "Campaign Settings", imageUrl: "https://placehold.co/600x400/1e40af/FFFFFF?text=Campaign+Settings" },
  { title: "CPS Settings", imageUrl: "https://placehold.co/600x400/1e40af/FFFFFF?text=CPS+Settings" },
  { title: "Form Submitter", imageUrl: "/images/cps-form-submitter.png" },
];

const GallerySection = () => {
  const [lightboxOpen, setLightboxOpen] = useState(false);
  const [activeIndex, setActiveIndex] = useState(0);

  const openLightbox = (index) => {
    setActiveIndex(index);
    setLightboxOpen(true);
  };

  const closeLightbox = () => setLightboxOpen(false);

  const showPrev = () =>
    setActiveIndex((prev) => (prev - 1 + gallery.length) % gallery.length);
  const showNext = () =>
    setActiveIndex((prev) => (prev + 1) % gallery.length);

  return (
    <Section id="gallery" className="bg-white">
      <SectionTitle>Admin Dashboard Screenshots</SectionTitle>
      <SectionSubtitle>
        Take a look inside the powerful and user-friendly CPS dashboard.
      </SectionSubtitle>

      {/* Image Grid */}
      <div className="mt-12 grid grid-cols-2 md:grid-cols-3 gap-4">
        {gallery.map((img, idx) => (
          <div
            key={idx}
            className="group relative cursor-pointer h-64"
            onClick={() => openLightbox(idx)}
          >
            <img
              src={img.imageUrl}
              alt={img.title}
              className="w-full h-full object-cover rounded-lg shadow-md"
            />
            <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-300">
              <p className="text-white font-bold text-lg">{img.title}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Lightbox Modal */}
      {lightboxOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-80 z-50 flex items-center justify-center">
          <div className="relative max-w-4xl max-h-[90vh] mx-auto">
            <img
              src={gallery[activeIndex].imageUrl}
              alt={gallery[activeIndex].title}
              className="max-h-[80vh] rounded shadow-lg"
            />
            <button
              onClick={closeLightbox}
              className="absolute top-4 right-4 text-white text-3xl"
            >
              &times;
            </button>
            <button
              onClick={showPrev}
              className="absolute left-4 top-1/2 -translate-y-1/2 text-white text-3xl"
            >
              &#8249;
            </button>
            <button
              onClick={showNext}
              className="absolute right-4 top-1/2 -translate-y-1/2 text-white text-3xl"
            >
              &#8250;
            </button>
          </div>
        </div>
      )}
    </Section>
  );
};

export default GallerySection;
