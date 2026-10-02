import React from 'react';
import { Loader2 } from 'lucide-react';

interface LoadingStateProps {
  message?: string;
  minHeight?: string;
}

export const LoadingState: React.FC<LoadingStateProps> = ({
  message = 'Loading data from backend...',
  minHeight = 'min-h-[240px]',
}) => {
  return (
    <div className={`flex flex-col items-center justify-center p-8 text-center ${minHeight}`}>
      <Loader2 className="w-8 h-8 text-teal-600 animate-spin mb-3" />
      <p className="text-sm font-medium text-slate-600">{message}</p>
      <span className="text-xs text-slate-400 mt-1">Connecting to FastAPI backend</span>
    </div>
  );
};
