// frontend/src/components/StatCard.jsx

import React from 'react';
import Card, { CardContent } from './ui/card';
import cn  from '../lib/utils';

const StatCard = ({ title, value, icon: Icon, color = 'text-white', bgColor = 'bg-indigo-600' }) => {
  return (
    <Card className={cn('shadow-md rounded-xl', bgColor)}>
      <CardContent className="flex items-center justify-between p-6 text-white">
        <div>
          <p className="text-sm font-medium text-gray-200">{title}</p>
          <p className="text-2xl font-semibold text-white mt-1">{value}</p>
        </div>
        {Icon && <Icon className="h-10 w-10 text-white opacity-90" />}
      </CardContent>
    </Card>
  );
};

export default StatCard;
