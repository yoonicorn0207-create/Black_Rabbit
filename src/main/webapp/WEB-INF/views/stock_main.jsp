<%@ page isELIgnored="true" %>
<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8" %>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>BLACK RABBIT HTS</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/apexcharts"></script>
    <style>
        body {
            background-color: #050505;
            color: #d1d4dc;
            font-family: sans-serif;
        }

        .bg-panel {
            background-color: #0a0e17;
            border: 1px solid #1f2937;
        }

        .text-up {
            color: #ef4444;
        }

        .text-down {
            color: #3b82f6;
        }

        /* 차트 높이 강제 지정하여 렌더링 문제 해결 */
        #main-chart {
            width: 100%;
            height: 500px;
        }

        /* 스크롤바 커스텀 */
        * {
            scrollbar-width: thin;
            scrollbar-color: #374151 #050505;
        }

        *::-webkit-scrollbar {
            width: 6px;
            height: 6px;
        }

        *::-webkit-scrollbar-track {
            background: #050505;
            border-radius: 9999px;
        }

        *::-webkit-scrollbar-thumb {
            background: #374151;
            border-radius: 9999px;
            transition: background 0.2s ease;
        }

        *::-webkit-scrollbar-thumb:hover {
            background: #4b5563;
        }

        *::-webkit-scrollbar-corner {
            background: #050505;
        }

        /* 일본 주봉 active 클래스 추가 */
        .period-btn {
            width: 60px;
            background-color: #1f2937;
            color: white;
            transition: all 0.15s ease;
        }

        .period-btn:hover {
            background-color: #374151;
        }

        .period-btn.active {
            background: linear-gradient(135deg, #f7df1e, #d4b80f);
            color: #1e293b;
            border: 1px solid #f7df1e;
            font-weight: 500;
        }

        .neon-price {
            color: #ccff00; /* 형광 연두색 */
            font-weight: bold;
            text-shadow: 0 0 5px rgba(204, 255, 0, 0.5);
        }
    </style>
</head>
<body class="h-screen flex flex-col overflow-hidden p-2">

<!-- 헤더 -->
<header class="h-14 flex items-center justify-between px-4 mb-2 border-b border-gray-800">
    <div class="flex items-center gap-4 justify-between ">
        <!-- 타이틀 -->
        <div class="text-2xl font-black italic text-white">BLACK<span class="text-red-500">RABBIT</span></div>

        <!-- 코스피/ 코스닥 지수 -->
        <div class="flex gap-4 text-sm text-gray-400 border-l border-gray-700 pl-4">
            <p>KOSPI <span class="text-green-400 font-mono">2,650.45</span></p>
            <p>KOSDAQ <span class="text-red-500 font-mono">850.20</span></p>
        </div>
    </div>

    <div class="flex items-center gap-4 justify-between ">
        <!-- 로그인 사용자 보유금 (2026_0706 수정)-->
        <div class="bg-gray-900 px-4 py-1 rounded border border-gray-700 text-right">
            <p class="text-[9px] text-gray-500">AVAILABLE BALANCE</p>
            <p id="available-balance" class="font-bold text-white font-mono">₩ 0</p>
        </div>

        <!-- 로그아웃 버튼 -->
        <div class="flex items-center gap-3">
            <span id="loginUserId" class="text-xs font-bold text-yellow-400"></span>

            <button class="text-xs text-gray-500 hover:text-red-400 transition font-bold" onclick="logout()">[LOGOUT]
            </button>
        </div>
    </div>
</header>

<!-- 메인 섹션 -->
<main class="flex-1 flex gap-3 overflow-hidden">

    <!-- 좌측 섹션 -->
    <section class="w-1/5 flex flex-col gap-2">
        <h2 class="text-xs font-bold uppercase">Watchlist</h2>
        <!-- 검색 -->
        <div class="flex gap-1">
            <input type="text" id="stockInput"
                   placeholder="종목 검색..."
                   oninput="filterWatchlist(this.value)"
                   class="flex-1 p-2 bg-gray-900 border border-gray-700 rounded text-sm">
            <button onclick="addStock()" class="px-3 bg-gray-700 rounded text-sm text-white">검색</button>
        </div>
        <!-- 종목 리스트 출력 -->
        <div id="watchlist" class="flex-1 overflow-y-auto space-y-1"></div>
    </section>

    <!-- 메인 차트 섹션 -->
    <section class="flex-1 flex flex-col bg-panel rounded p-3">
        <!-- 선택 종목명 및 봉 선택-->
        <div class="flex gap-2 mb-2 items-center">
            <span class="text-base font-bold text-white mr-2" id="stock-title">삼성전자</span>
            <button onclick="updatePeriod('minute', this)" class="period-btn px-3 py-1 rounded text-sm">1분</button>
            <button onclick="updatePeriod('hour', this)" class="period-btn px-3 py-1 rounded text-sm">1시간</button>
            <button onclick="updatePeriod('day', this)" class="period-btn active px-3 py-1 rounded text-sm">1일</button>
            <button onclick="updatePeriod('week', this)" class="period-btn px-3 py-1 rounded text-sm">1주</button>
            <button onclick="updatePeriod('month', this)" class="period-btn px-3 py-1 rounded text-sm">1월</button>
        </div>
        <!-- 차트 -->
        <div id="main-chart"></div>
    </section>

    <!-- 우측 섹션 -->
    <section class="w-1/5 flex flex-col gap-3">

        <!-- 사용자별 보유 종목 -->
        <div class="bg-panel p-3 rounded flex-[3] flex flex-col min-h-0">
            <h3 class="text-xs font-bold mb-2">MY HOLDINGS</h3>
            <div id="donut-chart" class="h-32"></div>
            <div id="holding-list" class="mt-3 text-sm space-y-1 overflow-y-auto flex-1 min-h-0"></div>
        </div>

        <!-- 선택 항목 매수/ 매도 섹션 -->
        <div class="bg-panel p-3 rounded flex-[1]">
            <h3 class="text-xs font-bold mb-2">ORDER</h3>
            <div id="order-info" class="mb-2 text-sm text-gray-400">
                <span id="order-stock-name" class="font-bold text-white">종목을 선택하세요</span>
                <span id="order-stock-price" class="ml-2 font-mono neon-price"></span>
            </div>
            <input type="number" id="order-quantity" placeholder="수량"
                   class="w-full p-2 bg-black border border-gray-700 rounded mb-2 text-sm">
            <div class="grid grid-cols-2 gap-2">
                <button onclick="executeOrder('buy')" class="bg-red-600 py-2 rounded text-sm font-bold text-white">매수
                </button>
                <button onclick="executeOrder('sell')" class="bg-blue-600 py-2 rounded text-sm font-bold text-white">
                    매도
                </button>
            </div>
        </div>
    </section>
</main>

<script>
    let allStocks = []; // 전역 변수 추가
    let currentStockCode = "005930"; // 기본값 삼성전자

    /* * [API 통신] (2026_0626에 추가)
         * fetchAndRender: 서버의 /api/stockList 경로에서 종목 데이터를 가져와
         * 렌더링 함수인 renderWatchlist로 데이터를 전달.
         */
    async function fetchAndRender() {
        try {
            const response = await fetch('/api/stockList');
            const data = await response.json();
            // 1. 전체 데이터를 전역 변수에 담기
            allStocks = Array.isArray(data) ? data : []; // 데이터를 전역 변수에 보관(2026_0629)

            // 2. 초기 리스트 렌더링
            renderWatchlist(allStocks); // 초기에는 전체 출력(2026_0629)
        } catch (error) {
            console.error('에러:', error);
        }
    }//

    /* * [Watchlist UI 렌더링] (2026_0626에 추가)
     * renderWatchlist: API로 받은 stockList 배열을 순회하며 HTML 요소를 생성하여 #watchlist 영역에 삽입.
     * 클릭 시 상단 종목 타이틀을 변경하는 기능을 포함.
     */
    function renderWatchlist(stockList) {
        const wl = document.getElementById('watchlist');
        wl.innerHTML = '';

        // stockList가 배열인지 확인 후 처리
        if (!Array.isArray(stockList)) return;

        stockList.forEach(s => {
            const code = s.stck_shrn_iscd || "000000";
            const name = s.hts_kor_isnm || "종목명";
            const price = s.stck_prpr ? parseInt(s.stck_prpr).toLocaleString() : '0';

            const div = document.createElement('div');
            // 리스트 디자인을 좀 더 깔끔하게 수정
            div.className = "px-3 py-2 bg-black rounded border border-gray-800 hover:border-gray-600 transition cursor-pointer flex justify-between items-center";
            div.innerHTML = `
                <div class="text-sm font-bold text-white truncate">[${code}] ${name}</div>
                <div class="text-sm font-mono text-gray-300">₩ ${price}</div>
            `;

            // 리스트 클릭 시 차트 타이틀 변경 예시 (필요 시)
            div.onclick = () => {
                currentStockCode = code; // 전역 변수 업데이트
                document.getElementById('stock-title').innerText = name;

                // 2. [추가] ORDER 영역에 종목명 및 현재가 표시(2026_0701)
                document.getElementById('order-stock-name').innerText = name;
                document.getElementById('order-stock-price').innerText = `₩ ${price}`;

                // 3. 차트 데이터 로드
                const activeBtn = document.querySelector('.period-btn.active');
                const period = activeBtn ? activeBtn.innerText : 'day';

                fetchChartData(code, period);
            };

            wl.appendChild(div);
        });
    }

    // [추가] fetch를 사용하는 새로운 차트 데이터 로드 함수 (2026_0629 생성)
    async function fetchChartData(stockCode, period) {
        try {
            // 서버의 컨트롤러로 요청 전송
            const url = period === 'minute' || period === 'hour' ? "minHourChartData" : "chartData";
            const response = await fetch(`/api/${url}?code=${stockCode}&period=${period}`);

            if (!response.ok) throw new Error('서버 데이터 응답 실패');

            const data = await response.json(); // DB에서 변환된 JSON 데이터 수신
            console.log("받아온 데이터:", data); // F12 콘솔에서 확인용

            // ApexCharts 차트 객체(chart)의 시리즈 데이터 업데이트
            // 가격 등을 차드에 반영하기 위해 가격 등을 숫자로 명시적 변환 진행
            const formattedData = data.map(item => {
                return {
                    x: item.x, // 날짜
                    y: [
                        parseFloat(item.y[0]), // 시가
                        parseFloat(item.y[1]), // 고가
                        parseFloat(item.y[2]), // 저가
                        parseFloat(item.y[3])  // 종가(또는 현재가)
                    ]
                }
            });
            // 이동평균선 계산
            const ma5 = calculateMA(5, formattedData);
            const ma20 = calculateMA(20, formattedData);
            const ma60 = calculateMA(60, formattedData);
            const ma120 = calculateMA(120, formattedData);

            // [중요] 모든 데이터를 한 번에 업데이트
            chart.updateSeries([
                {name: '주가', type: 'candlestick', data: formattedData},
                {name: '5', type: 'line', data: ma5},
                {name: '20', type: 'line', data: ma20},
                {name: '60', type: 'line', data: ma60},
                {name: '120', type: 'line', data: ma120}
            ]);

            // 종목명 업데이트 (선택 사항)
            // document.getElementById('stock-title').innerText = stockCode;

        } catch (error) {
            console.error("차트 데이터를 불러오는 중 에러 발생:", error);
        }
    }


    /* * [수정된 보유 종목 UI 렌더링] (2026_0630)
       * 서버에서 API(/api/myHoldings)를 호출해 실제 데이터를 가져와 그립니다.
       */
    async function renderHoldings() {
        try {
            const response = await fetch('/api/myHoldings');
            if (!response.ok) throw new Error('데이터 로드 실패');

            const data = await response.json();

            const list = document.getElementById('holding-list');
            // 1. 헤더 수정: 4개 -> 5개 컬럼으로 (종목, 수량, 평단, 현재, 수익) (2026_0701 수정)
            list.innerHTML = `<div class="grid grid-cols-5 gap-1 text-gray-500 border-b border-gray-800 pb-1 mb-1 text-[10px]">
                        <span class="text-center">종목</span>
                        <span class="text-center">수량</span>
                        <span class="text-center">평단</span>
                        <span class="text-center">현재</span>
                        <span class="text-center">수익</span>
                      </div>`;

            // 1. 도넛 차트 데이터 준비
            const chartSeries = [];
            const chartLabels = [];

            data.forEach(s => {
                const profit = s.profit_rate;
                const color = profit >= 0 ? 'text-up' : 'text-down';

                // 2. 행 클릭 시 매도 정보 자동 입력 (onclick 이벤트 추가) (2026_0701)
                list.innerHTML += `
    <div class="grid grid-cols-5 gap-1 items-center text-[11px] py-1 border-b border-gray-900 cursor-pointer hover:bg-gray-800"
         onclick="prepareSell('${s.stock_name}', ${s.total_quantity}, '${s.stck_shrn_iscd}', ${s.avg_buy_price})">
        <span class="font-bold text-white truncate text-center">${s.stock_name}</span>
        <span class="font-mono text-gray-300 text-center">${s.total_quantity.toLocaleString()}</span>
        <span class="font-mono text-center">₩ ${s.avg_buy_price.toLocaleString()}</span>
        <span class="font-mono text-center">₩ ${s.current_price.toLocaleString()}</span>
        <span class="${color} font-bold text-center">${profit}%</span>
    </div>`;

                // 2. 도넛 차트용 데이터 배열 채우기
                // 예: (현재가 * 수량)으로 비중 계산
                const evaluationAmount = s.current_price * s.total_quantity;
                chartSeries.push(evaluationAmount);
                chartLabels.push(s.stock_name);
            });

            // 3. 도넛 차트 업데이트 (ApexCharts 제공 메서드)
            donutChart.updateOptions({
                series: chartSeries,
                labels: chartLabels
            });

        } catch (error) {
            console.error("보유 종목 로딩 실패:", error);
        }
    }//renderHoldings(보유종목 리스트)

    /* * [초기화 및 차트 설정]
         * 페이지 로드 시 차트 객체를 선언하고 렌더링합니다.
         */
    // 기존 chart 선언 부분을 아래 내용으로 교체하세요.
    const chart = new ApexCharts(document.querySelector("#main-chart"), {
        series: [
            {name: '주가', type: 'candlestick', data: []},
            {name: '5', type: 'line', data: []},
            {name: '20', type: 'line', data: []},
            {name: '60', type: 'line', data: []},
            {name: '120', type: 'line', data: []}
        ],
        chart: {
            type: 'candlestick',
            height: '100%',
            zoom: {enabled: true},
            pan: {enabled: true},
            // [추가된 부분] 범례를 위해 상단에 여백 확보
            animations: {enabled: false},
            toolbar: {show: false}
        },
        // [추가된 부분] 범례(Legend) 설정 시작
        legend: {
            show: true,
            position: 'top',      // 상단 배치
            horizontalAlign: 'right', // 우측 정렬 (요청하신 빨간 영역 쪽)
            fontSize: '12px',
            labels: {
                colors: '#d1d4dc' // 전체적인 테마 색상에 맞춤
            },
            markers: {
                width: 12,
                height: 12,
                radius: 0
            }
        },
        // [추가된 부분] 범례 설정 끝
        stroke: {
            width: [0, 2, 2, 2, 2],
            curve: 'smooth',
            colors: ['#FFFFFF', '#FFD700', '#FF4500', '#00FF00', '#00BFFF']
        },
        tooltip: {
            shared: true,
            intersect: false
        },
        plotOptions: {candlestick: {colors: {upward: '#ef4444', downward: '#3b82f6'}}},
        xaxis: {labels: {style: {colors: '#9CA3AF'}}},
        yaxis: {
            labels: {
                style: {colors: '#9CA3AF'},
                formatter: function (val) {
                    return val ? val.toLocaleString() : "";
                }
            },
            forceNiceScale: true,
            decimalsInFloat: 0
        }
    });

    //보유종목 도넛형 차트(2026_0630)
    const donutChart = new ApexCharts(document.querySelector("#donut-chart"), {
        series: [], // 빈 배열로 시작
        labels: [],
        chart: {type: 'donut', height: 160},
        legend: {show: false}
    });


    /* * [이벤트 핸들러]
     * updatePeriod: 차트 기간 버튼 클릭 시 호출됩니다.
     * 버튼 디자인을 변경하고 선택된 기간에 맞춰 차트 데이터를 업데이트합니다.
     */
    function updatePeriod(period, button) {

        // 1. UI 활성화 상태 변경
        document.querySelectorAll('.period-btn').forEach(btn => btn.classList.remove('active'));
        button.classList.add('active');

        // 서버에 파라미터 전달 (예: 'day')
        fetchChartData(currentStockCode, period);
    }


    // 검색창 입력 시 호출될 함수(2026_0629)
    function filterWatchlist(keyword) {
        const searchKeyword = keyword.toLowerCase().trim();

        // 코드 혹은 이름이 포함된 항목만 필터링
        const filtered = allStocks.filter(s =>
            (s.stck_shrn_iscd && s.stck_shrn_iscd.includes(searchKeyword)) ||
            (s.hts_kor_isnm && s.hts_kor_isnm.toLowerCase().includes(searchKeyword))
        );

        renderWatchlist(filtered); // 필터링된 데이터만 다시 그리기
    }//검색창 검색어 입력 시 호출


    // [수정] 매수/매도 공통 실행 함수(2026_0701)
    async function executeOrder(type) {
        const quantity = document.getElementById('order-quantity').value;
        const stockName = document.getElementById('order-stock-name').innerText;

        if (!quantity || quantity <= 0) {
            alert("수량을 확인하세요.");
            return;
        }

        const url = type === 'buy' ? '/api/buyStock' : '/api/sellStock';

        const response = await fetch(url, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({stockCode: currentStockCode, stockName: stockName, quantity: parseInt(quantity)})
        });

        if (response.ok) {
            alert(type === 'buy' ? "매수가 완료되었습니다." : "매도가 완료되었습니다.");

            // 1. 보유 종목 리스트 갱신
            renderHoldings();

            // 2. [추가] 예수금 즉시 갱신 (2026_0706)
            loadUserBalance();

            // 3. 입력창 초기화 (선택 사항) (2026_0706)
            document.getElementById('order-quantity').value = '';
        } else {
            alert("거래 처리에 실패했습니다. 잔액 또는 보유 수량을 확인하세요.");
        }
    }

    // [추가] 매도 시 입력창 자동 채우기(2026_0701)
    function prepareSell(name, quantity, code, avgPrice) {
        document.getElementById('order-stock-name').innerText = name;
        // 평단가 표시를 위해 새로운 span 추가 또는 기존 영역 활용
        // 여기서는 종목명 옆에 평단가를 함께 표시하도록 구성
        document.getElementById('order-stock-name').innerText = `${name} (평단: ₩${avgPrice.toLocaleString()})`;

        document.getElementById('order-quantity').value = quantity;
        currentStockCode = code;
    }

    // [추가] 예수금 정보를 서버에서 가져와 화면에 출력 (2026_0706)
    async function loadUserBalance() {
        try {
            const response = await fetch('/api/userBalance');
            const data = await response.json();
            if (data.balance !== undefined) {
                // 천 단위 콤마 처리
                document.getElementById('available-balance').innerText = `₩ ${data.balance.toLocaleString()}`;
            }
        } catch (error) {
            console.error("예수금 로드 실패:", error);
        }
    }//loadUserBalance()


    // 3분(180,000ms)마다 KOSPI & KOSDAQ지수 업데이트(2026_0708)
    async function updateMarketIndices() {
        try {
            const response = await fetch('/api/market-indices');
            if (!response.ok) throw new Error('네트워크 응답 오류');

            const data = await response.json();

            // 데이터가 배열인지 확인 후 처리 (안전장치)
            const latest = Array.isArray(data) ? data[0] : data;

            if (latest) {
                const indexContainer = document.querySelector('.flex.gap-4.text-sm.text-gray-400');
                indexContainer.innerHTML = `
                <p>KOSPI <span class="text-green-400 font-mono">${latest.kospi.toLocaleString()}</span></p>
                <p>KOSDAQ <span class="text-red-500 font-mono">${latest.kosdaq.toLocaleString()}</span></p>
            `;
            }
        } catch (error) {
            console.error("지수 업데이트 실패:", error);
            // 에러 시 사용자에게 알림을 띄우거나, 기존 값을 유지하는 로직 추가 가능
        }
    }

    // document.addEventListener('DOMContentLoaded', ...) 내부에 추가
    setInterval(updateMarketIndices, 180000); // 3분 간격 호출


    // 수정된 이동평균 계산 함수 (기간 파라미터 추가)
    function calculateMA(dayCount, data) {
        let result = [];
        for (let i = 0; i < data.length; i++) {
            if (i < dayCount - 1) {
                result.push({x: data[i].x, y: null});
            } else {
                let sum = 0;
                for (let j = 0; j < dayCount; j++) {
                    // 데이터 배열에서 종가(y[3])를 가져옴
                    sum += parseFloat(data[i - j].y[3]);
                }
                result.push({x: data[i].x, y: (sum / dayCount).toFixed(0)});
            }
        }
        return result;
    }


    /* * [페이지 라이프사이클 관리]
         * DOMContentLoaded: HTML 문서가 모두 로드된 직후 실행되는 초기화 블록입니다.
         */
    // [중요] 페이지 로드 시 실행되는 부분 (2026_0626에 추가)
    document.addEventListener('DOMContentLoaded', async () => {
        // 1. Watchlist 서버 데이터 호출
        fetchAndRender();

        // 2. 보유 종목 표 출력
        renderHoldings();

        // 3. 예수금 불러오기 추가! (2026_0706)
        loadUserBalance();

        // 4. 차트 초기화 (초기 데이터는 빈 배열로 시작)
        chart.updateSeries([{data: []}]); //(2026_0629 추가)
        chart.render();
        donutChart.render();

        //5. 페이지 로드 시 즉시 (KOSPI & KOSDAQ)지수 한번 가져오기 (2026_0708)
        updateMarketIndices();

        // 2. 페이지 로드 시 삼성전자(005930) 기본 차트 로딩 (2026_0629)
        fetchChartData("005930", "day");


        // 5초마다 데이터 갱신
        setInterval(fetchAndRender, 500000);

        //3분마다 (KOSPI & KOSDAQ)지수로드
        setInterval(updateMarketIndices, 180000); // 3분
    });

    // =============================== 로그아웃 ===============================
    async function logout() {
        try {
            // 서버 측 토큰 무효화 요청
            await fetch('/api/logout', {method: 'POST'});
        } catch (e) {
            console.error("로그아웃 서버 처리 실패");
        } finally {
            // 성공하든 실패하든 클라이언트 로컬 스토리지는 반드시 비움
            localStorage.removeItem("accessToken");
            localStorage.removeItem("refreshToken");

            // 로그인 페이지로 이동
            window.location.href = "/login";
        }
    }

    // =============================== 로그인된 사용자 id 출력을 위한 로직 ===============================
    async function loadUserInfo() {
        const res = await fetch('/api/userInfo');
        const data = await res.json();
        if (data.userId) {
            document.getElementById('loginUserId').innerText = data.userId + "님";
        }
    }

    // 페이지 로드 시 실행
    document.addEventListener('DOMContentLoaded', loadUserInfo);
</script>
<script src="<c:url value='/resources/js/common.js'/>"></script>
<%@ include file="/WEB-INF/views/common/modal.jsp" %>
</body>
</html>