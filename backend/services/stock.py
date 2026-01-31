import yfinance as yf


class StockService:
    
    @staticmethod
    def get_price(symbol: str) -> dict:
        """실시간 주식 가격 가져오기"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            current_price = (
                info.get("currentPrice") or
                info.get("regularMarketPrice") or
                info.get("previousClose") or
                0
            )
            
            return {
                "symbol": symbol,
                "price": current_price,
                "name": info.get("shortName", symbol),
                "currency": info.get("currency", "USD"),
                "change": info.get("regularMarketChange", 0),
                "change_percent": info.get("regularMarketChangePercent", 0)
            }
        except Exception as e:
            return {
                "symbol": symbol,
                "price": 0,
                "name": symbol,
                "currency": "USD",
                "change": 0,
                "change_percent": 0,
                "error": str(e)
            }
    
    @staticmethod
    def get_prices(symbols: list) -> list:
        """여러 주식 가격 한번에 가져오기"""
        results = []
        for symbol in symbols:
            results.append(StockService.get_price(symbol))
        return results
    
    @staticmethod
    def get_history(symbol: str, period: str = "1mo") -> list:
        """주식 가격 히스토리 가져오기"""
        try:
            ticker = yf.Ticker(symbol)
            history = ticker.history(period=period)
            
            data = []
            for date, row in history.iterrows():
                data.append({
                    "time": date.strftime("%Y-%m-%d"),
                    "open": round(row["Open"], 2),
                    "high": round(row["High"], 2),
                    "low": round(row["Low"], 2),
                    "close": round(row["Close"], 2),
                    "volume": int(row["Volume"])
                })
            
            return data
        except Exception as e:
            return []
