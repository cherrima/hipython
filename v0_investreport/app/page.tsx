"use client"

import { useState, useCallback } from "react"
import { FileText, Info, FileStack, AlertCircle, Loader2, Search } from "lucide-react"
import useSWR from "swr"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import BasicInfo from "@/components/basic-info"
import InvestmentReport from "@/components/investment-report"
import FullInvestmentReport from "@/components/full-investment-report"
import {
  fetchCompanyData,
  fetchInvestmentReport,
  fetchFullInvestmentReport,
  searchCompanies,
  type CompanyListItem,
} from "@/lib/api"
import type { CompanyData, InvestmentReport as InvestmentReportType } from "@/lib/types"
import type { FullReportResponse } from "@/lib/api"

// 폴백 데이터 (API 연결 실패 시 사용)
import {
  companies as fallbackCompanies,
  getCompanyData as getFallbackCompanyData,
  getInvestmentReport as getFallbackInvestmentReport,
} from "@/lib/sample-data"

type MenuType = "basic-info" | "investment-report" | "full-report"

// SWR fetcher 함수들
const companyDataFetcher = async (ticker: string): Promise<CompanyData> => {
  try {
    return await fetchCompanyData(ticker)
  } catch {
    const fallback = getFallbackCompanyData(ticker)
    if (fallback) return fallback
    throw new Error("Company not found")
  }
}

const reportFetcher = async (ticker: string): Promise<InvestmentReportType> => {
  try {
    return await fetchInvestmentReport(ticker)
  } catch {
    const fallback = getFallbackInvestmentReport(ticker)
    if (fallback) return fallback
    throw new Error("Report not found")
  }
}

