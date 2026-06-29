<%@ page isELIgnored="true" %>
<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8" %>
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
            width: 50px;
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
        <!-- 로그인 사용자 보유금 -->
        <div class="bg-gray-900 px-4 py-1 rounded border border-gray-700 text-right">
            <p class="text-[9px] text-gray-500">AVAILABLE BALANCE</p>
            <p class="font-bold text-white font-mono">₩ 12,450,000</p>
        </div>

        <!-- 로그아웃 버튼 -->
        <button class="text-xs text-gray-500 hover:text-red-400 transition font-bold">[LOGOUT]</button>
    </div>
</header>

<!-- 메인 섹션 -->
<main class="flex-1 flex gap-3 overflow-hidden">

    <!-- 좌측 섹션 -->
    <section class="w-1/5 flex flex-col gap-2">
        <h2 class="text-xs font-bold uppercase">Watchlist</h2>
        <!-- 검색 -->
        <div class="flex gap-1">
            <input type="text" id="stockInput" placeholder="종목 검색..."
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
            <button onclick="updatePeriod('1D', this)" class="period-btn active px-3 py-1 rounded text-sm">1일</button>
            <button onclick="updatePeriod('1W', this)" class="period-btn px-3 py-1 rounded text-sm">1주</button>
            <button onclick="updatePeriod('1M', this)" class="period-btn px-3 py-1 rounded text-sm">1월</button>
            <button onclick="updatePeriod('1Y', this)" class="period-btn px-3 py-1 rounded text-sm">1년</button>
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
            <input type="number" placeholder="수량"
                   class="w-full p-2 bg-black border border-gray-700 rounded mb-2 text-sm">
            <div class="grid grid-cols-2 gap-2">
                <button class="bg-red-600 py-2 rounded text-sm font-bold text-white">매수</button>
                <button class="bg-blue-600 py-2 rounded text-sm font-bold text-white">매도</button>
            </div>
        </div>
    </section>
</main>

