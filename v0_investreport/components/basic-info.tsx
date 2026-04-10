"use client"

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import type { CompanyBasicInfo, FinancialDataRow } from "@/lib/types"

interface BasicInfoProps {
  ticker: string
  companyName: string
  basicInfo: CompanyBasicInfo
  incomeStatement: FinancialDataRow[]
  balanceSheet: FinancialDataRow[]
  cashFlow: FinancialDataRow[]
}

// 기본 정보 테이블 (dict/json 형식 데이터)
function BasicInfoTable({
  basicInfo,
}: {
  basicInfo: CompanyBasicInfo
}) {
  const rows = [
    { key: "longName", label: "longName", value: basicInfo.longName },
    { key: "industry", label: "industry", value: basicInfo.industry },
    { key: "sector", label: "sector", value: basicInfo.sector },
    { key: "marketCap", label: "marketCap", value: basicInfo.marketCap },
    { key: "sharesOutstanding", label: "sharesOutstanding", value: basicInfo.sharesOutstanding },
  ]

  return (
    <Table>
      <TableHeader>
        <TableRow className="bg-muted/50">
          <TableHead className="font-semibold">항목</TableHead>
          <TableHead className="font-semibold">Value</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {rows.map((row) => (
          <TableRow key={row.key}>
            <TableCell className="font-medium">{row.label}</TableCell>
            <TableCell>{String(row.value)}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  )
}

// DataFrame 형식 테이블 (분기별 재무제표)
function FinancialTable({
  title,
  data,
}: {
  title: string
  data: FinancialDataRow[]
}) {
  if (!data || data.length === 0) return null

  // 첫 번째 행에서 기간 컬럼 추출 (항목 제외)
  const periods = Object.keys(data[0]).filter((key) => key !== "항목")

  return (
    <div className="space-y-2">
      <h3 className="text-base font-semibold text-foreground">{title}</h3>
      <Table>
        <TableHeader>
          <TableRow className="bg-muted/50">
            <TableHead className="font-semibold">항목</TableHead>
            {periods.map((period) => (
              <TableHead key={period} className="font-semibold text-center">
                {period}
              </TableHead>
            ))}
          </TableRow>
        </TableHeader>
        <TableBody>
          {data.map((row, idx) => (
            <TableRow key={idx}>
              <TableCell className="font-medium">{row.항목}</TableCell>
              {periods.map((period) => (
                <TableCell key={period} className="text-right">
                  {String(row[period])}
                </TableCell>
              ))}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  )
}

export default function BasicInfo({
  ticker,
  companyName,
  basicInfo,
  incomeStatement,
  balanceSheet,
  cashFlow,
}: BasicInfoProps) {
  return (
    <div className="space-y-8 p-6">
      {/* 페이지 제목 */}
      <h2 className="text-xl font-bold text-foreground">
        {ticker}: {companyName} 기본정보
      </h2>

      {/* 기본 정보 테이블 */}
      <BasicInfoTable basicInfo={basicInfo} />

      {/* 분기별 손익계산서 */}
      <FinancialTable title="Quarterly Income Statement" data={incomeStatement} />

      {/* 분기별 재무상태표 */}
      <FinancialTable title="Quarterly Balance Sheet" data={balanceSheet} />

      {/* 분기별 현금흐름표 */}
      <FinancialTable title="Quarterly Cash Flow" data={cashFlow} />
    </div>
  )
}
