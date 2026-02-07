"""
================================================================================
PYTHON FINANCIAL DATA ANALYSIS TUTORIAL (2024-2026 Best Practices)
================================================================================

A comprehensive guide for quantitative traders returning to Python after a hiatus.
Covers data fetching, Pandas, NumPy, and time series analysis.

Author: Tutorial for Quantitative Traders
Last Updated: February 2026
================================================================================
"""

# =============================================================================
# SECTION 1: MODERN PYTHON ENVIRONMENT SETUP
# =============================================================================
"""
RECOMMENDED PACKAGE VERSIONS (as of 2026):
------------------------------------------
pip install pandas>=2.0 numpy>=1.24 yfinance>=0.2 matplotlib>=3.7 scipy>=1.11

Key changes since ~2020:
- Pandas 2.0+ uses PyArrow backend for better performance (optional)
- NumPy has deprecated many aliases (np.int -> np.int64, etc.)
- yfinance replaced pandas-datareader as the go-to for free stock data
- Type hints are now standard practice in production code
"""

import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from typing import Optional
import warnings

# Suppress yfinance warnings for cleaner output
warnings.filterwarnings('ignore', category=FutureWarning)

# Modern Pandas settings for better display
pd.set_option('display.max_columns', 15)
pd.set_option('display.width', 120)
pd.set_option('display.precision', 4)


# =============================================================================
# SECTION 2: FETCHING PUBLIC STOCK DATA
# =============================================================================
"""
yfinance is the standard free data source. It wraps Yahoo Finance API.
For production trading, consider paid APIs: Polygon.io, Alpha Vantage, IEX Cloud
"""

def fetch_stock_data(
    tickers: list[str],
    start_date: str,
    end_date: Optional[str] = None,
    interval: str = "1d"
) -> pd.DataFrame:
    """
    Fetch historical stock data using yfinance.

    Parameters
    ----------
    tickers : list[str]
        List of stock symbols (e.g., ['AAPL', 'MSFT', 'GOOGL'])
    start_date : str
        Start date in 'YYYY-MM-DD' format
    end_date : str, optional
        End date (defaults to today)
    interval : str
        Data frequency: '1d', '1wk', '1mo', '1h', '5m', etc.
        Note: Intraday data limited to last 60 days

    Returns
    -------
    pd.DataFrame
        OHLCV data with DatetimeIndex

    Example
    -------
    >>> df = fetch_stock_data(['AAPL', 'MSFT'], '2023-01-01', '2024-01-01')
    """
    if end_date is None:
        end_date = datetime.now().strftime('%Y-%m-%d')

    # Download data for multiple tickers
    data = yf.download(
        tickers=tickers,
        start=start_date,
        end=end_date,
        interval=interval,
        auto_adjust=True,  # Adjusts for splits/dividends automatically
        progress=False
    )

    return data


def fetch_single_stock_with_info(ticker: str) -> tuple[pd.DataFrame, dict]:
    """
    Fetch stock data along with company fundamentals.

    Returns both price history and company info (P/E, market cap, etc.)
    """
    stock = yf.Ticker(ticker)

    # Get 2 years of daily data
    hist = stock.history(period="2y")

    # Company fundamentals (useful for factor analysis)
    info = stock.info

    return hist, info


# =============================================================================
# SECTION 3: PANDAS ESSENTIALS FOR FINANCIAL DATA
# =============================================================================
"""
Key Pandas concepts for quant work:
- DatetimeIndex for time series alignment
- MultiIndex for multiple securities
- Vectorized operations (avoid loops!)
- Method chaining for readable code
"""

