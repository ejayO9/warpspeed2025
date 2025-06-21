import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../components/ui/table';
import { Banknote, Landmark, LineChart, FileText, Handshake } from 'lucide-react';
import ChatPanel from '../components/ChatPanel';

const documents = [
  { title: 'Bank statements', icon: <Landmark size={24} /> },
  { title: 'Stocks', icon: <LineChart size={24} /> },
  { title: 'Mutual funds', icon: <Banknote size={24} /> },
  { title: 'Credit report', icon: <FileText size={24} /> },
];

const otherDocuments = [
  { title: 'Loan offers', icon: <Handshake size={24} /> },
];

const scenarios = [
  {
    option: 'Option A',
    pros: ['High down payment, lower EMI', 'Finishes by age ~70'],
    cons: ['Ties up more cash'],
  },
  {
    option: 'Option B',
    pros: ['Retains buffer and corpus', 'Affordable EMI'],
    cons: ['Longer tenure'],
  },
];

const RecommendationPage = () => {
  return (
    <div className="bg-slate-50 min-h-screen text-foreground font-sans">
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 p-8">
        {/* Left Column */}
        <div className="lg:col-span-3 space-y-8">
          <div>
            <h2 className="text-lg font-semibold mb-4 font-serif text-slate-600">Things I fetched.</h2>
            <div className="space-y-4">
              {documents.map((doc) => (
                <Card key={doc.title} className="bg-white hover:shadow-lg transition-shadow border-slate-200">
                  <CardContent className="flex items-center gap-4 p-4">
                    {doc.icon}
                    <span className="font-medium text-slate-700">{doc.title}</span>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
          <div>
            <h2 className="text-lg font-semibold mt-8 mb-4 font-serif text-slate-600">Other things</h2>
            <div className="space-y-4">
              {otherDocuments.map((doc) => (
                <Card key={doc.title} className="bg-white hover:shadow-lg transition-shadow border-slate-200">
                  <CardContent className="flex items-center gap-4 p-4">
                    {doc.icon}
                    <span className="font-medium text-slate-700">{doc.title}</span>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </div>

        {/* Middle Column */}
        <div className="lg:col-span-6 bg-white rounded-2xl shadow-2xl p-8 space-y-8">
          <h1 className="text-4xl font-bold font-serif text-slate-800">Recommendation</h1>
          <Card className="border-none shadow-none">
            <CardHeader className="p-0">
              <CardTitle className="font-serif text-slate-700">Summary</CardTitle>
            </CardHeader>
            <CardContent className="p-0 mt-4">
              <div className="prose prose-slate max-w-none">
                <p>
                  Pramod (62, retired) wants to buy a ₹45 L house. He has a large ₹2 Cr investment portfolio and ₹20k monthly rental income. Assuming an estimated monthly income of ₹1.2 L (rental + investment yield), and keeping a ₹20 L emergency buffer, we compare several options: (A) high down payment of ₹30 L + ₹15 L home loan → EMI ~₹18.6k but ties up more cash; (B) moderate down payment ₹22.5 L + ₹22.5 L home loan over 8 years at ~9% → EMI ~₹31.4k, finishes by age ~70, retains buffer and corpus; (C) all-cash uses ₹45 L but reduces corpus significantly; (D) loan-against-securities is affordable EMI but high interest and market risk. Option B is recommended: EMI fits comfortably within income, tenure aligns with age policies, and preserves buffer/investment. Next steps: verify lender acceptance of rental/investment income, prepare documentation, consider co-applicant if needed, and lock rates or plan prepayments if extra cash arises.
                </p>
              </div>
            </CardContent>
          </Card>

          <h2 className="text-2xl font-bold font-serif text-slate-800">Scenarios</h2>
          <Card className="border-slate-200">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-[200px]"> </TableHead>
                  <TableHead>Pros</TableHead>
                  <TableHead>Cons</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {scenarios.map((scenario) => (
                  <TableRow key={scenario.option}>
                    <TableCell className="font-medium">{scenario.option}</TableCell>
                    <TableCell>
                      <ul className="list-disc list-inside text-emerald-600">
                        {scenario.pros.map((pro) => <li key={pro}><span className="text-slate-700">{pro}</span></li>)}
                      </ul>
                    </TableCell>
                    <TableCell>
                      <ul className="list-disc list-inside text-rose-600">
                        {scenario.cons.map((con) => <li key={con}><span className="text-slate-700">{con}</span></li>)}
                      </ul>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Card>
        </div>

        {/* Right Column */}
        <div className="lg:col-span-3">
            <ChatPanel />
        </div>
      </div>
    </div>
  );
};

export default RecommendationPage;
