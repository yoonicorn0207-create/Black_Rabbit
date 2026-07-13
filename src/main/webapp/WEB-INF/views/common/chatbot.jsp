<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8" %>

<style>
    /* 메인 컬러 변수화 */
    :root {
        --chatbot-glow-rgb: 163, 230, 53; /* 네온 라임 */
    }
    /* 글래스모피즘 베이스 */
    .chatbot-fab-glass {
        background: rgba(var(--chatbot-glow-rgb), 0.15);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.15);
        box-shadow:
            inset 0 1px 1px rgba(255, 255, 255, 0.25),
            inset 0 -1px 1px rgba(0, 0, 0, 0.2);
        transition: background 0.2s ease;
    }

    .chatbot-fab-glow:hover .chatbot-fab-glass {
        background: rgba(var(--chatbot-glow-rgb), 0.25);
    }

    /* 네온 글로우 펄스 */
    .chatbot-fab-glow {
        animation: neon-pulse 2.4s ease-in-out infinite;
    }

    @keyframes neon-pulse {
        0%, 100% {
            box-shadow:
                0 0 8px 2px rgba(var(--chatbot-glow-rgb), 0.5),
                0 0 20px 6px rgba(var(--chatbot-glow-rgb), 0.25);
        }
        50% {
            box-shadow:
                0 0 14px 4px rgba(var(--chatbot-glow-rgb), 0.8),
                0 0 32px 12px rgba(var(--chatbot-glow-rgb), 0.4);
        }
    }

    .chatbot-fab-dragging {
        animation: none !important;
        box-shadow: 0 0 16px 4px rgba(var(--chatbot-glow-rgb), 0.7) !important;
    }

    /* ---- 채팅창 라임 포인트 컬러 ---- */
    #chatbot-input:focus {
        border-color: rgb(var(--chatbot-glow-rgb), 0.5) !important;
        box-shadow: 0 0 0 2px rgba(var(--chatbot-glow-rgb), 0.2);
    }

    #chatbot-send {
        background-color: rgb(var(--chatbot-glow-rgb), 0.7);
        color: #1a1a1a;
    }
    #chatbot-send:hover {
        background-color: rgba(var(--chatbot-glow-rgb), 0.95);
    }

    /* ---- iMessage 스타일 채팅 버블 ---- */
    .chatbot-bubble-user {
        background-color: #d3f8a0;  /* 연한 파스텔 라임 (눈 안 아픈 톤) */
        color: #1a1a1a;
        border-radius: 18px 18px 4px 18px;  /* 오른쪽 아래만 각지게 -> 말풍선 꼬리 느낌 */
    }

    .chatbot-bubble-bot {
        background-color: #e9e9eb;  /* 아이폰 수신 메시지 색 (연회색) */
        color: #1a1a1a;
        border-radius: 18px 18px 18px 4px;  /* 왼쪽 아래만 각지게 */
    }
</style>

<!-- 드래그 가능한 챗봇 플로팅 버튼 -->
<div id="chatbot-fab"
     class="fixed z-[9998] w-16 h-16 rounded-full cursor-grab flex items-center justify-center chatbot-fab-glow"
     style="right: 24px; bottom: 24px;">
    <div class="chatbot-fab-glass w-full h-full rounded-full flex items-center justify-center">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="#a3e635" stroke-width="0.5">
            <path d="M12 2C6.48 2 2 6.03 2 11c0 2.42 1.09 4.6 2.86 6.19-.1.98-.4 2.32-1.11 3.6a.5.5 0 0 0 .58.72c1.9-.5 3.36-1.27 4.24-1.8.99.28 2.05.29 3.43.29 5.52 0 10-4.03 10-9s-4.48-9-10-9z"
                  fill="#a3e635"/>
        </svg>
    </div>
</div>

<!-- 챗봇 채팅창 -->
<div id="chatbot-window"
     class="hidden fixed z-[9999] w-96 h-[520px] bg-white border border-gray-200 rounded-xl shadow-2xl flex flex-col overflow-hidden"
     style="right: 24px; bottom: 96px;">

    <!-- 헤더 -->
    <div class="bg-gray-50 px-4 py-3 flex items-center justify-between border-b border-gray-200">
        <span class="text-sm font-bold text-gray-800">BlackRabbit AI 어시스턴트</span>
        <button id="chatbot-close" class="text-gray-400 hover:text-gray-700 text-lg leading-none">&times;</button>
    </div>

    <!-- 메시지 영역 -->
    <div id="chatbot-messages" class="flex-1 overflow-y-auto p-3 space-y-3 text-sm bg-white">
        <div class="chatbot-bubble-bot px-3 py-2 max-w-[75%]">
            안녕하세요! 오늘 매수하기 좋은 종목을 추천해드리거나, 궁금한 종목에 대해 물어보세요.
        </div>
    </div>

    <!-- 입력 영역 -->
    <div class="border-t border-gray-200 p-2 flex gap-2 bg-white">
        <input type="text" id="chatbot-input" placeholder="메시지를 입력하세요..."
               class="flex-1 bg-gray-50 border border-gray-300 rounded-lg px-3 py-2 text-sm text-gray-800 focus:outline-none">
        <button id="chatbot-send" class="px-4 rounded-lg text-sm font-bold transition-colors">전송</button>
    </div>
</div>

<script src="<c:url value='/resources/js/chatbot.js'/>"></script>