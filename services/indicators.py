
def calculate_sma(data, period=20):
    """
    Calculate Simple Moving Average.
    """
    return data["Close"].rolling(window=period).mean()


def calculate_rsi(data, period=14):
    """
    Calculate Relative Strength Index.
    """
    delta = data["Close"].diff()

    gain = delta.clip(lower=0).rolling(window=period).mean()

    loss = -delta.clip(upper=0).rolling(window=period).mean()

    rs = gain / loss

    rsi = 100 - (100 / (1 + rs))

    return rsi


def calculate_indicators(data):
    """
    Calculate technical indicators for stock data.
    """
    data = data.copy()

    data["SMA20"] = calculate_sma(data, 20)

    data["RSI"] = calculate_rsi(data, 14)

    return data
