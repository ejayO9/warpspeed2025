import React, { useState } from 'react';
import { Check, Loader, ArrowRight } from 'lucide-react';

const analysisSteps = [
  { id: 'bank', title: 'Bank account', description: 'Transactional behaviour, cash reserves' },
  { id: 'stocks', title: 'Stocks, ETFs', description: 'Transactional behaviour, cash reserves' },
  { id: 'funds', title: 'Mutual funds', description: 'Transactional behaviour, cash reserves' },
  { id: 'credit', title: 'Credit history', description: 'Transactional behaviour, cash reserves' },
  { id: 'loans', title: 'Fetching loan offers', description: 'Finding best loan options for you' },
];

const StatusIndicator = ({ status, onStart }) => {
  switch (status) {
    case 'completed':
      return <div className="w-8 h-8 rounded-full bg-slate-100 flex items-center justify-center"><Check className="w-5 h-5 text-slate-400" /></div>;
    case 'in-progress':
      return <Loader className="w-8 h-8 text-blue-500 animate-spin" />;
    case 'yet-to-start':
      return (
        <button onClick={onStart} className="bg-slate-900 text-white text-sm font-medium px-4 py-2 rounded-full flex items-center gap-2 hover:bg-slate-700 transition-colors">
          <span>Start</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      );
    default:
      return null;
  }
};

const StepperIcon = ({ status }) => {
  if (status === 'completed') {
    return (
      <div className="w-9 h-9 rounded-full bg-slate-900 flex items-center justify-center ring-4 ring-white">
        <Check className="w-5 h-5 text-white" />
      </div>
    );
  }
  if (status === 'in-progress') {
    return (
      <div className="w-9 h-9 rounded-full bg-white border-2 border-slate-900 flex items-center justify-center ring-4 ring-white">
        <div className="w-3 h-3 bg-slate-900 rounded-full"></div>
      </div>
    );
  }
  // yet-to-start
  return (
    <div className="w-9 h-9 rounded-full bg-slate-300 ring-4 ring-white"></div>
  );
};

const AnalysingPage = () => {
  const [statuses, setStatuses] = useState({
    bank: 'yet-to-start',
    stocks: 'in-progress',
    funds: 'in-progress',
    credit: 'completed',
    loans: 'yet-to-start',
  });

  const handleStart = (id) => {
    // In a real app, you'd handle the logic here.
    // For this demo, we'll just log it.
    console.log(`Starting analysis for: ${id}`);
  };

  return (
    <div className="bg-white min-h-screen font-sans flex items-center justify-center p-4">
      <div className="w-full max-w-2xl mx-auto">
        <h1 className="text-4xl font-serif text-slate-800 mb-16 text-center">
          Let's understand your financial situation.
        </h1>
        <div className="relative pl-12">
          <div className="absolute left-[22px] top-4 bottom-4 w-0.5 bg-slate-200" aria-hidden="true"></div>
          <div className="space-y-8">
            {analysisSteps.map((step, index) => (
              <div key={step.id} className="relative flex items-center">
                <div className="absolute -left-12 top-1/2 -translate-y-1/2">
                  <StepperIcon status={statuses[step.id]} />
                </div>
                <div className={`flex-1 border rounded-2xl p-5 flex justify-between items-center w-full transition-colors ${statuses[step.id] === 'yet-to-start' ? 'bg-blue-50 border-blue-200' : 'bg-white border-slate-200'}`}>
                  <div className="text-left">
                    <h2 className="font-semibold text-slate-900">{step.title}</h2>
                    <p className="text-sm text-slate-500">{step.description}</p>
                  </div>
                  <div className="pl-4">
                    <StatusIndicator status={statuses[step.id]} onStart={() => handleStart(step.id)} />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalysingPage;