def pandas_financial_operations_demo(df: pd.DataFrame) -> pd.DataFrame:
    """
    Demonstrate essential Pandas operations for financial analysis.
    Assumes df has columns: Open, High, Low, Close, Volume
    """

    # --- BASIC COLUMN OPERATIONS ---

    # Calculate daily returns (percentage change)
    # This is the foundation of most financial analysis
    df['Returns'] = df['Close'].pct_change()

    # Log returns (preferred for statistical analysis - additive over time)
    df['Log_Returns'] = np.log(df['Close'] / df['Close'].shift(1))

    # --- ROLLING WINDOW CALCULATIONS ---

    # 20-day moving average (standard short-term trend indicator)
    df['SMA_20'] = df['Close'].rolling(window=20).mean()

    # 50-day moving average (medium-term trend)
    df['SMA_50'] = df['Close'].rolling(window=50).mean()

    # Exponential moving average (more weight on recent prices)
    df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()

    # Rolling volatility (annualized standard deviation of returns)
    df['Volatility_20d'] = df['Returns'].rolling(window=20).std() * np.sqrt(252)

    # --- PANDAS 2.0+ FEATURES ---

    # Rolling with min_periods (don't require full window for early data)
    df['SMA_20_early'] = df['Close'].rolling(window=20, min_periods=5).mean()

    # Named aggregation (cleaner than apply for multiple stats)
    rolling_stats = df['Returns'].rolling(window=20).agg(['mean', 'std', 'min', 'max'])

    return df


def handle_multiindex_data(tickers: list[str]) -> pd.DataFrame:
    """
    Working with multiple stocks creates MultiIndex DataFrames.
    This is critical for portfolio analysis.
    """
    # Fetch multiple stocks
    df = fetch_stock_data(tickers, '2023-01-01', '2024-12-31')

    # yfinance returns MultiIndex columns: (Price_Type, Ticker)
    # Example: df.columns = MultiIndex([('Close', 'AAPL'), ('Close', 'MSFT'), ...])

    # Extract just closing prices for all tickers
    close_prices = df['Close']  # Returns DataFrame with tickers as columns

    # Calculate returns for all stocks at once (vectorized!)
    returns = close_prices.pct_change()

    # Correlation matrix (essential for portfolio construction)
    correlation_matrix = returns.corr()

    # Stack to convert wide format to long format (useful for groupby operations)
    returns_long = returns.stack().reset_index()
    returns_long.columns = ['Date', 'Ticker', 'Return']

    return close_prices, returns, correlation_matrix


def method_chaining_example(df: pd.DataFrame) -> pd.DataFrame:
    """
    Modern Pandas style: method chaining for readable pipelines.

    This style replaced the old pattern of intermediate variables.
    """
    result = (
        df
        .assign(
            returns=lambda x: x['Close'].pct_change(),
            log_returns=lambda x: np.log(x['Close'] / x['Close'].shift(1)),
            volatility=lambda x: x['returns'].rolling(20).std() * np.sqrt(252)
        )
        .dropna()
        .loc[lambda x: x['volatility'] > 0.15]  # Filter high volatility days
        .sort_values('volatility', ascending=False)
    )
    return result


# =============================================================================
# SECTION 4: NUMPY FOR QUANTITATIVE ANALYSIS
# =============================================================================
"""
NumPy is the backbone of numerical computing in Python.
Key for: matrix operations, statistical calculations, performance optimization
"""

def numpy_financial_calculations(prices: np.ndarray) -> dict:
    """
    Essential NumPy operations for quantitative finance.

    Parameters
    ----------
    prices : np.ndarray
        1D array of closing prices

    Returns
    -------
    dict
        Dictionary of calculated metrics
    """
    # Simple returns
    simple_returns = np.diff(prices) / prices[:-1]

    # Log returns (more numerically stable)
    log_returns = np.diff(np.log(prices))

    # Annualized metrics (assuming daily data, 252 trading days/year)
    annualized_return = np.mean(log_returns) * 252
    annualized_volatility = np.std(log_returns, ddof=1) * np.sqrt(252)

    # Sharpe Ratio (assuming risk-free rate of 4%)
    risk_free_rate = 0.04
    sharpe_ratio = (annualized_return - risk_free_rate) / annualized_volatility

    # Maximum Drawdown calculation
    cumulative_returns = np.cumprod(1 + simple_returns)
    running_max = np.maximum.accumulate(cumulative_returns)
    drawdowns = (cumulative_returns - running_max) / running_max
    max_drawdown = np.min(drawdowns)

    # Sortino Ratio (downside deviation only)
    negative_returns = log_returns[log_returns < 0]
    downside_std = np.std(negative_returns, ddof=1) * np.sqrt(252)
    sortino_ratio = (annualized_return - risk_free_rate) / downside_std

    # Value at Risk (VaR) - Historical method, 95% confidence
    var_95 = np.percentile(simple_returns, 5)

    # Conditional VaR (Expected Shortfall)
    cvar_95 = np.mean(simple_returns[simple_returns <= var_95])

    return {
        'annualized_return': annualized_return,
        'annualized_volatility': annualized_volatility,
        'sharpe_ratio': sharpe_ratio,
        'sortino_ratio': sortino_ratio,
        'max_drawdown': max_drawdown,
        'var_95': var_95,
        'cvar_95': cvar_95
    }


