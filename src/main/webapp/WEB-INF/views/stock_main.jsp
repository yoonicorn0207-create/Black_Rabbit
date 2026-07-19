<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8" %>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<c:set var="pageTitle" value="BLACK RABBIT HTS" />
<%@ include file="/WEB-INF/views/common/layout-top.jsp" %>
<script src="https://cdn.jsdelivr.net/npm/apexcharts"></script>
<link rel="stylesheet" href="<c:url value='/resources/css/stock.css'/>">

<body class="min-h-screen flex flex-col">

<!-- 기존 1화면 영역: 헤더 + 메인 -->
<div class="h-screen flex flex-col overflow-hidden p-2">
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
            <div class="flex justify-between items-center">
                <h2 class="text-xs font-bold uppercase">Watchlist</h2>
                <span id="watchlist-count" class="text-[12px] text-gray-500"></span>
            </div>
            <div class="flex gap-1">
                <input type="text" id="stockInput"
                       placeholder="종목 검색..."
                       class="flex-1 p-2 bg-gray-900 border border-gray-700 rounded text-sm">
                <button onclick="searchStock()" class="px-3 bg-gray-700 rounded text-sm text-white">검색</button>
            </div>
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
</div>
<!-- /1화면 영역 -->

<!-- 푸터: 스크롤을 내려야 보임 -->
<footer class="px-6 py-5 border-t border-gray-800 bg-black flex items-center justify-between text-xs text-gray-500">
    <p>&copy; 2026 BlackRabbit. All rights reserved.</p>
    <div class="flex items-center gap-6">
        <!-- 개발자 1 -->
        <div class="flex items-center gap-2">
            <span class="text-gray-400">yoonicorn9227</span>
            <a href="https://github.com/yoonicorn0207-create" target="_blank" rel="noopener noreferrer"
               class="hover:text-white transition" title="GitHub - yoonicorn9227">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
                    <path d="M12 .5C5.65.5.5 5.65.5 12c0 5.08 3.29 9.39 7.86 10.91.57.1.78-.25.78-.55 0-.27-.01-1.17-.02-2.12-3.2.7-3.88-1.36-3.88-1.36-.52-1.33-1.28-1.69-1.28-1.69-1.04-.71.08-.7.08-.7 1.15.08 1.76 1.18 1.76 1.18 1.03 1.76 2.7 1.25 3.36.96.1-.75.4-1.25.73-1.54-2.55-.29-5.24-1.28-5.24-5.68 0-1.26.45-2.28 1.18-3.09-.12-.29-.51-1.46.11-3.05 0 0 .96-.31 3.15 1.18a10.9 10.9 0 0 1 5.74 0c2.19-1.49 3.15-1.18 3.15-1.18.62 1.59.23 2.76.11 3.05.74.81 1.18 1.83 1.18 3.09 0 4.41-2.69 5.38-5.25 5.67.41.36.78 1.06.78 2.15 0 1.55-.01 2.79-.01 3.17 0 .3.2.66.79.55A10.51 10.51 0 0 0 23.5 12C23.5 5.65 18.35.5 12 .5z"/>
                </svg>
            </a>
        </div>

        <!-- 구분선 -->
        <div class="w-px h-4 bg-gray-800"></div>

        <!-- 개발자 2 -->
        <div class="flex items-center gap-2">
            <span class="text-gray-400">js37hwang</span>
            <a href="https://github.com/js37hwang" target="_blank" rel="noopener noreferrer"
               class="hover:text-white transition" title="GitHub - js37hwang">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
                    <path d="M12 .5C5.65.5.5 5.65.5 12c0 5.08 3.29 9.39 7.86 10.91.57.1.78-.25.78-.55 0-.27-.01-1.17-.02-2.12-3.2.7-3.88-1.36-3.88-1.36-.52-1.33-1.28-1.69-1.28-1.69-1.04-.71.08-.7.08-.7 1.15.08 1.76 1.18 1.76 1.18 1.03 1.76 2.7 1.25 3.36.96.1-.75.4-1.25.73-1.54-2.55-.29-5.24-1.28-5.24-5.68 0-1.26.45-2.28 1.18-3.09-.12-.29-.51-1.46.11-3.05 0 0 .96-.31 3.15 1.18a10.9 10.9 0 0 1 5.74 0c2.19-1.49 3.15-1.18 3.15-1.18.62 1.59.23 2.76.11 3.05.74.81 1.18 1.83 1.18 3.09 0 4.41-2.69 5.38-5.25 5.67.41.36.78 1.06.78 2.15 0 1.55-.01 2.79-.01 3.17 0 .3.2.66.79.55A10.51 10.51 0 0 0 23.5 12C23.5 5.65 18.35.5 12 .5z"/>
                </svg>
            </a>
        </div>
    </div>
</footer>

<script src="<c:url value='/resources/js/stock.js'/>"></script>
<%@ include file="/WEB-INF/views/editUserInfoModal.jsp" %>
<%@ include file="/WEB-INF/views/common/layout-bottom.jsp" %>