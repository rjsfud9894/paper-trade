import yfinance as yf


class StockService:
    
    @staticmethod
    def get_price(symbol: str) -> dict:
        """실시간 주식 가격 가져오기"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # 현재 가격 (여러 필드 중 있는 거 사용)
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
