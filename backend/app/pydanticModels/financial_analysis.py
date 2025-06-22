from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Union, Any


class PersonalProfile(BaseModel):
    name: str
    age: int
    occupation: str
    dependents: int
    totalIncomeMonthly: Dict[str, float]
    employmentStability: str
    emergencyBufferPreference: str
    riskTolerance: str


class CreditScoreAnalysisElement(BaseModel):
    description: str
    note: str


class CreditScoreAnalysis(BaseModel):
    scoreValue: int
    scoreInterpretation: str
    scoringElements: List[CreditScoreAnalysisElement]
    notes: List[str]


class AccountSummaryAnalysisLiabilities(BaseModel):
    noOfActiveAccounts: int
    totalOutstanding: int


class AccountSummaryAnalysisLiquidity(BaseModel):
    bankBalances: str
    investmentPortfolio: int
    usableLiquidityAfterBuffer: int


class AccountSummaryAnalysis(BaseModel):
    existingLiabilities: AccountSummaryAnalysisLiabilities
    liquidity: AccountSummaryAnalysisLiquidity
    notes: List[str]


class OtherKeyIndicators(BaseModel):
    ageOfOldestTrade: Optional[Any]
    numberOfOpenTrades: int
    recentInquiries: int
    notes: List[str]


class RecentActivityAnalysis(BaseModel):
    accountsOpenedLast6Months: int
    delinquentAccounts: int
    notes: List[str]


class DerivedMetrics(BaseModel):
    debtToIncomeRatioIfLoan: Optional[Any]
    utilizationRatio: int
    monthlySurplusAfterExistingObligations: int
    maxAffordableEMI: int


class ScenarioAssumptions(BaseModel):
    downPayment: int
    loanAmount: int
    interestRate: Optional[float]
    tenureYears: int


class ScenarioCalculations(BaseModel):
    estimatedEMI: int
    totalInterestPayable: int
    DTI: str
    remainingLiquidInvestments: int
    bufferAfterDownPayment: int


class Scenario(BaseModel):
    scenarioName: str
    assumptions: ScenarioAssumptions
    calculations: ScenarioCalculations
    pros: List[str]
    cons: List[str]
    riskAssessment: str


class Recommendation(BaseModel):
    recommendedScenario: str
    rationale: List[str]
    nextSteps: List[str]


class SensitivityAnalysisDetails(BaseModel):
    scenario: Optional[str] = None
    rateIncrease: Optional[str] = None
    newInterestRate: Optional[float] = None
    newEMI: Optional[str] = None
    impact: Optional[str] = None
    fromScenario: Optional[str] = None
    increaseDownPaymentBy: Optional[str] = None
    newDownPayment: Optional[int] = None
    newLoanAmount: Optional[int] = None


class SensitivityAnalysis(BaseModel):
    type: str
    details: SensitivityAnalysisDetails


class FinancialAnalysis(BaseModel):
    personalProfile: PersonalProfile
    creditScoreAnalysis: CreditScoreAnalysis
    accountSummaryAnalysis: AccountSummaryAnalysis
    otherKeyIndicators: OtherKeyIndicators
    recentActivityAnalysis: RecentActivityAnalysis
    derivedMetrics: DerivedMetrics
    riskFlags: List[str]
    scenarios: List[Scenario]
    recommendations: List[Recommendation]
    sensitivityAnalyses: List[SensitivityAnalysis]
    notes: List[str]
    humanSummary: str


class FinancialAnalysisCreate(FinancialAnalysis):
    pass 