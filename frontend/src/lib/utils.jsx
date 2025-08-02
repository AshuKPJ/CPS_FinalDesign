// frontend/src/lib/utils.jsx

/**
 * Combines multiple class names into one string (similar to classnames library).
 * Filters out falsy values.
 * @param  {...string} classes
 * @returns {string}
 */
const cn = (...classes) => {
  return classes.filter(Boolean).join(' ');
};

/**
 * Returns a Tailwind background color class based on the input color key.
 * If no matching color is found, defaults to gray.
 *
 * @param {string} color - One of: 'indigo', 'green', 'blue', 'yellow', 'red', 'gray'
 * @returns {string} Tailwind CSS class for background color
 */
export const getColorClass = (color) => {
  const colors = {
    indigo: 'bg-indigo-500',
    green: 'bg-green-500',
    blue: 'bg-blue-500',
    yellow: 'bg-yellow-500',
    red: 'bg-red-500',
    gray: 'bg-gray-500',
  };

  return colors[color] || 'bg-gray-500';
};

export default cn;
