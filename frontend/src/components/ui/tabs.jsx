import React, { useState } from 'react';

const Tabs = ({ tabs = [], defaultIndex = 0 }) => {
  const [activeIndex, setActiveIndex] = useState(defaultIndex);

  return (
    <div>
      {/* Tab Headers */}
      <div className="flex space-x-4 border-b border-gray-300">
        {tabs.map((tab, idx) => (
          <button
            key={idx}
            onClick={() => setActiveIndex(idx)}
            className={`px-4 py-2 font-medium border-b-2 transition-all ${
              activeIndex === idx
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-blue-500'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="mt-4">
        {tabs[activeIndex]?.content || <div>No content</div>}
      </div>
    </div>
  );
};

export default Tabs;
