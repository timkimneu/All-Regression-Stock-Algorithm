import requests
import pandas as pd

my_key = "02SPF8GNBRU864WA"

top10 = ['AAPL', 'MSFT', 'GOOG', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK-B', 'LLY', 'V']

# define urls for relevant financial info and monthly stock prices for specified company
symbol = 'TSLA'
income_url = f'https://www.alphavantage.co/query?function=INCOME_STATEMENT&symbol={symbol}&apikey={my_key}'
balance_url = f'https://www.alphavantage.co/query?function=BALANCE_SHEET&symbol={symbol}&apikey={my_key}'
cash_url = f'https://www.alphavantage.co/query?function=CASH_FLOW&symbol={symbol}&apikey={my_key}'
stock_month_url = f'https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY&symbol={symbol}&apikey={my_key}'

# retrieve responses
r_income = requests.get(income_url)
r_balance = requests.get(balance_url)
r_cash = requests.get(cash_url)
# r_stock_month = requests.get(stock_month_url)

if r_income.status_code == 200:

    # define lists to be used in dataframe
    l_current_ratio = list()
    l_quick_ratio = list()
    l_de_ratio = list()
    l_inv_turnover_ratio = list()
    l_avg_fixed = list()
    l_gross_profit_margin = list()
    l_income_quality_ratio = list()
    l_cap_acq_ratio = list()
    l_date = list()

    for i in range(4):
        # retrieve income statement details
        income_data = r_income.json()
        income_q_latest = income_data['quarterlyReports'][i]
        income_q_latest_date = income_q_latest['fiscalDateEnding']
        l_date.append(income_q_latest_date)

        # retrieve balance sheet details
        balance_data = r_balance.json()

        def get_balance_info(tick):
            balance_q = balance_data['quarterlyReports'][tick]
            balance_q_date = balance_q['fiscalDateEnding']

            if balance_q_date == income_q_latest_date:
                return tick
            else:
                tick += 1
                get_balance_info(tick)

        bal_date_adj = get_balance_info(tick=i)
        balance_q_latest = balance_data['quarterlyReports'][bal_date_adj]
        balance_q_prior = balance_data['quarterlyReports'][bal_date_adj + 1]

        # retrieve cash flow statement details
        cash_data = r_cash.json()

        def get_cash_info(tick):
            cash_q = cash_data['quarterlyReports'][tick]
            cash_q_date = cash_q['fiscalDateEnding']

            if cash_q_date == income_q_latest_date:
                return tick
            else:
                tick += 1
                get_cash_info(tick)

        cash_date_adj = get_cash_info(tick=i)
        cash_q_latest = cash_data['quarterlyReports'][cash_date_adj]
        cash_q_latest_date = cash_q_latest['fiscalDateEnding']

        # relevant income statement info
        gross_profit = int(income_q_latest['grossProfit'])
        revenue = int(income_q_latest['totalRevenue'])
        cogs = int(income_q_latest['costofGoodsAndServicesSold'])
        net_income = int(income_q_latest['netIncome'])

        # relevant balance sheet info
        # assets
        total_assets = int(balance_q_latest['totalAssets'])
        # current assets
        current_assets = int(balance_q_latest['totalCurrentAssets'])
        inventory = int(balance_q_latest['inventory'])
        inventory_prior = int(balance_q_prior['inventory'])
        # non-current assets
        ppe = int(balance_q_latest['propertyPlantEquipment'])
        ppe_prior = int(balance_q_prior['propertyPlantEquipment'])
        # liabilities
        total_liabilities = int(balance_q_latest['totalLiabilities'])
        # current liabilities
        current_liabilities = int(balance_q_latest['totalCurrentLiabilities'])
        # shareholders' equity
        total_se = int(balance_q_latest['totalShareholderEquity'])

        # relevant cash flow statement info
        operating_cash = int(cash_q_latest['operatingCashflow'])
        cash_paid_ppe = int(cash_q_latest['capitalExpenditures'])

        # Accounting Ratios
        # CURRENT RATIO
        # Current Assets / Current Liabilities --> Good Range: 1.2 - 2
        current_ratio = round((current_assets / current_liabilities), 3)
        l_current_ratio.append(current_ratio)

        # QUICK RATIO
        # (Current Assets - Inventory) / Current Liabilities --> Measure of liquidity
        quick_ratio = round(((current_assets - inventory) / current_liabilities), 3)
        l_quick_ratio.append(quick_ratio)

        # DEBT-TO-EQUITY RATIO
        # Total Liabilities / Total Shareholders' Equity --> Good: ~2.0
        de_ratio = round((total_liabilities / total_se), 3)
        l_de_ratio.append(de_ratio)

        # INVENTORY TURNOVER RATIO
        # Cost of Goods Sold (COGS) / Avg Inventory --> Good Range: 5 - 10
        avg_inv = (inventory + inventory_prior) / 2
        inv_turnover_ratio = round((cogs / avg_inv), 3)
        l_inv_turnover_ratio.append(inv_turnover_ratio)

        # FIXED ASSET TURNOVER RATIO
        # Revenue / Avg PPE
        avg_ppe = (ppe + ppe_prior) / 2
        avg_fixed = round((revenue / avg_ppe), 3)
        l_avg_fixed.append(avg_fixed)

        # GROSS PROFIT MARGIN
        # Gross Profit / Revenue
        gross_profit_margin = round((gross_profit / revenue), 3)
        l_gross_profit_margin.append(gross_profit_margin)

        # QUALITY OF INCOME RATIO
        # Cash from Operating Activities / Net Income
        income_quality_ratio = round((operating_cash / net_income), 3)
        l_income_quality_ratio.append(income_quality_ratio)

        # CAPITAL ACQUISITION RATIO
        # Cash from Operating Activities / Cash paid for Property, Plant, and Equipment (PPE)
        cap_acq_ratio = round((operating_cash / cash_paid_ppe), 3)
        l_cap_acq_ratio.append(cap_acq_ratio)

    # Compiled Dictionary of All Ratios
    fin_info = {'Current Ratio': l_current_ratio, 'Quick Ratio': l_quick_ratio, 'Debt-to-Equity': l_de_ratio,
                'Inventory Turnover': l_inv_turnover_ratio, 'Fixed Asset Turnover': l_avg_fixed,
                'Gross Profit Margin': l_gross_profit_margin, 'Quality of Income': l_income_quality_ratio,
                'Capital Acquisition Ratio': l_cap_acq_ratio, 'Date': l_date}

    fin_df = pd.DataFrame(fin_info)

    print(fin_df)

# Y = percent return over 1 month
# sklearn.train_test_split(80, 20)
# x_train, y_train, x_test, y_test = sklearn.train_test_split(data, test=20%)
# knn = sklearn.KNearestNeightbors(n_neightbors=5)
# knn.fit(X,y)
# y_predict = knn.predict(x_test)
