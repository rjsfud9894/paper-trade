// API 주소
const API_URL = "http://127.0.0.1:8000";

// 토큰 저장
let token = localStorage.getItem("token");

// 주식 가격 캐시
let stockPrices = {};

// 페이지 로드 시
document.addEventListener("DOMContentLoaded", function() {
    if (token) {
        showDashboard();
    }
    
    // 폼 이벤트 등록
    document.getElementById("login-form").addEventListener("submit", login);
    document.getElementById("register-form").addEventListener("submit", register);
});

// 탭 전환
function showTab(tabName) {
    const tabs = document.querySelectorAll(".tab");
    tabs.forEach(tab => tab.classList.remove("active"));
    
    if (tabName === "login") {
        tabs[0].classList.add("active");
        document.getElementById("login-form").classList.remove("hidden");
        document.getElementById("register-form").classList.add("hidden");
    } else {
        tabs[1].classList.add("active");
        document.getElementById("login-form").classList.add("hidden");
        document.getElementById("register-form").classList.remove("hidden");
    }
}

// 메시지 표시
function showMessage(text, type) {
    const messageEl = document.getElementById("message");
    messageEl.textContent = text;
    messageEl.className = "message " + type;
    messageEl.classList.remove("hidden");
    
    setTimeout(() => {
        messageEl.classList.add("hidden");
    }, 3000);
}

// 회원가입
async function register(event) {
    event.preventDefault();
    
    const username = document.getElementById("register-username").value;
    const email = document.getElementById("register-email").value;
    const password = document.getElementById("register-password").value;
    
    try {
        const response = await fetch(API_URL + "/auth/register", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ username, email, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage("회원가입 성공! 로그인해주세요.", "success");
            showTab("login");
        } else {
            showMessage(data.detail || "회원가입 실패", "error");
        }
    } catch (error) {
        showMessage("서버 연결 실패", "error");
    }
}

// 로그인
async function login(event) {
    event.preventDefault();
    
    const email = document.getElementById("login-email").value;
    const password = document.getElementById("login-password").value;
    
    try {
        const response = await fetch(API_URL + "/auth/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            token = data.access_token;
            localStorage.setItem("token", token);
            showMessage("로그인 성공!", "success");
            showDashboard();
        } else {
            showMessage(data.detail || "로그인 실패", "error");
        }
    } catch (error) {
        showMessage("서버 연결 실패", "error");
    }
}

// 로그아웃
function logout() {
    token = null;
    localStorage.removeItem("token");
    document.getElementById("auth-section").classList.remove("hidden");
    document.getElementById("dashboard-section").classList.add("hidden");
    showMessage("로그아웃 되었습니다", "success");
}

// 대시보드 표시
async function showDashboard() {
    document.getElementById("auth-section").classList.add("hidden");
    document.getElementById("dashboard-section").classList.remove("hidden");
    
    await loadUserInfo();
    await loadStocks();
    await loadRealtimePrices();
    await loadPortfolio();
    await loadHistory();
}

// 유저 정보 로드
async function loadUserInfo() {
    try {
        const response = await fetch(API_URL + "/auth/me?token=" + token);
        const data = await response.json();
        
        if (response.ok) {
            document.getElementById("user-name").textContent = "안녕하세요, " + data.username + "님!";
        }
    } catch (error) {
        console.error("유저 정보 로드 실패:", error);
    }
}

// 실시간 가격 로드
async function loadRealtimePrices() {
    try {
        const response = await fetch(API_URL + "/stocks/prices/realtime");
        const data = await response.json();
        
        if (response.ok) {
            // 가격 캐시에 저장
            data.forEach(stock => {
                stockPrices[stock.symbol] = stock;
            });
            
            // 주식 목록 표시
            displayStockPrices(data);
        }
    } catch (error) {
        console.error("실시간 가격 로드 실패:", error);
    }
}

// 주식 가격 표시
function displayStockPrices(stocks) {
    const stockList = document.getElementById("stock-list");
    
    if (stocks.length === 0) {
        stockList.innerHTML = "<p>등록된 주식이 없습니다.</p>";
        return;
    }
    
    stockList.innerHTML = stocks.map(stock => {
        const changeClass = stock.change >= 0 ? "positive" : "negative";
        const changeSymbol = stock.change >= 0 ? "+" : "";
        
        return `
            <div class="stock-item">
                <div class="stock-info">
                    <strong>${stock.symbol}</strong>
                    <span>${stock.name}</span>
                </div>
                <div class="stock-price">
                    <span class="price">${formatPrice(stock.price, stock.currency)}</span>
                    <span class="change ${changeClass}">
                        ${changeSymbol}${stock.change.toFixed(2)} (${changeSymbol}${stock.change_percent.toFixed(2)}%)
                    </span>
                </div>
                <button onclick="fillTradeForm('${stock.symbol}', ${stock.price})">선택</button>
            </div>
        `;
    }).join("");
}

