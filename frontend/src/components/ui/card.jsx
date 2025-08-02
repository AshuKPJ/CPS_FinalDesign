// frontend/src/components/ui/card.jsx
import React from 'react';
import classNames from 'classnames';

const Card = ({ children, className = '', ...props }) => (
  <div className={classNames('bg-white p-6 rounded-lg shadow-md', className)} {...props}>
    {children}
  </div>
);

// ✅ Add CardContent
export const CardContent = ({ children, className = '', ...props }) => (
  <div className={classNames('p-4', className)} {...props}>
    {children}
  </div>
);

export default Card;
