// src/components/landing/HeroSection.jsx

import React from "react";
import { Phone, Mail } from "lucide-react";

const HeroSection = ({ onLogin, onRegister }) => {
  return (
    <section className="bg-zinc-50 pt-24 pb-12">
      <div className="max-w-7xl mx-auto grid lg:grid-cols-12 gap-8 px-4 sm:px-6 lg:px-8">
        {/* Text Content */}
        <div className="lg:col-span-7 flex items-center">
          <div>
            <h1 className="text-4xl sm:text-5xl md:text-6xl font-extrabold text-gray-900 leading-tight">
              Get <span className="text-indigo-600">100% Open Rate</span>
              <br />
              <span className="text-indigo-600"> & Look Professional!</span>
            </h1>

            <p className="mt-6 text-lg text-gray-600">
              The cost to use CPS is miniscule compared to emailing; plus,
              it’s much more effective as you appear so much more professional!
            </p>
            <p className="mt-4 text-lg text-gray-600">
              Open rates when emailing are puny compared to the 100% open rate CPS gets! User-friendly CPS works online as it imports fresh sales leads; it then uses AI to find contact pages, generate personalized messages, and solve captchas and submit!
            </p>

            <div className="mt-6 flex flex-wrap items-center gap-4">
              <button
                onClick={onLogin}
                className="px-6 py-3 text-sm font-medium text-indigo-700 bg-indigo-100 rounded-md hover:bg-indigo-200 transition"
              >
                Login
              </button>
              <button
                onClick={onRegister}
                className="px-6 py-3 text-sm font-medium text-white bg-indigo-600 rounded-md hover:bg-indigo-700 transition"
              >
                Sign Up
              </button>
            </div>

            <div className="mt-6 space-y-1 text-sm text-gray-600">
              <a
                href="tel:973-618-9906"
                className="flex items-center hover:text-gray-900"
              >
                <Phone className="h-4 w-4 mr-2" />
                973.618.9906
              </a>
              <a
                href="mailto:AL@DBE.name"
                className="flex items-center hover:text-gray-900"
              >
                <Mail className="h-4 w-4 mr-2" />
                AL@DBE.name
              </a>
            </div>
          </div>
        </div>

        {/* Hero Video */}
        <div className="lg:col-span-5 flex justify-center items-center">
          <video
            className="w-full h-auto object-cover rounded-xl shadow-2xl max-h-[450px]"
            src="https://videos.pexels.com/video-files/3209828/3209828-hd_1920_1080_25fps.mp4"
            autoPlay
            loop
            muted
            playsInline
          />
        </div>
      </div>
    </section>
  );
};

export default HeroSection;
