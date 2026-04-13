# 종목 기본정보 스크래핑
import yfinance as yf
import pandas as pd

class Stock:

    KEYS_BASIC = ['longName','industry','sector','marketCap','sharesOutstanding']
    KEYS_INCOME = ['Total Revenue','Gross Profit','Operating Income','Net Income']
    KEYS_BALANCE = ['Total Assets','Total Liabilities Net Minority Interest','Stockholders Equity']
    KEYS_CASHFLOW = ['Operating Cash Flow','Investing Cash Flow','Financing Cash Flow']

    
    def __init__(self, symbol: str):
        self.ticker = symbol
        self.company = yf.Ticker(symbol)
    
    def get_basic_info(self) -> dict:
        basic_info = {key: self.company.info[key] for key in Stock.KEYS_BASIC if key in self.company.info}
        return basic_info

        # df = pd.DataFrame.from_dict(self.company.info, orient='index', columns=['Value'])
        # df = df.loc[['longName','industry','sector','marketCap','sharesOutstanding']]
        # df = df.rename_axis('항목')
        # return df.to_markdown()

    def get_financial_statement(self) -> dict:
        inc = self.company.quarterly_income_stmt.loc[
            ['Total Revenue','Gross Profit','Operating Income','Net Income']
        ].rename_axis('항목').rename(columns=lambda x: x.strftime("%Y-%m-%d"))
        bal = self.company.quarterly_balance_sheet.loc[
            ['Total Assets','Total Liabilities Net Minority Interest','Stockholders Equity']
        ].rename_axis('항목').rename(columns=lambda x: x.strftime("%Y-%m-%d"))
        cfs = self.company.quarterly_cash_flow.loc[
            ['Operating Cash Flow','Investing Cash Flow','Financing Cash Flow']
        ].rename_axis('항목').rename(columns=lambda x: x.strftime("%Y-%m-%d"))

        return {
            "incomeStatement" : inc.iloc[:, :5].reset_index().to_dict('records'), 
            "balanceSheet" : bal.iloc[:, :5].reset_index().to_dict('records'), 
            "cashFlow" : cfs.iloc[:, :5].reset_index().to_dict('records'), 
        }

        # return (
        #     "### Quarterly Income Statement\n" + inc.to_markdown() + "\n\n" +
        #     "### Quarterly Balance Sheet\n"  + bal.to_markdown() + "\n\n" +
        #     "### Quarterly Cash Flow\n"      + cfs.to_markdown()
        # )
    
    def get_company_data(self) -> dict: 

        # 정보가 제대로 가져오지 못한 경우
        if len(self.company.info) < 2 : return None

        company_data = { 
            "ticker" : self.ticker,
            "name" : self.company.info['longName'],           
            "basicInfo": self.get_basic_info(),
            "financialData": self.get_financial_statement(),
        }

        return company_data
    
