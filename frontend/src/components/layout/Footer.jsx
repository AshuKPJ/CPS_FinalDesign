// src/components/landing/Footer.jsx

import React from "react";

const Footer = () => {
  return (
    <footer className="bg-gray-800 text-gray-300">
      <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col items-center text-center space-y-8">
          {/* Logo */}
          <div className="flex items-center space-x-2">
            <img
              className="h-20"
              src="/assets/images/CPS_footer_logo.png"
              alt="CPS Logo"
            />
          </div>

          {/* Blurb */}
          <p className="text-lg max-w-xl">
            The effective, professional, low-cost way to deliver automated
            personalized messages — at scale!
          </p>

          {/* Footer links */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-left w-full max-w-4xl">
            <div>
              <h4 className="text-sm font-semibold text-gray-400 uppercase">
                Solutions
              </h4>
              <ul className="mt-4 space-y-2">
                <li>
                  <a href="#features" className="hover:text-white">
                    Features
                  </a>
                </li>
                <li>
                  <a href="#benefits" className="hover:text-white">
                    Benefits
                  </a>
                </li>
              </ul>
            </div>
            <div>
              <h4 className="text-sm font-semibold text-gray-400 uppercase">
                Company
              </h4>
              <ul className="mt-4 space-y-2">
                <li>
                  <a href="#about" className="hover:text-white">
                    About
                  </a>
                </li>
                <li>
                  <a
                    href="https://www.databaseemailer.com/tos.php"
                    className="hover:text-white"
                  >
                    Contact
                  </a>
                </li>
              </ul>
            </div>
            <div>
              <h4 className="text-sm font-semibold text-gray-400 uppercase">
                Legal
              </h4>
              <ul className="mt-4 space-y-2">
                <li>
                  <a
                    href="https://www.databaseemailer.com/tos.php"
                    className="hover:text-white"
                  >
                    Privacy
                  </a>
                </li>
                <li>
                  <a
                    href="https://www.databaseemailer.com/tos.php"
                    className="hover:text-white"
                  >
                    Terms
                  </a>
                </li>
              </ul>
            </div>
          </div>
        </div>

        <div className="mt-12 border-t border-gray-700 pt-8 text-center">
          <p className="text-base text-gray-400">
            &copy; {new Date().getFullYear()} Contact Page Submitter. All
            rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
