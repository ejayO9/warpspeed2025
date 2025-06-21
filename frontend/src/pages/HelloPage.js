import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { AudioLines, Send } from 'lucide-react';

const HelloPage = () => {
  return (
    <div className="min-h-screen bg-slate-50 flex items-start justify-center p-8">
      <div className="w-full max-w-2xl">
        <Card className="bg-white rounded-2xl shadow-xl h-[80vh] flex flex-col">
          <CardHeader className="border-b border-slate-100">
            <CardTitle className="font-serif text-slate-800">Financial Assistant</CardTitle>
          </CardHeader>
          
          {/* Chat Messages Area - Empty state */}
          <div className="flex-1 p-6 overflow-y-auto">
            <div className="text-center text-slate-500 mt-16">
              <AudioLines className="w-12 h-12 mx-auto mb-4 text-slate-300" />
              <p className="text-lg font-medium">Ask me anything about your finances</p>
              <p className="text-sm mt-2">I can help analyze your documents and provide insights</p>
            </div>
          </div>
          
          {/* Input Area */}
          <div className="p-4 border-t border-slate-100">
            <div className="flex items-center gap-2">
              <button 
                className="p-3 rounded-full transition-colors text-slate-50"
                aria-label="Start voice input"
              >
                <AudioLines className="w-5 h-5" />
              </button>
              <div className="relative flex-1">
                <input
                  type="text"
                  placeholder="Type your message..."
                  className="w-full bg-white border border-slate-200 rounded-full py-3 pl-4 pr-12 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent text-slate-700 placeholder-slate-400 dark:bg-white dark:text-slate-800 dark:border-slate-300 dark:placeholder-slate-500"
                  style={{
                    backgroundColor: 'white',
                    color: '#1e293b',
                    borderColor: '#e2e8f0',
                    '--tw-ring-color': 'rgba(168, 85, 247, 0.5)'
                  }}
                />
                <button 
                  className="absolute right-2 top-1/2 transform -translate-y-1/2 p-1 text-slate-400 hover:text-purple-600 transition-colors"
                  aria-label="Send message"
                >
                  <Send className="w-5 h-5" />
                </button>
              </div>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default HelloPage;
