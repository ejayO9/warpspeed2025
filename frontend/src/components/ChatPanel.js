import React from 'react';
import { AudioLines } from 'lucide-react';
import { Card, CardContent } from './ui/card';

const ChatPanel = () => {
  return (
    <Card className="h-full flex flex-col bg-white rounded-2xl shadow-lg">
      <CardContent className="flex-grow flex flex-col items-center justify-between p-6 space-y-6">
        {/* Voice Visualizer Area */}
        <div className="flex-grow flex items-center justify-center">
          <button className="w-28 h-28 rounded-full bg-slate-100 flex items-center justify-center transition-transform transform hover:scale-105 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary shadow-[0_0_25px_rgba(168,85,247,0.2)]">
            <AudioLines className="text-slate-500" size={40} />
          </button>
        </div>
        
        {/* Input Area */}
        <div className="w-full">
          <input
            type="text"
            placeholder="Text or talk to me"
            className="w-full px-4 py-3 rounded-lg border-transparent bg-slate-100 text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>
      </CardContent>
    </Card>
  );
};

export default ChatPanel;