<script>
    const stocks = [
        {code: '005930', name: '삼성전자', price: 73500, avg: 70000, ratio: 15, change: '+1.2%'},
        {code: '000660', name: 'SK하이닉스', price: 152000, avg: 160000, ratio: 10, change: '-0.8%'},
        {code: '373220', name: 'LG에너지솔루션', price: 380000, avg: 390000, ratio: 8, change: '+1.2%'},
        {code: '207940', name: '삼성바이오로직스', price: 820000, avg: 800000, ratio: 7, change: '-0.8%'},
        {code: '005380', name: '현대차', price: 240000, avg: 230000, ratio: 7, change: '+1.2%'},
        {code: '000270', name: '기아', price: 110000, avg: 105000, ratio: 6, change: '-0.8%'},
        {code: '068270', name: '셀트리온', price: 180000, avg: 185000, ratio: 5, change: '+1.2%'},
        {code: '005490', name: 'POSCO홀딩스', price: 420000, avg: 410000, ratio: 5, change: '-0.8%'},
        {code: '035420', name: 'NAVER', price: 185000, avg: 180000, ratio: 5, change: '-0.8%'},
        {code: '028260', name: '삼성물산', price: 145000, avg: 140000, ratio: 4, change: '+1.2%'},
        {code: '105560', name: 'KB금융', price: 75000, avg: 72000, ratio: 4, change: '-0.8%'},
        {code: '012330', name: '현대모비스', price: 230000, avg: 225000, ratio: 4, change: '+1.2%'},
        {code: '051910', name: 'LG화학', price: 350000, avg: 360000, ratio: 4, change: '-0.8%'},
        {code: '035720', name: '카카오', price: 45000, avg: 48000, ratio: 3, change: '+1.2%'},
        {code: '086790', name: '하나금융지주', price: 60000, avg: 58000, ratio: 3, change: '-0.8%'},
        {code: '032830', name: '삼성생명', price: 95000, avg: 92000, ratio: 3, change: '+1.2%'},
        {code: '055550', name: '신한지주', price: 48000, avg: 47000, ratio: 2, change: '-0.8%'},
        {code: '096770', name: 'SK이노베이션', price: 110000, avg: 120000, ratio: 2, change: '+1.2%'},
        {code: '033780', name: 'KT&G', price: 92000, avg: 90000, ratio: 2, change: '-0.8%'},
        {code: '018260', name: '삼성에스디에스', price: 160000, avg: 155000, ratio: 1, change: '+1.2%'}
    ];

    /* * [API 통신] (2026_0626에 추가)
         * fetchAndRender: 서버의 /api/stockList 경로에서 종목 데이터를 가져와
         * 렌더링 함수인 renderWatchlist로 데이터를 전달.
         */
    async function fetchAndRender() {
        try {
            const response = await fetch('/api/stockList');
            const data = await response.json();
            renderWatchlist(Array.isArray(data) ? data : []);
        } catch (error) {
            console.error('에러:', error);
        }
    }

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
                document.getElementById('stock-title').innerText = name;

                // [추가] 리스트 클릭 시 차트 데이터를 서버에서 새로 가져오기 (2026_0629)
                // period는 현재 선택된 버튼 값을 사용하거나, 기본값 '1D'를 넣습니다.
                fetchChartData(code, '1D');
            };

            wl.appendChild(div);
        });
    }

    /* * [데이터 생성] - (기존)
         * generateCandleData: 차트에 사용할 랜덤 봉 데이터를 생성합니다.
         * days 인자만큼의 날짜 데이터를 만들어 반환합니다.
         */
    <%--function generateCandleData(days) {--%>
    <%--    let data = [], price = 70000;--%>
    <%--    for (let i = 0; i < days; i++) {--%>
    <%--        let change = (Math.random() - 0.5) * 4000;--%>
    <%--        data.push({x: `2026-06-${i + 1}`, y: [price, price + 2000, price - 2000, price + change]});--%>
    <%--        price += change;--%>
    <%--    }--%>
    <%--    return data;--%>
    <%--}--%>

    // [추가] fetch를 사용하는 새로운 차트 데이터 로드 함수 (2026_0629 생성)
    async function fetchChartData(stockCode, period) {
        try {
            // 서버의 컨트롤러로 요청 전송
            const response = await fetch(`/api/chartData?code=${stockCode}&period=${period}`);

            if (!response.ok) throw new Error('서버 데이터 응답 실패');

            const data = await response.json(); // DB에서 변환된 JSON 데이터 수신
            console.log("받아온 데이터:", data); // F12 콘솔에서 확인용

            // ApexCharts 차트 객체(chart)의 시리즈 데이터 업데이트
            chart.updateSeries([{data: data}]); // 서버에서 받은 데이터로 업데이트

            // 종목명 업데이트 (선택 사항)
            // document.getElementById('stock-title').innerText = stockCode;

        } catch (error) {
            console.error("차트 데이터를 불러오는 중 에러 발생:", error);
        }
    }


    /* * [보유 종목 UI 렌더링]
     * renderHoldings: stocks 배열 정보를 바탕으로
     * #holding-list 영역에 보유 주식 현황 표를 생성합니다.
     */
    function renderHoldings() {
        const list = document.getElementById('holding-list');
        list.innerHTML = `<div class="grid grid-cols-4 gap-1 text-gray-500 border-b border-gray-800 pb-1 mb-1"><span>종목</span><span>평단</span><span>현재</span><span>수익</span></div>`;
        stocks.forEach(s => {
            const profit = ((s.price - s.avg) / s.avg * 100).toFixed(1);
            const color = profit >= 0 ? 'text-up' : 'text-down';
            list.innerHTML += `<div class="grid grid-cols-4 gap-1 items-center"><span class="font-bold text-white truncate">${s.name}</span><span>${s.avg.toLocaleString()}</span><span>${s.price.toLocaleString()}</span><span class="${color}">${profit}%</span></div>`;
        });
    }

    /* * [초기화 및 차트 설정]
         * 페이지 로드 시 차트 객체를 선언하고 렌더링합니다.
         */
    const chart = new ApexCharts(document.querySelector("#main-chart"), {
        series: [{data: []}],
        chart: {type: 'candlestick', height: '100%', toolbar: {show: false}},
        plotOptions: {candlestick: {colors: {upward: '#ef4444', downward: '#3b82f6'}}},
        xaxis: {labels: {style: {colors: '#9CA3AF'}}},
        yaxis: {labels: {style: {colors: '#9CA3AF'}}}
    });
    chart.render();

    const donutChart = new ApexCharts(document.querySelector("#donut-chart"), {
        series: stocks.map(s => s.ratio),
        labels: stocks.map(s => s.name),
        chart: {type: 'donut', height: 160},
        legend: {show: false}
    });


    /* * [이벤트 핸들러]
     * updatePeriod: 차트 기간 버튼 클릭 시 호출됩니다.
     * 버튼 디자인을 변경하고 선택된 기간에 맞춰 차트 데이터를 업데이트합니다.
     */
    function updatePeriod(period, button) {

        document.querySelectorAll('.period-btn').forEach(btn => {
            btn.classList.remove('active');
        });

        button.classList.add('active');

        const days =
            period === '1D' ? 30 :
                period === '1W' ? 90 :
                    period === '1M' ? 180 :
                        365;

        chart.updateSeries([{data: generateCandleData(days)}]);
    }

    /* * [페이지 라이프사이클 관리]
         * DOMContentLoaded: HTML 문서가 모두 로드된 직후 실행되는 초기화 블록입니다.
         */
    // [중요] 페이지 로드 시 실행되는 부분 (2026_0626에 추가)
    document.addEventListener('DOMContentLoaded', async () => {
        renderHoldings(); // 보유 종목 표 출력
        fetchAndRender();  // 1. Watchlist 서버 데이터 호출

        // 1. 차트 초기화 (초기 데이터는 빈 배열로 시작)
        chart.updateSeries([{data: []}]); //(2026_0629 추가)
        chart.render();
        donutChart.render();

        // 2. 페이지 로드 시 삼성전자(005930) 기본 차트 로딩 (2026_0629)
        fetchChartData("005930", "1D");


        // 5초마다 데이터 갱신
        setInterval(fetchAndRender, 5000);
    });


</script>
</body>
</html>