def numpy_matrix_operations_for_portfolios(returns: pd.DataFrame) -> dict:
    """
    Matrix operations for portfolio optimization.

    Parameters
    ----------
    returns : pd.DataFrame
        DataFrame with returns for multiple assets (columns = assets)
    """
    # Convert to NumPy for matrix operations
    R = returns.values  # Shape: (n_observations, n_assets)

    # Mean returns vector
    mu = np.mean(R, axis=0) * 252  # Annualized

    # Covariance matrix
    cov_matrix = np.cov(R, rowvar=False) * 252  # Annualized

    # Correlation matrix
    corr_matrix = np.corrcoef(R, rowvar=False)

    # --- PORTFOLIO CALCULATIONS ---

    n_assets = len(mu)

    # Equal-weighted portfolio
    equal_weights = np.ones(n_assets) / n_assets

    # Portfolio return: w' * mu
    portfolio_return = np.dot(equal_weights, mu)

    # Portfolio variance: w' * Sigma * w
    portfolio_variance = np.dot(equal_weights, np.dot(cov_matrix, equal_weights))
    portfolio_volatility = np.sqrt(portfolio_variance)

    # --- MINIMUM VARIANCE PORTFOLIO (Analytical Solution) ---

    # Inverse of covariance matrix
    cov_inv = np.linalg.inv(cov_matrix)

    # Ones vector
    ones = np.ones(n_assets)

    # Minimum variance weights: (Sigma^-1 * 1) / (1' * Sigma^-1 * 1)
    min_var_weights = np.dot(cov_inv, ones) / np.dot(ones, np.dot(cov_inv, ones))

    min_var_return = np.dot(min_var_weights, mu)
    min_var_volatility = np.sqrt(np.dot(min_var_weights, np.dot(cov_matrix, min_var_weights)))

    return {
        'mean_returns': mu,
        'covariance_matrix': cov_matrix,
        'correlation_matrix': corr_matrix,
        'equal_weight_return': portfolio_return,
        'equal_weight_volatility': portfolio_volatility,
        'min_var_weights': min_var_weights,
        'min_var_return': min_var_return,
        'min_var_volatility': min_var_volatility
    }


# =============================================================================
# SECTION 5: TIME SERIES ANALYSIS
# =============================================================================
"""
Time series analysis is central to quantitative trading.
Key techniques: stationarity testing, autocorrelation, trend decomposition
"""

from scipy import stats

