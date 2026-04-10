/**
 * FastAPI 백엔드와 통신하는 API 서비스 레이어
 * 백엔드 URL을 환경변수로 설정 가능 (기본값: http://localhost:8000)
 */

import type { CompanyData, InvestmentReport, CompanyBasicInfo, FinancialData } from "./types"

// API 기본 URL (환경변수 또는 기본값)
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

// 회사 목록 타입
export interface CompanyListItem {
  ticker: string
  name: string
}

// API 응답 타입 (전체 보고서)
export interface FullReportResponse {
  ticker: string
  companyName: string
  markdownContent: string
}

/**
 * 모든 회사 목록 조회
 */
export async function fetchCompanies(): Promise<CompanyListItem[]> {
  const response = await fetch(`${API_BASE_URL}/api/companies`)
  if (!response.ok) {
    throw new Error(`Failed to fetch companies: ${response.statusText}`)
  }
  return response.json()
}

/**
 * 회사 검색
 */
export async function searchCompanies(query: string): Promise<CompanyListItem[]> {
  const response = await fetch(`${API_BASE_URL}/api/search?q=${encodeURIComponent(query)}`)
  if (!response.ok) {
    throw new Error(`Failed to search companies: ${response.statusText}`)
  }
  return response.json()
}

/**
 * 특정 회사의 전체 데이터 조회 (기본정보 + 재무데이터)
 */
export async function fetchCompanyData(ticker: string): Promise<CompanyData> {
  const response = await fetch(`${API_BASE_URL}/api/companies/${ticker}`)
  if (!response.ok) {
    throw new Error(`Failed to fetch company data: ${response.statusText}`)
  }
  return response.json()
}

/**
 * 특정 회사의 기본정보만 조회 (dict/json 형식)
 */
export async function fetchCompanyBasicInfo(ticker: string): Promise<CompanyBasicInfo> {
  const response = await fetch(`${API_BASE_URL}/api/companies/${ticker}/basic-info`)
  if (!response.ok) {
    throw new Error(`Failed to fetch basic info: ${response.statusText}`)
  }
  return response.json()
}

/**
 * 특정 회사의 재무 데이터 조회 (DataFrame 유사 형식)
 */
export async function fetchFinancialData(ticker: string): Promise<FinancialData> {
  const response = await fetch(`${API_BASE_URL}/api/companies/${ticker}/financial-data`)
  if (!response.ok) {
    throw new Error(`Failed to fetch financial data: ${response.statusText}`)
  }
  return response.json()
}

/**
 * 특정 회사의 투자보고서 조회 (Markdown 형식)
 */
export async function fetchInvestmentReport(ticker: string): Promise<InvestmentReport> {
  const response = await fetch(`${API_BASE_URL}/api/reports/${ticker}`)
  if (!response.ok) {
    throw new Error(`Failed to fetch investment report: ${response.statusText}`)
  }
  return response.json()
}

/**
 * 특정 회사의 투자보고서(전체) 조회 - 제목 제외 Markdown 형식
 */
export async function fetchFullInvestmentReport(ticker: string): Promise<FullReportResponse> {
  const response = await fetch(`${API_BASE_URL}/api/reports/${ticker}/full`)
  if (!response.ok) {
    throw new Error(`Failed to fetch full investment report: ${response.statusText}`)
  }
  return response.json()
}

/**
 * API 연결 상태 확인
 */
export async function checkApiHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/health`)
    return response.ok
  } catch {
    return false
  }
}
