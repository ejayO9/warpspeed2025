import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../components/ui/table';
import Modal from '../components/ui/modal';
import { Banknote, Landmark, LineChart, FileText, Handshake, Eye } from 'lucide-react';
import ChatPanel from '../components/ChatPanel';
import BankStatementsModal from '../components/BankStatementsModal';
import { API_URL } from '../config';

const documents = [
  { title: 'Bank statements', icon: <Landmark size={24} /> },
  { title: 'Stocks', icon: <LineChart size={24} /> },
  { title: 'Mutual funds', icon: <Banknote size={24} /> },
  { title: 'Credit report', icon: <FileText size={24} /> },
];

const otherDocuments = [
  { title: 'Loan offers', icon: <Handshake size={24} /> },
];

const RecommendationPage = () => {
  const [isBankStatementsModalOpen, setIsBankStatementsModalOpen] = useState(false);
  const [scrollTarget, setScrollTarget] = useState(null);
  const [financialInfo, setFinancialInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedScenario, setSelectedScenario] = useState(null);
  const [isScenarioModalOpen, setIsScenarioModalOpen] = useState(false);

  // Fetch financial info when component mounts
  useEffect(() => {
    const fetchFinancialInfo = async () => {
      try {
        // Using user_id = 1 for demo purposes. In a real app, this would come from auth context
        const response = await fetch(`${API_URL}/users/1/financial-info`);
        if (response.ok) {
          const data = await response.json();
          setFinancialInfo(data);
        } else {
          console.error('Failed to fetch financial info:', response.status, response.statusText);
        }
      } catch (error) {
        console.error('Error fetching financial info:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchFinancialInfo();
  }, []);

  const handleDocumentClick = (docTitle) => {
    let targetSection = null;
    
    switch (docTitle) {
      case 'Bank statements':
        targetSection = 'balance-history';
        break;
      case 'Stocks':
        targetSection = 'equity-portfolio';
        break;
      case 'Mutual funds':
        targetSection = 'mutual-funds';
        break;
      case 'Credit report':
        targetSection = 'credit-report';
        break;
      default:
        targetSection = null;
    }
    
    setScrollTarget(targetSection);
    setIsBankStatementsModalOpen(true);
  };

  const handleViewDetails = (scenario) => {
    setSelectedScenario(scenario);
    setIsScenarioModalOpen(true);
  };

  const formatCurrency = (value) => {
    if (typeof value === 'number') {
      return `₹${(value / 100000).toFixed(1)} L`;
    }
    return value;
  };

  const renderScenarioDetails = (scenario) => {
    if (!scenario) return null;

    return (
      <div className="space-y-6">
        <div>
          <h3 className="text-lg font-semibold text-slate-800 mb-3">Assumptions</h3>
          <div className="bg-slate-50 p-4 rounded-lg space-y-2">
            <div className="grid grid-cols-2 gap-4">
              <div><strong>Down Payment:</strong> {formatCurrency(scenario.assumptions?.downPayment)}</div>
              <div><strong>Loan Amount:</strong> {formatCurrency(scenario.assumptions?.loanAmount)}</div>
              <div><strong>Interest Rate:</strong> {scenario.assumptions?.interestRate}%</div>
              <div><strong>Tenure:</strong> {scenario.assumptions?.tenureYears} years</div>
            </div>
          </div>
        </div>

        <div>
          <h3 className="text-lg font-semibold text-slate-800 mb-3">Calculations</h3>
          <div className="bg-slate-50 p-4 rounded-lg space-y-2">
            <div><strong>Estimated EMI:</strong> ₹{scenario.calculations?.estimatedEMI?.toLocaleString()}</div>
            <div><strong>Total Interest Payable:</strong> {formatCurrency(scenario.calculations?.totalInterestPayable)}</div>
            <div><strong>DTI Ratio:</strong> {scenario.calculations?.DTI}</div>
            <div><strong>Remaining Liquid Investments:</strong> {formatCurrency(scenario.calculations?.remainingLiquidInvestments)}</div>
          </div>
        </div>

        <div>
          <h3 className="text-lg font-semibold text-slate-800 mb-3">Risk Assessment</h3>
          <div className="bg-amber-50 p-4 rounded-lg border border-amber-200">
            <p className="text-slate-700">{scenario.riskAssessment}</p>
          </div>
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="bg-slate-50 min-h-screen flex items-center justify-center">
        <div className="text-slate-600">Loading financial information...</div>
      </div>
    );
  }

  const scenarios = financialInfo?.scenarios || [];
  const summary = financialInfo?.humanSummary || '';

  return (
    <div className="bg-slate-50 min-h-screen text-foreground font-sans">
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 p-8 h-[calc(100vh-2rem)]">
        {/* Left Column */}
        <div className="lg:col-span-3 space-y-8">
          <div>
            <h2 className="text-lg font-semibold mb-4 font-serif text-slate-600 text-left">Things I fetched.</h2>
            <div className="space-y-4">
              {documents.map((doc) => (
                <Card 
                  key={doc.title} 
                  className="bg-white hover:shadow-lg transition-shadow border-slate-200 cursor-pointer"
                  onClick={() => handleDocumentClick(doc.title)}
                >
                  <CardContent className="flex items-center gap-4 p-4">
                    {doc.icon}
                    <span className="font-medium text-slate-700">{doc.title}</span>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
          <div>
            <h2 className="text-lg font-semibold mt-8 mb-4 font-serif text-slate-600 text-left">Other things</h2>
            <div className="space-y-4">
              {otherDocuments.map((doc) => (
                <Card 
                  key={doc.title} 
                  className="bg-white hover:shadow-lg transition-shadow border-slate-200 cursor-pointer"
                  onClick={() => handleDocumentClick(doc.title)}
                >
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
        <div className="lg:col-span-6 bg-white rounded-2xl shadow-lg p-8 space-y-8 h-full text-left overflow-y-auto">
          <h1 className="text-4xl font-bold font-serif text-slate-800">Recommendation</h1>
          <Card className="border border-slate-100 bg-slate-50 rounded-2xl p-6 shadow-sm">
            <CardHeader className="p-0">
              <CardTitle className="font-serif text-slate-700">Summary</CardTitle>
            </CardHeader>
            <CardContent className="p-0 mt-4">
              <div className="prose prose-slate max-w-none text-left">
                <p className="text-slate-700">
                  {summary}
                </p>
              </div>
            </CardContent>
          </Card>

          <h2 className="text-2xl font-bold font-serif text-slate-800 text-left">Scenarios</h2>
          <Card className="border-slate-200">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-[250px]">Scenario</TableHead>
                  <TableHead>Pros</TableHead>
                  <TableHead>Cons</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {scenarios.map((scenario, index) => (
                  <TableRow key={index}>
                    <TableCell className="font-medium">
                      <div className="space-y-2">
                        <div>{scenario.scenarioName}</div>
                        <button
                          onClick={() => handleViewDetails(scenario)}
                          className="inline-flex items-center gap-2 px-3 py-1 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700 transition-colors"
                        >
                          <Eye size={16} />
                          View Details
                        </button>
                      </div>
                    </TableCell>
                    <TableCell>
                      <ul className="list-disc list-inside text-emerald-600 space-y-1">
                        {scenario.pros?.map((pro, proIndex) => (
                          <li key={proIndex}>
                            <span className="text-slate-700">{pro}</span>
                          </li>
                        ))}
                      </ul>
                    </TableCell>
                    <TableCell>
                      <ul className="list-disc list-inside text-rose-600 space-y-1">
                        {scenario.cons?.map((con, conIndex) => (
                          <li key={conIndex}>
                            <span className="text-slate-700">{con}</span>
                          </li>
                        ))}
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

      {/* Bank Statements Modal */}
      <BankStatementsModal 
        isOpen={isBankStatementsModalOpen}
        onClose={() => setIsBankStatementsModalOpen(false)}
        scrollTarget={scrollTarget}
      />

      {/* Scenario Details Modal */}
      <Modal 
        isOpen={isScenarioModalOpen} 
        onClose={() => setIsScenarioModalOpen(false)}
        title={selectedScenario?.scenarioName}
        size="lg"
      >
        {renderScenarioDetails(selectedScenario)}
      </Modal>
    </div>
  );
};

export default RecommendationPage;
