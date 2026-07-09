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
    <link rel="stylesheet" href="<c:url value='/resources/css/stock.css'/>">
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
                <span id="loginUserId"
                    class="text-xs font-bold text-yellow-400 cursor-pointer hover:underline"
                    onclick="openEditModal()"></span>

            <button class="text-xs text-gray-500 hover:text-red-400 transition font-bold" onclick="logout()">[LOGOUT]</button>
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
</body>
<script src="<c:url value='/resources/js/stock.js'/>"></script>
<script src="<c:url value='/resources/js/common.js'/>"></script>
<%@ include file="/WEB-INF/views/common/modal.jsp" %>
<%@ include file="/WEB-INF/views/editUserInfoModal.jsp" %>
</body>
</html>