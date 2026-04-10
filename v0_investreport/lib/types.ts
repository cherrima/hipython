// 기본정보 타입 정의
export interface CompanyBasicInfo {
  longName: string
  industry: string
  sector: string
  marketCap: number | string
  sharesOutstanding: number | string
}

// DataFrame 형태의 재무제표 데이터 타입
export interface FinancialDataRow {
  항목: string
  [period: string]: string | number
}

export interface FinancialData {
  incomeStatement: FinancialDataRow[]
  balanceSheet: FinancialDataRow[]
  cashFlow: FinancialDataRow[]
}

// 회사 데이터 전체 타입
export interface CompanyData {
  ticker: string
  name: string
  basicInfo: CompanyBasicInfo
  financialData: FinancialData
}

// 투자 보고서 타입
export interface InvestmentReport {
  ticker: string
  companyName: string
  markdownContent: string
}
