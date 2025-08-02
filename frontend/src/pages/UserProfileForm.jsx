
// src/pages/UserProfileForm.jsx

// src/pages/UserProfileForm.jsx

import React, { useEffect, useState } from "react";
import { ChevronDown } from "lucide-react";
import api from "../services/api";
import toast from "react-hot-toast";

const UserProfileForm = () => {
  const [openSection, setOpenSection] = useState(0);
  const [formData, setFormData] = useState({});
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [showBanner, setShowBanner] = useState(false);

  const requiredFields = ["first_name", "last_name", "email"];

  const isValidUrl = (url) => {
    try {
      new URL(url);
      return true;
    } catch (_) {
      return false;
    }
  };

  const isValidEmail = (email) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  const isValidPhone = (phone) => /^[0-9()+\-\s]{7,20}$/.test(phone);
  const isLinkedInUrl = (url) => /^https?:\/\/(www\.)?linkedin\.com\/.*/i.test(url);

  const toggleSection = (idx) => setOpenSection((prev) => (prev === idx ? -1 : idx));

  useEffect(() => {
    let cancelled = false;
    const fetchData = async () => {
      try {
        const res = await api.get("/usercontactprofile/contact-answers");
        if (!cancelled) {
          setFormData(res.data || {});
        }
      } catch (err) {
        if (!cancelled) {
          console.error("Error fetching profile", err);
          toast.error("Failed to load profile data.");
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    };
    fetchData();
    return () => {
      cancelled = true;
    };
  }, []);

  const validateField = (id, value) => {
    let message = "";
    let fixedValue = value;

    if (requiredFields.includes(id) && (!value || (typeof value === "string" && !value.trim()))) {
      message = `${id.replace("_", " ")} is required.`;
    }

    if (id === "email" && value && !isValidEmail(value)) {
      message = "Invalid email format.";
    }
    if (id === "phone_number" && value && !isValidPhone(value)) {
      message = "Invalid phone number format.";
    }
    if (id === "website_url" && value) {
      if (!/^https?:\/\//i.test(value)) fixedValue = "https://" + value;
      if (!isValidUrl(fixedValue)) message = "Invalid website URL.";
      else setFormData((prev) => ({ ...prev, [id]: fixedValue }));
    }
    if (id === "linkedin_url" && value && !isLinkedInUrl(value)) {
      message = "LinkedIn URL must start with https://www.linkedin.com/";
    }

    setErrors((prevErrors) => ({ ...prevErrors, [id]: message || undefined }));
  };

  const handleChange = (e) => {
    const { id, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [id]: e.target.type === "select-one" && id === "is_existing_customer"
        ? value === "true"
        : value,
    }));
    if (errors[id] && value) {
      setErrors((prev) => {
        const { [id]: removed, ...rest } = prev;
        return rest;
      });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setErrors({});

    const newErrors = {};
    for (let field of requiredFields) {
      const val = formData[field];
      if (!val || (typeof val === "string" && !val.trim())) {
        newErrors[field] = `${field.replace("_", " ")} is required.`;
      }
    }

    if (formData.email && !isValidEmail(formData.email)) newErrors.email = "Invalid email format.";
    if (formData.phone_number && !isValidPhone(formData.phone_number)) newErrors.phone_number = "Invalid phone number.";
    if (formData.website_url && !isValidUrl(/^https?:\/\//i.test(formData.website_url) ? formData.website_url : "https://" + formData.website_url)) newErrors.website_url = "Invalid website URL.";
    if (formData.linkedin_url && !isLinkedInUrl(formData.linkedin_url)) newErrors.linkedin_url = "Invalid LinkedIn URL.";

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      toast.error("Please correct the errors in the form.");
      setSubmitting(false);
      window.scrollTo({ top: 0, behavior: "smooth" });
      return;
    }

    const toastId = toast.loading("Saving profile...");

    try {
      await api.post("/usercontactprofile/upsert", formData);
      toast.success("✅ Profile saved successfully.", { id: toastId });
      setShowBanner(true);
      setTimeout(() => setShowBanner(false), 4000);
      setOpenSection(-1);
    } catch (err) {
      console.error(err);
      toast.error("❌ Failed to save profile.", { id: toastId });
    } finally {
      setSubmitting(false);
      window.scrollTo({ top: 0, behavior: "smooth" });
    }
  };

  const sections = [
    {
      title: "Basic Identity",
      fields: [
        ["first_name", "First Name"],
        ["last_name", "Last Name"],
        ["email", "Email"],
        ["phone_number", "Phone Number"],
        ["linkedin_url", "LinkedIn URL"],
      ],
    },
    {
      title: "Company Details",
      fields: [
        ["company_name", "Company Name"],
        ["job_title", "Job Title"],
        ["website_url", "Website URL"],
        ["industry", "Industry"],
      ],
    },
    {
      title: "Geographic Information",
      fields: [
        ["city", "City"],
        ["state", "State"],
        ["zip_code", "Zip Code"],
        ["country", "Country"],
        ["region", "Region"],
        ["timezone", "Timezone"],
      ],
    },
    {
      title: "Inquiry Details",
      fields: [
        ["subject", "Subject"],
        ["message", "Message", "textarea"],
        ["product_interest", "Product Interest"],
        ["budget_range", "Budget Range"],
        ["referral_source", "Referral Source"],
        ["preferred_contact", "Preferred Contact Method"],
        ["best_time_to_contact", "Best Time to Contact"],
      ],
    },
    {
      title: "Additional Context",
      fields: [
        ["contact_source", "Contact Source"],
        [
          "is_existing_customer",
          "Is Existing Customer?",
          "select",
          [
            { value: "false", label: "No" },
            { value: "true", label: "Yes" },
          ],
        ],
        ["language", "Language"],
        ["preferred_language", "Preferred Language"],
        ["notes", "Notes", "textarea"],
        ["form_custom_field_1", "Custom Field 1"],
        ["form_custom_field_2", "Custom Field 2"],
        ["form_custom_field_3", "Custom Field 3"],
      ],
    },
  ];

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        Loading profile...
      </div>
    );
  }

  return (
    <div className="p-4 sm:p-6 md:p-8 min-h-screen bg-gray-50">
      {showBanner && (
        <div className="bg-green-100 border border-green-400 text-green-800 px-6 py-3 rounded-lg text-center mb-6 animate-fade-in">
          ✅ Profile saved successfully!
        </div>
      )}

      <form
        onSubmit={handleSubmit}
        className="max-w-5xl mx-auto bg-white shadow-xl rounded-xl overflow-hidden"
      >
        <div className="px-6 py-8">
          <h1 className="text-2xl font-bold text-center text-gray-900 mb-6">
            User Profile Form
          </h1>

          {sections.map((section, idx) => (
            <div key={idx} className="mb-4 border rounded-lg">
              <button
                type="button"
                onClick={() => toggleSection(idx)}
                className="w-full flex justify-between items-center px-4 py-3 bg-gray-50 hover:bg-gray-100"
              >
                <span className="font-semibold text-gray-800">
                  {section.title}
                </span>
                <ChevronDown
                  className={`h-5 w-5 text-gray-500 transform transition-transform ${openSection === idx ? "rotate-180" : ""
                    }`}
                />
              </button>

              <div
                className={`transition-all duration-300 overflow-hidden px-4 ${openSection === idx ? "max-h-[2000px] py-4" : "max-h-0"
                  }`}
              >
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {section.fields.map(([id, label, type = "text", options]) => (
                    <div key={id} className="md:col-span-1">
                      <label
                        htmlFor={id}
                        className="block text-sm font-medium text-gray-700 mb-1"
                      >
                        {label}
                      </label>

                      {type === "textarea" ? (
                        <>
                          <textarea
                            id={id}
                            value={formData[id] || ""}
                            onChange={handleChange}
                            onBlur={(e) => validateField(id, e.target.value)}
                            rows="4"
                            className={`form-textarea block w-full rounded-md border px-3 py-2 ${errors[id]
                              ? "border-red-500"
                              : typeof formData[id] === "string" &&
                                formData[id].trim()
                                ? "border-green-500"
                                : "border-gray-300"
                              }`}
                          />
                          {errors[id] && (
                            <p className="text-red-500 text-sm mt-1">
                              {errors[id]}
                            </p>
                          )}
                        </>
                      ) : type === "select" ? (
                        <>
                          <select
                            id={id}
                            value={
                              formData[id] === true
                                ? "true"
                                : formData[id] === false
                                  ? "false"
                                  : ""
                            }
                            onChange={handleChange}
                            onBlur={(e) => validateField(id, e.target.value)}
                            className={`form-select block w-full rounded-md border px-3 py-2 ${errors[id]
                              ? "border-red-500"
                              : typeof formData[id] === "string" &&
                                formData[id].trim()
                                ? "border-green-500"
                                : "border-gray-300"
                              }`}
                          >
                            {options.map((opt) => (
                              <option key={opt.value} value={opt.value}>
                                {opt.label}
                              </option>
                            ))}
                          </select>
                          {errors[id] && (
                            <p className="text-red-500 text-sm mt-1">
                              {errors[id]}
                            </p>
                          )}
                        </>
                      ) : (
                        <>
                          <input
                            type={type}
                            id={id}
                            value={formData[id] || ""}
                            onChange={handleChange}
                            onBlur={(e) => validateField(id, e.target.value)}
                            className={`form-input block w-full rounded-md border px-3 py-2 ${errors[id]
                              ? "border-red-500"
                              : typeof formData[id] === "string" &&
                                formData[id].trim()
                                ? "border-green-500"
                                : "border-gray-300"
                              }`}
                          />
                          {errors[id] && (
                            <p className="text-red-500 text-sm mt-1">
                              {errors[id]}
                            </p>
                          )}
                        </>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ))}

          <button
            type="submit"
            disabled={submitting}
            className={`mt-6 w-full font-semibold py-3 px-4 rounded-lg transition flex items-center justify-center gap-2 ${submitting
              ? "bg-gray-400 cursor-not-allowed"
              : "bg-blue-600 hover:bg-blue-700 text-white"
              }`}
          >
            {submitting && (
              <svg
                className="animate-spin h-5 w-5 text-white"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                ></circle>
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"
                ></path>
              </svg>
            )}
            {submitting ? "Saving..." : "Save Information"}
          </button>
        </div>
      </form>
    </div>
  );
};

export default UserProfileForm;
