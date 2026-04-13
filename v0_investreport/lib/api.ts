/**
 * FastAPI 백엔드와 통신하는 API 서비스 레이어
 * 백엔드 URL을 환경변수로 설정 가능 (기본값: http://localhost:8000)
 */

import type { CompanyData, InvestmentReport } from "./types"

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
  const url = `${API_BASE_URL}/api/search?query=${encodeURIComponent(query)}`
  console.log("[v0] searchCompanies - API URL:", url)
  console.log("[v0] searchCompanies - query:", query)
  
  const response = await fetch(url)
  console.log("[v0] searchCompanies - response status:", response.status)
  
  if (!response.ok) {
    throw new Error(`Failed to search companies: ${response.statusText}`)
  }
  const data = await response.json()
  console.log("[v0] searchCompanies - results:", data)
  return data
}

/**
 * 특정 회사의 전체 데이터 조회 (기본정보 + 재무데이터)
 * main.py에서 [{...}] 형식으로 반환하므로 첫 번째 요소 추출
 */
export async function fetchCompanyData(ticker: string): Promise<CompanyData> {
  const url = `${API_BASE_URL}/api/companies/${ticker}`
  console.log("[v0] fetchCompanyData - API URL:", url)
  
  const response = await fetch(url)
  console.log("[v0] fetchCompanyData - response status:", response.status)
  
  if (!response.ok) {
    throw new Error(`Failed to fetch company data: ${response.statusText}`)
  }
  
  const data = await response.json()
  console.log("[v0] fetchCompanyData - raw data:", data)
  
  // main.py에서 [{...}] 배열 형식으로 반환하므로 첫 번째 요소 추출
  const companyData = Array.isArray(data) ? data[0] : data
  console.log("[v0] fetchCompanyData - companyData:", companyData)
  
  return companyData
}

// 기본정보와 재무데이터는 fetchCompanyData()에서 한 번에 조회하므로
// fetchCompanyBasicInfo, fetchFinancialData 개별 함수는 제거됨

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
