import React, { useState, useEffect, useRef } from 'react';
import Modal from './ui/modal';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';
import { User, CreditCard, Wallet, TrendingUp, AlertCircle, FileText, Banknote, LineChart } from 'lucide-react';
import { API_URL } from '../config';

const BankStatementsModal = ({ isOpen, onClose, scrollTarget }) => {
  const [userData, setUserData] = useState(null);
  const [financialAnalyses, setFinancialAnalyses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Refs for scrolling to specific sections
  const creditReportRef = useRef(null);
  const mutualFundsRef = useRef(null);
  const equityPortfolioRef = useRef(null);
  const balanceHistoryRef = useRef(null);

  useEffect(() => {
    if (isOpen) {
      fetchUserData();
    }
  }, [isOpen]);

  // Handle scrolling to target section
  useEffect(() => {
    if (isOpen && !loading && scrollTarget) {
      // Small delay to ensure modal content is rendered
      setTimeout(() => {
        let targetRef = null;
        
        switch (scrollTarget) {
          case 'credit-report':
            targetRef = creditReportRef;
            break;
          case 'mutual-funds':
            targetRef = mutualFundsRef;
            break;
          case 'equity-portfolio':
            targetRef = equityPortfolioRef;
            break;
          case 'balance-history':
            targetRef = balanceHistoryRef;
            break;
          default:
            return;
        }
        
        if (targetRef.current) {
          targetRef.current.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'start' 
          });
        }
      }, 300);
    }
  }, [isOpen, loading, scrollTarget]);

  const fetchUserData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Fetch user profile with financials
      const userResponse = await fetch(`${API_URL}/users/1`);
      if (!userResponse.ok) throw new Error('Failed to fetch user data');
      const userData = await userResponse.json();
      
      // Fetch financial analyses
      const analysesResponse = await fetch(`${API_URL}/users/1/financial-analyses`);
      if (!analysesResponse.ok) throw new Error('Failed to fetch financial analyses');
      const analysesData = await analysesResponse.json();
      
      setUserData(userData);
      setFinancialAnalyses(analysesData);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const formatDateTime = (dateString) => {
    return new Date(dateString).toLocaleString('en-IN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const sortByTimestamp = (data) => {
    if (!data || !Array.isArray(data)) return [];
    return [...data].sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
  };

  const renderPersonalDetails = () => {
    if (!userData) return null;

    return (
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <User size={20} />
            Personal Details
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-600">Full Name</p>
              <p className="font-medium">{userData.full_name || 'N/A'}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Email</p>
              <p className="font-medium">{userData.email}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Phone</p>
              <p className="font-medium">{userData.phone_number || 'N/A'}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">PAN ID</p>
              <p className="font-medium">{userData.pan_id || 'N/A'}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Date of Birth</p>
              <p className="font-medium">{userData.date_of_birth || 'N/A'}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Gender</p>
              <p className="font-medium">{userData.gender || 'N/A'}</p>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  };

  const renderFinancialAnalysis = () => {
    if (!financialAnalyses || financialAnalyses.length === 0) return null;

    const latestAnalysis = financialAnalyses[0]; // Get the most recent analysis

    return (
      <div className="space-y-6">
        {/* Personal Profile from Analysis */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp size={20} />
              Financial Profile
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-600">Name</p>
                <p className="font-medium">{latestAnalysis.personalProfile?.name || 'N/A'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Age</p>
                <p className="font-medium">{latestAnalysis.personalProfile?.age || 'N/A'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Occupation</p>
                <p className="font-medium">{latestAnalysis.personalProfile?.occupation || 'N/A'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Dependents</p>
                <p className="font-medium">{latestAnalysis.personalProfile?.dependents || 'N/A'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Employment Stability</p>
                <p className="font-medium">{latestAnalysis.personalProfile?.employmentStability || 'N/A'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Risk Tolerance</p>
                <p className="font-medium">{latestAnalysis.personalProfile?.riskTolerance || 'N/A'}</p>
              </div>
            </div>
            
            {latestAnalysis.personalProfile?.totalIncomeMonthly && (
              <div className="mt-4">
                <p className="text-sm text-gray-600 mb-2">Monthly Income Breakdown</p>
                <div className="bg-gray-50 p-3 rounded-lg">
                  {Object.entries(latestAnalysis.personalProfile.totalIncomeMonthly).map(([source, amount]) => (
                    <div key={source} className="flex justify-between items-center py-1">
                      <span className="capitalize">{source.replace(/([A-Z])/g, ' $1').trim()}</span>
                      <span className="font-medium">{formatCurrency(amount)}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Credit Score Analysis */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CreditCard size={20} />
              Credit Score Analysis
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-600">Credit Score</p>
                <p className="font-bold text-2xl text-green-600">{latestAnalysis.creditScoreAnalysis?.scoreValue || 'N/A'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Score Interpretation</p>
                <p className="font-medium">{latestAnalysis.creditScoreAnalysis?.scoreInterpretation || 'N/A'}</p>
              </div>
            </div>
            
            {latestAnalysis.creditScoreAnalysis?.scoringElements && (
              <div className="mt-4">
                <p className="text-sm text-gray-600 mb-2">Credit Factors</p>
                <div className="space-y-2">
                  {latestAnalysis.creditScoreAnalysis.scoringElements.map((element, index) => (
                    <div key={index} className="bg-gray-50 p-3 rounded-lg">
                      <p className="font-medium">{element.description}</p>
                      <p className="text-sm text-gray-600">{element.note}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Account Summary & Bank Statement Data */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Wallet size={20} />
              Account Summary & Bank Statements
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-medium mb-3">Liabilities</h4>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Active Accounts</span>
                    <span className="font-medium">{latestAnalysis.accountSummaryAnalysis?.existingLiabilities?.noOfActiveAccounts || 'N/A'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Total Outstanding</span>
                    <span className="font-medium">{formatCurrency(latestAnalysis.accountSummaryAnalysis?.existingLiabilities?.totalOutstanding || 0)}</span>
                  </div>
                </div>
              </div>
              
              <div>
                <h4 className="font-medium mb-3">Liquidity</h4>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Bank Balances</span>
                    <span className="font-medium">{latestAnalysis.accountSummaryAnalysis?.liquidity?.bankBalances || 'N/A'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Investment Portfolio</span>
                    <span className="font-medium">{formatCurrency(latestAnalysis.accountSummaryAnalysis?.liquidity?.investmentPortfolio || 0)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Usable Liquidity</span>
                    <span className="font-medium">{formatCurrency(latestAnalysis.accountSummaryAnalysis?.liquidity?.usableLiquidityAfterBuffer || 0)}</span>
                  </div>
                </div>
              </div>
            </div>
            
            {latestAnalysis.accountSummaryAnalysis?.notes && (
              <div className="mt-4">
                <p className="text-sm text-gray-600 mb-2">Notes</p>
                <ul className="list-disc list-inside space-y-1">
                  {latestAnalysis.accountSummaryAnalysis.notes.map((note, index) => (
                    <li key={index} className="text-sm">{note}</li>
                  ))}
                </ul>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Risk Flags */}
        {latestAnalysis.riskFlags && latestAnalysis.riskFlags.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertCircle size={20} className="text-red-500" />
                Risk Flags
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2">
                {latestAnalysis.riskFlags.map((flag, index) => (
                  <li key={index} className="flex items-start gap-2">
                    <AlertCircle size={16} className="text-red-500 mt-0.5 flex-shrink-0" />
                    <span className="text-sm">{flag}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        )}
      </div>
    );
  };

  const renderCreditReportData = () => {
    if (!userData?.financials) return null;

    const financials = userData.financials;
    
    return (
      <Card className="mb-6" ref={creditReportRef}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText size={20} />
            Credit Report Summary
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {financials.credit_score_name && (
              <div>
                <p className="text-sm text-gray-600">Credit Score Provider</p>
                <p className="font-medium">{financials.credit_score_name}</p>
              </div>
            )}
            {financials.credit_score && (
              <div>
                <p className="text-sm text-gray-600">Credit Score</p>
                <p className="font-bold text-2xl text-green-600">{financials.credit_score}</p>
              </div>
            )}
            {financials.total_income && (
              <div>
                <p className="text-sm text-gray-600">Total Income</p>
                <p className="font-medium">{formatCurrency(financials.total_income)}</p>
              </div>
            )}
            {financials.active_loans_count !== null && (
              <div>
                <p className="text-sm text-gray-600">Active Loans</p>
                <p className="font-medium">{financials.active_loans_count}</p>
              </div>
            )}
            {financials.loans_balance && (
              <div>
                <p className="text-sm text-gray-600">Current Loan Balance</p>
                <p className="font-medium">{formatCurrency(financials.loans_balance)}</p>
              </div>
            )}
            {financials.loans_sanctioned_amount && (
              <div>
                <p className="text-sm text-gray-600">Total Sanctioned Amount</p>
                <p className="font-medium">{formatCurrency(financials.loans_sanctioned_amount)}</p>
              </div>
            )}
            {financials.loans_past_due_amount && (
              <div>
                <p className="text-sm text-gray-600">Past Due Amount</p>
                <p className="font-medium text-red-600">{formatCurrency(financials.loans_past_due_amount)}</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    );
  };

  const renderInvestmentSummary = () => {
    if (!userData?.financials) return null;

    const { mutual_funds_summary, equities_summary, etf_summary } = userData.financials;
    
    const hasInvestments = (mutual_funds_summary && mutual_funds_summary.length > 0) ||
                          (equities_summary && equities_summary.length > 0) ||
                          (etf_summary && etf_summary.length > 0);

    if (!hasInvestments) return null;

    return (
      <div className="space-y-6">
        {/* Mutual Funds */}
        {mutual_funds_summary && mutual_funds_summary.length > 0 && (
          <Card ref={mutualFundsRef}>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Banknote size={20} />
                Mutual Funds Portfolio
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Fund Name</TableHead>
                      <TableHead>AMC</TableHead>
                      <TableHead>Category</TableHead>
                      <TableHead className="text-right">Units</TableHead>
                      <TableHead className="text-right">NAV</TableHead>
                      <TableHead className="text-right">Current Value</TableHead>
                      <TableHead className="text-right">Cost Value</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {mutual_funds_summary.slice(0, 10).map((fund, index) => (
                      <TableRow key={index}>
                        <TableCell className="font-medium max-w-xs truncate" title={fund.description}>
                          {fund.description}
                        </TableCell>
                        <TableCell>{fund.amc}</TableCell>
                        <TableCell>
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                            {fund.scheme_category}
                          </span>
                        </TableCell>
                        <TableCell className="text-right">{fund.units.toFixed(3)}</TableCell>
                        <TableCell className="text-right">{formatCurrency(fund.nav)}</TableCell>
                        <TableCell className="text-right font-medium">
                          {formatCurrency(fund.current_value)}
                        </TableCell>
                        <TableCell className="text-right">
                          {formatCurrency(fund.cost_value)}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
              {mutual_funds_summary.length > 10 && (
                <p className="text-sm text-gray-500 mt-2">
                  Showing 10 of {mutual_funds_summary.length} funds
                </p>
              )}
            </CardContent>
          </Card>
        )}

        {/* Equities */}
        {equities_summary && equities_summary.length > 0 && (
          <Card ref={equityPortfolioRef}>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <LineChart size={20} />
                Equity Portfolio
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Company</TableHead>
                      <TableHead>ISIN</TableHead>
                      <TableHead className="text-right">Units</TableHead>
                      <TableHead className="text-right">Last Price</TableHead>
                      <TableHead className="text-right">Current Value</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {equities_summary.slice(0, 10).map((equity, index) => (
                      <TableRow key={index}>
                        <TableCell className="font-medium max-w-xs truncate" title={equity.description}>
                          {equity.issuer_name}
                        </TableCell>
                        <TableCell className="text-sm text-gray-600">{equity.isin}</TableCell>
                        <TableCell className="text-right">{equity.units}</TableCell>
                        <TableCell className="text-right">{formatCurrency(equity.last_traded_price)}</TableCell>
                        <TableCell className="text-right font-medium">
                          {formatCurrency(equity.current_value)}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
              {equities_summary.length > 10 && (
                <p className="text-sm text-gray-500 mt-2">
                  Showing 10 of {equities_summary.length} stocks
                </p>
              )}
            </CardContent>
          </Card>
        )}

        {/* ETFs */}
        {etf_summary && etf_summary.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp size={20} />
                ETF Portfolio
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>ETF Name</TableHead>
                      <TableHead>ISIN</TableHead>
                      <TableHead className="text-right">Units</TableHead>
                      <TableHead className="text-right">NAV</TableHead>
                      <TableHead className="text-right">Current Value</TableHead>
                      <TableHead>Last NAV Date</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {etf_summary.slice(0, 10).map((etf, index) => (
                      <TableRow key={index}>
                        <TableCell className="font-medium max-w-xs truncate" title={etf.description}>
                          {etf.description}
                        </TableCell>
                        <TableCell className="text-sm text-gray-600">{etf.isin}</TableCell>
                        <TableCell className="text-right">{etf.units.toFixed(3)}</TableCell>
                        <TableCell className="text-right">{formatCurrency(etf.nav)}</TableCell>
                        <TableCell className="text-right font-medium">
                          {formatCurrency(etf.current_value)}
                        </TableCell>
                        <TableCell>{formatDateTime(etf.last_nav_date)}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
              {etf_summary.length > 10 && (
                <p className="text-sm text-gray-500 mt-2">
                  Showing 10 of {etf_summary.length} ETFs
                </p>
              )}
            </CardContent>
          </Card>
        )}
      </div>
    );
  };

  const renderBankingHistory = () => {
    if (!userData?.financials) return null;

    const { bank_balance_history, inflow_history, outflow_history } = userData.financials;
    
    return (
      <div className="space-y-6">
        {/* Balance History */}
        {bank_balance_history && bank_balance_history.length > 0 && (
          <Card ref={balanceHistoryRef}>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Wallet size={20} />
                Balance History
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Date & Time</TableHead>
                      <TableHead className="text-right">Balance</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {sortByTimestamp(bank_balance_history).slice(0, 10).map((point, index) => (
                      <TableRow key={index}>
                        <TableCell>{formatDateTime(point.timestamp)}</TableCell>
                        <TableCell className="text-right font-medium">
                          {formatCurrency(point.balance)}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
              {bank_balance_history.length > 10 && (
                <p className="text-sm text-gray-500 mt-2">
                  Showing latest 10 of {bank_balance_history.length} records
                </p>
              )}
            </CardContent>
          </Card>
        )}

        {/* Inflow History */}
        {inflow_history && inflow_history.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp size={20} className="text-green-600" />
                Inflow History
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Date & Time</TableHead>
                      <TableHead className="text-right">Amount</TableHead>
                      <TableHead>Category</TableHead>
                      <TableHead>Description</TableHead>
                      <TableHead className="text-right">Balance After</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {sortByTimestamp(inflow_history).slice(0, 10).map((transaction, index) => (
                      <TableRow key={index}>
                        <TableCell>{formatDateTime(transaction.timestamp)}</TableCell>
                        <TableCell className="text-right font-medium text-green-600">
                          +{formatCurrency(transaction.amount)}
                        </TableCell>
                        <TableCell>
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                            {transaction.category}
                          </span>
                        </TableCell>
                        <TableCell className="max-w-xs truncate" title={transaction.narration}>
                          {transaction.narration}
                        </TableCell>
                        <TableCell className="text-right">
                          {formatCurrency(transaction.balance)}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
              {inflow_history.length > 10 && (
                <p className="text-sm text-gray-500 mt-2">
                  Showing latest 10 of {inflow_history.length} records
                </p>
              )}
            </CardContent>
          </Card>
        )}

        {/* Outflow History */}
        {outflow_history && outflow_history.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertCircle size={20} className="text-red-600" />
                Outflow History
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Date & Time</TableHead>
                      <TableHead className="text-right">Amount</TableHead>
                      <TableHead>Category</TableHead>
                      <TableHead>Description</TableHead>
                      <TableHead className="text-right">Balance After</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {sortByTimestamp(outflow_history).slice(0, 10).map((transaction, index) => (
                      <TableRow key={index}>
                        <TableCell>{formatDateTime(transaction.timestamp)}</TableCell>
                        <TableCell className="text-right font-medium text-red-600">
                          -{formatCurrency(transaction.amount)}
                        </TableCell>
                        <TableCell>
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                            {transaction.category}
                          </span>
                        </TableCell>
                        <TableCell className="max-w-xs truncate" title={transaction.narration}>
                          {transaction.narration}
                        </TableCell>
                        <TableCell className="text-right">
                          {formatCurrency(transaction.balance)}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
              {outflow_history.length > 10 && (
                <p className="text-sm text-gray-500 mt-2">
                  Showing latest 10 of {outflow_history.length} records
                </p>
              )}
            </CardContent>
          </Card>
        )}

        {/* Show message if no banking history data */}
        {(!bank_balance_history || bank_balance_history.length === 0) &&
         (!inflow_history || inflow_history.length === 0) &&
         (!outflow_history || outflow_history.length === 0) && (
          <Card>
            <CardContent className="text-center py-8">
              <Wallet size={48} className="mx-auto text-gray-400 mb-4" />
              <p className="text-gray-500">No banking history data available</p>
            </CardContent>
          </Card>
        )}
      </div>
    );
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Bank Statements & Financial Data" size="xl">
      {loading && (
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-2">Loading financial data...</span>
        </div>
      )}
      
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
          <div className="flex items-center gap-2">
            <AlertCircle size={20} className="text-red-500" />
            <span className="text-red-800">Error: {error}</span>
          </div>
        </div>
      )}
      
      {!loading && !error && (
        <div>
          {renderPersonalDetails()}
          {renderCreditReportData()}
          {renderFinancialAnalysis()}
          {renderInvestmentSummary()}
          {renderBankingHistory()}
        </div>
      )}
    </Modal>
  );
};

export default BankStatementsModal; 