// 거래 폼에 자동 입력
function fillTradeForm(symbol, price) {
    document.getElementById("trade-symbol").value = symbol;
    document.getElementById("trade-price").value = price;
    document.getElementById("trade-quantity").focus();
}

// 포트폴리오 로드
async function loadPortfolio() {
    try {
        const response = await fetch(API_URL + "/portfolio/summary?token=" + token);
        const data = await response.json();
        
        if (response.ok) {
            document.getElementById("balance").textContent = formatMoney(data.balance);
            document.getElementById("invested").textContent = formatMoney(data.total_invested);
            document.getElementById("total-assets").textContent = formatMoney(data.total_assets);
            
            // 보유 주식 표시 (실시간 가격 포함)
            const holdingsList = document.getElementById("holdings-list");
            if (data.holdings.length === 0) {
                holdingsList.innerHTML = "<p>보유한 주식이 없습니다.</p>";
            } else {
                holdingsList.innerHTML = data.holdings.map(h => {
                    const currentPrice = stockPrices[h.symbol]?.price || h.avg_price;
                    const currentValue = h.quantity * currentPrice;
                    const profit = currentValue - h.total_invested;
                    const profitPercent = (profit / h.total_invested * 100).toFixed(2);
                    const profitClass = profit >= 0 ? "positive" : "negative";
                    const profitSymbol = profit >= 0 ? "+" : "";
                    
                    return `
                        <div class="holding-item">
                            <div>
                                <strong>${h.symbol}</strong> (${h.name})
                                <br>
                                <small>${h.quantity}주 / 평균 ${formatMoney(h.avg_price)}</small>
                            </div>
                            <div class="holding-value">
                                <span>현재가: ${formatMoney(currentPrice)}</span>
                                <span class="${profitClass}">
                                    ${profitSymbol}${formatMoney(profit)} (${profitSymbol}${profitPercent}%)
                                </span>
                            </div>
                        </div>
                    `;
                }).join("");
            }
        }
    } catch (error) {
        console.error("포트폴리오 로드 실패:", error);
    }
}

// 주식 목록 로드 (select용)
async function loadStocks() {
    try {
        const response = await fetch(API_URL + "/stocks");
        const data = await response.json();
        
        if (response.ok) {
            const select = document.getElementById("trade-symbol");
            select.innerHTML = '<option value="">종목 선택</option>';
            
            data.forEach(stock => {
                select.innerHTML += `<option value="${stock.symbol}">${stock.symbol} - ${stock.name}</option>`;
            });
        }
    } catch (error) {
        console.error("주식 목록 로드 실패:", error);
    }
}

// 거래 내역 로드
async function loadHistory() {
    try {
        const response = await fetch(API_URL + "/trades/history?token=" + token);
        const data = await response.json();
        
        if (response.ok) {
            const historyList = document.getElementById("history-list");
            
            if (data.length === 0) {
                historyList.innerHTML = "<p>거래 내역이 없습니다.</p>";
            } else {
                historyList.innerHTML = data.map(t => `
                    <div class="history-item">
                        <span class="${t.trade_type}">${t.trade_type === "buy" ? "매수" : "매도"}</span>
                        <span>주식ID: ${t.stock_id}</span>
                        <span>${t.quantity}주</span>
                        <span>${formatMoney(t.price)}</span>
                    </div>
                `).join("");
            }
        }
    } catch (error) {
        console.error("거래 내역 로드 실패:", error);
    }
}

// 거래 실행
async function executeTrade(tradeType) {
    const symbol = document.getElementById("trade-symbol").value;
    const quantity = parseInt(document.getElementById("trade-quantity").value);
    const price = parseFloat(document.getElementById("trade-price").value);
    
    if (!symbol || !quantity || !price) {
        showMessage("모든 항목을 입력해주세요", "error");
        return;
    }
    
    const endpoint = tradeType === "buy" ? "/trades/buy" : "/trades/sell";
    
    try {
        const response = await fetch(API_URL + endpoint + "?token=" + token, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ symbol, quantity, price })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage(tradeType === "buy" ? "매수 완료!" : "매도 완료!", "success");
            
            // 폼 초기화
            document.getElementById("trade-quantity").value = "";
            document.getElementById("trade-price").value = "";
            
            // 데이터 새로고침
            await loadPortfolio();
            await loadHistory();
        } else {
            showMessage(data.detail || "거래 실패", "error");
        }
    } catch (error) {
        showMessage("서버 연결 실패", "error");
    }
}

// 가격 새로고침
async function refreshPrices() {
    showMessage("가격 새로고침 중...", "success");
    await loadRealtimePrices();
    await loadPortfolio();
    showMessage("가격 업데이트 완료!", "success");
}

// 금액 포맷 (원화)
function formatMoney(amount) {
    return new Intl.NumberFormat("ko-KR", {
        style: "currency",
        currency: "KRW"
    }).format(amount);
}

// 가격 포맷 (통화 맞춤)
function formatPrice(amount, currency) {
    return new Intl.NumberFormat("en-US", {
        style: "currency",
        currency: currency || "USD"
    }).format(amount);
}
