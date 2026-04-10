"use client"

import ReactMarkdown from "react-markdown"

interface FullInvestmentReportProps {
  ticker: string
  companyName: string
  markdownContent: string
}

export default function FullInvestmentReport({ 
  ticker, 
  companyName, 
  markdownContent 
}: FullInvestmentReportProps) {
  return (
    <div className="p-6">
      <h2 className="text-xl font-bold text-foreground mb-2">투자보고서(전체)</h2>
      <p className="text-muted-foreground mb-6">{ticker}: {companyName}</p>
      
      <article className="prose prose-sm max-w-none dark:prose-invert prose-headings:text-foreground prose-p:text-foreground prose-li:text-foreground prose-strong:text-foreground">
        <ReactMarkdown
          components={{
            h1: ({ children }) => (
              <h1 className="text-2xl font-bold mb-4 text-foreground">{children}</h1>
            ),
            h2: ({ children }) => (
              <h2 className="text-xl font-bold mt-8 mb-4 text-foreground">{children}</h2>
            ),
            h3: ({ children }) => (
              <h3 className="text-lg font-semibold mt-6 mb-3 text-foreground">{children}</h3>
            ),
            p: ({ children }) => (
              <p className="mb-4 leading-relaxed text-foreground">{children}</p>
            ),
            ul: ({ children }) => (
              <ul className="list-disc pl-6 mb-4 space-y-2">{children}</ul>
            ),
            ol: ({ children }) => (
              <ol className="list-decimal pl-6 mb-4 space-y-2">{children}</ol>
            ),
            li: ({ children }) => (
              <li className="text-foreground">{children}</li>
            ),
            strong: ({ children }) => (
              <strong className="font-bold text-foreground">{children}</strong>
            ),
            hr: () => (
              <hr className="my-6 border-border" />
            ),
          }}
        >
          {markdownContent}
        </ReactMarkdown>
      </article>
    </div>
  )
}