const fullReportFetcher = async (ticker: string): Promise<FullReportResponse> => {
  try {
    return await fetchFullInvestmentReport(ticker)
  } catch {
    const fallback = getFallbackInvestmentReport(ticker)
    if (fallback) {
      return {
        ticker: fallback.ticker,
        companyName: fallback.companyName,
        markdownContent: fallback.markdownContent.replace(/^#.*\n\n/, '').replace(/## \d\) [^\n]+\n\n/g, '')
      }
    }
    throw new Error("Full report not found")
  }
}

const searchFetcher = async (query: string): Promise<CompanyListItem[]> => {
  if (!query.trim()) {
    return fallbackCompanies.map(c => ({ ticker: c.ticker, name: c.name }))
  }
  try {
    const results = await searchCompanies(query)
    return results.length > 0 ? results : fallbackCompanies
      .filter(c => 
        c.ticker.toLowerCase().includes(query.toLowerCase()) ||
        c.name.toLowerCase().includes(query.toLowerCase())
      )
      .map(c => ({ ticker: c.ticker, name: c.name }))
  } catch {
    return fallbackCompanies
      .filter(c => 
        c.ticker.toLowerCase().includes(query.toLowerCase()) ||
        c.name.toLowerCase().includes(query.toLowerCase())
      )
      .map(c => ({ ticker: c.ticker, name: c.name }))
  }
}

export default function Home() {
  const [selectedTicker, setSelectedTicker] = useState<string>("")
  const [activeMenu, setActiveMenu] = useState<MenuType>("basic-info")
  const [searchInput, setSearchInput] = useState<string>("")
  const [searchQuery, setSearchQuery] = useState<string>("")
  const [apiError, setApiError] = useState<boolean>(false)

  // SWR hooks
  const { data: searchResults = [], isLoading: isSearching } = useSWR(
    searchQuery ? `search-${searchQuery}` : null,
    () => searchFetcher(searchQuery),
    {
      onError: () => setApiError(true),
      revalidateOnFocus: false,
    }
  )

  const { data: companyData, isLoading: isLoadingCompanyData } = useSWR(
    selectedTicker ? `company-${selectedTicker}` : null,
    () => companyDataFetcher(selectedTicker),
    {
      onError: () => setApiError(true),
      revalidateOnFocus: false,
    }
  )

  const { data: reportData, isLoading: isLoadingReport } = useSWR(
    selectedTicker && activeMenu === "investment-report" ? `report-${selectedTicker}` : null,
    () => reportFetcher(selectedTicker),
    {
      onError: () => setApiError(true),
      revalidateOnFocus: false,
    }
  )

  const { data: fullReportData, isLoading: isLoadingFullReport } = useSWR(
    selectedTicker && activeMenu === "full-report" ? `full-report-${selectedTicker}` : null,
    () => fullReportFetcher(selectedTicker),
    {
      onError: () => setApiError(true),
      revalidateOnFocus: false,
    }
  )

  // 검색 실행 함수
  const handleSearch = useCallback(() => {
    if (searchInput.trim()) {
      setSearchQuery(searchInput.trim())
    }
  }, [searchInput])

  // Enter 키 입력 처리
  const handleKeyDown = useCallback((e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      handleSearch()
    }
  }, [handleSearch])

  // 회사 선택 변경 처리
  const handleCompanyChange = useCallback((ticker: string) => {
    setSelectedTicker(ticker)
  }, [])

  const menuItems = [
    { id: "basic-info" as MenuType, label: "기본정보", icon: Info },
    { id: "investment-report" as MenuType, label: "투자보고서", icon: FileText },
    { id: "full-report" as MenuType, label: "투자보고서(전체)", icon: FileStack },
  ]

  const isLoading = isLoadingCompanyData || 
    (activeMenu === "investment-report" && isLoadingReport) ||
    (activeMenu === "full-report" && isLoadingFullReport)

  return (
    <div className="min-h-screen bg-background">
      {/* TOP 영역 */}
      <header className="border-b border-border bg-card px-6 py-4">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-2xl font-bold text-foreground">
            LLM 투자 보고서 생성 서비스
          </h1>
          {apiError && (
            <div className="flex items-center gap-2 text-amber-600 text-sm">
              <AlertCircle className="size-4" />
              <span>API 연결 실패 - 샘플 데이터 사용 중</span>
            </div>
          )}
        </div>

        <div className="grid gap-4 max-w-md">
          {/* 회사명 입력 + 검색 버튼 */}
          <div>
            <label className="text-sm text-muted-foreground mb-1 block">
              회사명
            </label>
            <div className="flex gap-2">
              <Input
                placeholder="회사명 입력..."
                value={searchInput}
                onChange={(e) => setSearchInput(e.target.value)}
                onKeyDown={handleKeyDown}
                className="flex-1"
              />
              <Button 
                onClick={handleSearch}
                disabled={isSearching}
                className="shrink-0"
              >
                {isSearching ? (
                  <Loader2 className="size-4 animate-spin" />
                ) : (
                  <Search className="size-4" />
                )}
                <span className="ml-2">검색</span>
              </Button>
            </div>
          </div>

          {/* 검색 결과 목록 */}
          <div>
            <label className="text-sm text-muted-foreground mb-1 block">
              검색 결과 목록
            </label>
            <Select value={selectedTicker} onValueChange={handleCompanyChange}>
              <SelectTrigger className="w-full">
                <SelectValue placeholder="회사를 선택하세요" />
              </SelectTrigger>
              <SelectContent>
                {searchResults.length > 0 ? (
                  searchResults.map((company) => (
                    <SelectItem key={company.ticker} value={company.ticker}>
                      {company.ticker}: {company.name}
                    </SelectItem>
                  ))
                ) : (
                  <SelectItem value="_empty" disabled>
                    검색 결과가 없습니다
                  </SelectItem>
                )}
              </SelectContent>
            </Select>
          </div>
        </div>
      </header>

      {/* 메인 영역 (좌측 메뉴 + 우측 컨텐츠) */}
      <div className="flex">
        {/* 좌측 메뉴 */}
        <aside className="w-52 min-h-[calc(100vh-180px)] border-r border-border bg-card">
          <nav className="p-2">
            {menuItems.map((item) => {
              const Icon = item.icon
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveMenu(item.id)}
                  className={cn(
                    "w-full flex items-center gap-3 px-4 py-3 rounded-md text-left text-sm font-medium transition-colors",
                    activeMenu === item.id
                      ? "bg-primary text-primary-foreground"
                      : "text-muted-foreground hover:bg-muted hover:text-foreground"
                  )}
                >
                  <Icon className="size-4 shrink-0" />
                  {item.label}
                </button>
              )
            })}
          </nav>
        </aside>

        {/* 우측 컨텐츠 */}
        <main className="flex-1 overflow-auto">
          {!selectedTicker && (
            <div className="flex items-center justify-center h-64 text-muted-foreground">
              회사명을 입력하고 검색 버튼을 클릭한 후, 검색 결과에서 회사를 선택해주세요.
            </div>
          )}

          {selectedTicker && isLoading && (
            <div className="flex items-center justify-center h-64">
              <Loader2 className="size-8 animate-spin text-muted-foreground" />
            </div>
          )}

          {selectedTicker && !isLoading && activeMenu === "basic-info" && companyData && (
            <BasicInfo
              ticker={companyData.ticker}
              companyName={companyData.name}
              basicInfo={companyData.basicInfo}
              incomeStatement={companyData.financialData.incomeStatement}
              balanceSheet={companyData.financialData.balanceSheet}
              cashFlow={companyData.financialData.cashFlow}
            />
          )}

          {selectedTicker && !isLoading && activeMenu === "investment-report" && reportData && (
            <InvestmentReport report={reportData} />
          )}

          {selectedTicker && !isLoading && activeMenu === "full-report" && fullReportData && (
            <FullInvestmentReport 
              ticker={fullReportData.ticker}
              companyName={fullReportData.companyName}
              markdownContent={fullReportData.markdownContent}
            />
          )}
        </main>
      </div>
    </div>
  )
}