def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Common technical indicators used in trading strategies.
    """
    df = df.copy()

    # --- TREND INDICATORS ---

    # MACD (Moving Average Convergence Divergence)
    ema_12 = df['Close'].ewm(span=12, adjust=False).mean()
    ema_26 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = ema_12 - ema_26
    df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']

    # --- MOMENTUM INDICATORS ---

    # RSI (Relative Strength Index)
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    # Rate of Change
    df['ROC_10'] = df['Close'].pct_change(periods=10) * 100

    # --- VOLATILITY INDICATORS ---

    # Bollinger Bands
    df['BB_Middle'] = df['Close'].rolling(window=20).mean()
    bb_std = df['Close'].rolling(window=20).std()
    df['BB_Upper'] = df['BB_Middle'] + (2 * bb_std)
    df['BB_Lower'] = df['BB_Middle'] - (2 * bb_std)
    df['BB_Width'] = (df['BB_Upper'] - df['BB_Lower']) / df['BB_Middle']

    # Average True Range (ATR)
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df['ATR'] = true_range.rolling(window=14).mean()

    # --- VOLUME INDICATORS ---

    # On-Balance Volume (OBV)
    df['OBV'] = (np.sign(df['Close'].diff()) * df['Volume']).fillna(0).cumsum()

    # Volume Moving Average
    df['Volume_SMA_20'] = df['Volume'].rolling(window=20).mean()

    return df


def analyze_return_distribution(returns: pd.Series) -> dict:
    """
    Statistical analysis of return distribution.

    Financial returns typically exhibit:
    - Fat tails (excess kurtosis)
    - Negative skewness
    - Volatility clustering
    """
    returns_clean = returns.dropna()

    # Basic statistics
    mean_return = returns_clean.mean()
    std_return = returns_clean.std()

    # Higher moments
    skewness = stats.skew(returns_clean)
    kurtosis = stats.kurtosis(returns_clean)  # Excess kurtosis (normal = 0)

    # Normality test (Jarque-Bera)
    jb_stat, jb_pvalue = stats.jarque_bera(returns_clean)

    # Percentiles for tail analysis
    percentiles = np.percentile(returns_clean, [1, 5, 25, 50, 75, 95, 99])

    return {
        'mean': mean_return,
        'std': std_return,
        'skewness': skewness,  # Negative = left tail heavier
        'excess_kurtosis': kurtosis,  # Positive = fat tails
        'jarque_bera_stat': jb_stat,
        'jarque_bera_pvalue': jb_pvalue,  # < 0.05 = reject normality
        'percentiles': dict(zip([1, 5, 25, 50, 75, 95, 99], percentiles))
    }


def calculate_rolling_beta(
    stock_returns: pd.Series,
    market_returns: pd.Series,
    window: int = 60
) -> pd.Series:
    """
    Calculate rolling beta of a stock relative to the market.

    Beta = Cov(stock, market) / Var(market)

    Parameters
    ----------
    stock_returns : pd.Series
        Daily returns of the stock
    market_returns : pd.Series
        Daily returns of the market index (e.g., SPY)
    window : int
        Rolling window size (default 60 days ≈ 3 months)
    """
    # Align the series
    aligned = pd.concat([stock_returns, market_returns], axis=1).dropna()
    aligned.columns = ['stock', 'market']

    # Rolling covariance and variance
    rolling_cov = aligned['stock'].rolling(window).cov(aligned['market'])
    rolling_var = aligned['market'].rolling(window).var()

    beta = rolling_cov / rolling_var

    return beta


def detect_regime_changes(returns: pd.Series, window: int = 20) -> pd.DataFrame:
    """
    Simple regime detection based on volatility regimes.

    Identifies high/low volatility periods, useful for:
    - Position sizing
    - Strategy switching
    - Risk management
    """
    df = pd.DataFrame({'returns': returns})

    # Rolling volatility
    df['volatility'] = returns.rolling(window).std() * np.sqrt(252)

    # Long-term volatility median for comparison
    vol_median = df['volatility'].expanding().median()

    # Regime classification
    df['regime'] = np.where(
        df['volatility'] > vol_median * 1.5,
        'high_vol',
        np.where(
            df['volatility'] < vol_median * 0.75,
            'low_vol',
            'normal'
        )
    )

    # Regime duration
    df['regime_change'] = df['regime'] != df['regime'].shift(1)
    df['regime_id'] = df['regime_change'].cumsum()

    return df


def calculate_autocorrelation(returns: pd.Series, max_lags: int = 20) -> pd.DataFrame:
    """
    Calculate autocorrelation of returns.

    Autocorrelation reveals:
    - Mean reversion (negative autocorrelation)
    - Momentum (positive autocorrelation)
    - Market efficiency (near-zero autocorrelation)
    """
    autocorr_values = []

    for lag in range(1, max_lags + 1):
        autocorr = returns.autocorr(lag=lag)
        autocorr_values.append({
            'lag': lag,
            'autocorrelation': autocorr,
            # Significance threshold (approximate 95% CI)
            'significant': abs(autocorr) > 1.96 / np.sqrt(len(returns))
        })

    return pd.DataFrame(autocorr_values)


# =============================================================================
# SECTION 6: PUTTING IT ALL TOGETHER - COMPLETE WORKFLOW
# =============================================================================

def complete_analysis_workflow():
    """
    Complete workflow demonstrating all concepts.
    Run this function to see all the analysis in action.
    """
    print("=" * 80)
    print("COMPLETE FINANCIAL ANALYSIS WORKFLOW")
    print("=" * 80)

    # --- STEP 1: FETCH DATA ---
    print("\n1. FETCHING STOCK DATA...")
    tickers = ['AAPL', 'MSFT', 'GOOGL', 'SPY']  # 3 stocks + market benchmark

    df = fetch_stock_data(tickers, '2022-01-01', '2024-12-31')
    print(f"   Downloaded {len(df)} trading days of data")
    print(f"   Columns: {df.columns.get_level_values(0).unique().tolist()}")

    # --- STEP 2: PREPARE DATA ---
    print("\n2. PREPARING DATA...")
    close_prices = df['Close']
    returns = close_prices.pct_change().dropna()

    print(f"   Shape: {returns.shape}")
    print(f"\n   First few rows of returns:")
    print(returns.head())

    # --- STEP 3: BASIC STATISTICS ---
    print("\n3. BASIC STATISTICS FOR AAPL...")
    aapl_stats = analyze_return_distribution(returns['AAPL'])

    print(f"   Mean Daily Return: {aapl_stats['mean']:.4%}")
    print(f"   Std Dev (Daily):   {aapl_stats['std']:.4%}")
    print(f"   Skewness:          {aapl_stats['skewness']:.3f}")
    print(f"   Excess Kurtosis:   {aapl_stats['excess_kurtosis']:.3f}")
    print(f"   Jarque-Bera p-val: {aapl_stats['jarque_bera_pvalue']:.4f}")
    print(f"   (p < 0.05 means returns are NOT normally distributed)")

    # --- STEP 4: RISK METRICS ---
    print("\n4. RISK METRICS FOR AAPL...")
    aapl_prices = close_prices['AAPL'].values
    risk_metrics = numpy_financial_calculations(aapl_prices)

    print(f"   Annualized Return:     {risk_metrics['annualized_return']:.2%}")
    print(f"   Annualized Volatility: {risk_metrics['annualized_volatility']:.2%}")
    print(f"   Sharpe Ratio:          {risk_metrics['sharpe_ratio']:.2f}")
    print(f"   Sortino Ratio:         {risk_metrics['sortino_ratio']:.2f}")
    print(f"   Maximum Drawdown:      {risk_metrics['max_drawdown']:.2%}")
    print(f"   VaR (95%):             {risk_metrics['var_95']:.2%}")
    print(f"   CVaR (95%):            {risk_metrics['cvar_95']:.2%}")

    # --- STEP 5: PORTFOLIO ANALYSIS ---
    print("\n5. PORTFOLIO ANALYSIS (AAPL, MSFT, GOOGL)...")
    stock_returns = returns[['AAPL', 'MSFT', 'GOOGL']]
    portfolio_stats = numpy_matrix_operations_for_portfolios(stock_returns)

    print(f"\n   Correlation Matrix:")
    corr_df = pd.DataFrame(
        portfolio_stats['correlation_matrix'],
        index=['AAPL', 'MSFT', 'GOOGL'],
        columns=['AAPL', 'MSFT', 'GOOGL']
    )
    print(corr_df.round(3))

    print(f"\n   Equal-Weight Portfolio:")
    print(f"   - Return:     {portfolio_stats['equal_weight_return']:.2%}")
    print(f"   - Volatility: {portfolio_stats['equal_weight_volatility']:.2%}")

    print(f"\n   Minimum Variance Portfolio:")
    print(f"   - Weights:    {dict(zip(['AAPL', 'MSFT', 'GOOGL'], portfolio_stats['min_var_weights'].round(3)))}")
    print(f"   - Return:     {portfolio_stats['min_var_return']:.2%}")
    print(f"   - Volatility: {portfolio_stats['min_var_volatility']:.2%}")

    # --- STEP 6: ROLLING BETA ---
    print("\n6. ROLLING BETA (AAPL vs SPY)...")
    beta = calculate_rolling_beta(returns['AAPL'], returns['SPY'], window=60)

    print(f"   Current 60-day Beta:  {beta.iloc[-1]:.2f}")
    print(f"   Average Beta:         {beta.mean():.2f}")
    print(f"   Min Beta:             {beta.min():.2f}")
    print(f"   Max Beta:             {beta.max():.2f}")

    # --- STEP 7: AUTOCORRELATION ---
    print("\n7. AUTOCORRELATION ANALYSIS (AAPL)...")
    autocorr = calculate_autocorrelation(returns['AAPL'], max_lags=10)
    significant = autocorr[autocorr['significant']]

    print(f"   Significant lags: {significant['lag'].tolist() if len(significant) > 0 else 'None'}")
    print(f"\n   First 5 lags:")
    print(autocorr.head().to_string(index=False))

    # --- STEP 8: TECHNICAL INDICATORS ---
    print("\n8. TECHNICAL INDICATORS (AAPL)...")

    # Get single stock data for technical indicators
    # NOTE: yfinance 0.2.28+ returns MultiIndex columns even for single tickers
    # We flatten them to avoid DataFrame vs Series issues in calculations
    aapl_df = yf.download('AAPL', start='2024-01-01', end='2024-12-31', progress=False)
    aapl_df.columns = aapl_df.columns.get_level_values(0)  # Flatten MultiIndex
    aapl_df = calculate_technical_indicators(aapl_df)

    print(f"   Latest values:")
    latest = aapl_df.iloc[-1]
    print(f"   - Close:        ${latest['Close']:.2f}")
    print(f"   - RSI:          {latest['RSI']:.1f} {'(Overbought)' if latest['RSI'] > 70 else '(Oversold)' if latest['RSI'] < 30 else ''}")
    print(f"   - MACD:         {latest['MACD']:.3f}")
    print(f"   - MACD Signal:  {latest['MACD_Signal']:.3f}")
    print(f"   - BB Position:  {'Above Upper' if latest['Close'] > latest['BB_Upper'] else 'Below Lower' if latest['Close'] < latest['BB_Lower'] else 'Within Bands'}")
    print(f"   - ATR:          ${latest['ATR']:.2f}")

    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)

    return {
        'returns': returns,
        'close_prices': close_prices,
        'risk_metrics': risk_metrics,
        'portfolio_stats': portfolio_stats
    }


# =============================================================================
# SECTION 7: BEST PRACTICES AND TIPS
# =============================================================================
"""
MODERN PYTHON BEST PRACTICES FOR QUANT WORK:
=============================================

1. TYPE HINTS (Python 3.10+)
   - Use: def func(x: float) -> pd.DataFrame
   - Use: list[str] instead of List[str] (no import needed)
   - Makes code self-documenting and catches bugs

2. VECTORIZATION
   - NEVER loop through DataFrame rows
   - Use .apply() only as last resort
   - Prefer: df['new'] = df['a'] * df['b']
   - Not:   for i in range(len(df)): df.loc[i, 'new'] = df.loc[i, 'a'] * df.loc[i, 'b']

3. MEMORY EFFICIENCY
   - Use df.astype() to downcast dtypes
   - Use chunked reading for large CSVs: pd.read_csv(..., chunksize=10000)
   - Consider PyArrow backend: pd.options.mode.dtype_backend = 'pyarrow'

4. REPRODUCIBILITY
   - Set random seeds: np.random.seed(42)
   - Pin package versions in requirements.txt
   - Use virtual environments (venv, conda)

5. PERFORMANCE
   - Profile with %timeit in Jupyter
   - Consider numba for hot loops: @numba.jit(nopython=True)
   - Use joblib for parallelization

6. DATA VALIDATION
   - Always check for NaN: df.isna().sum()
   - Check for duplicates: df.duplicated().sum()
   - Validate date ranges and data completeness

7. COMMON PANDAS 2.0+ GOTCHAS
   - .groupby() now keeps NA by default (use dropna=True if needed)
   - .resample() on empty DataFrames no longer raises
   - Some string methods return nullable StringDtype

8. YFINANCE 0.2.28+ GOTCHA (IMPORTANT!)
   - yf.download() now returns MultiIndex columns even for SINGLE tickers
   - Columns look like: ('Close', 'AAPL') instead of just 'Close'
   - This causes "Cannot set DataFrame to single column" errors
   - FIX: Flatten columns after download for single tickers:
         df.columns = df.columns.get_level_values(0)
   - OR use: yf.Ticker('AAPL').history() which returns flat columns

9. DEBUGGING TIPS
   - Use df.info() for quick overview
   - Use df.describe() for statistical summary
   - Check dtypes: df.dtypes
   - Use assert statements for data validation
"""


# =============================================================================
# RUN THE COMPLETE WORKFLOW
# =============================================================================

if __name__ == "__main__":
    # Run the complete analysis
    results = complete_analysis_workflow()

    # The results dictionary contains all calculated data for further use
    print("\n\nResults are stored in 'results' dictionary with keys:")
    print(list(results.keys()))
