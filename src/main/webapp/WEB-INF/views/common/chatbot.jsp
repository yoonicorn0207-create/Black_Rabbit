<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8" %>
<link rel="stylesheet" href="<c:url value='/resources/css/chatbot.css'/>">

<!-- 드래그 가능한 챗봇 플로팅 버튼 -->
<div id="chatbot-fab"
     class="fixed z-[9998] w-16 h-16 rounded-full cursor-grab flex items-center justify-center chatbot-fab-glow">
    <div class="chatbot-fab-glass w-full h-full rounded-full flex items-center justify-center">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="#a3e635" stroke-width="0.5">
            <path d="M12 2C6.48 2 2 6.03 2 11c0 2.42 1.09 4.6 2.86 6.19-.1.98-.4 2.32-1.11 3.6a.5.5 0 0 0 .58.72c1.9-.5 3.36-1.27 4.24-1.8.99.28 2.05.29 3.43.29 5.52 0 10-4.03 10-9s-4.48-9-10-9z"
                  fill="#a3e635"/>
        </svg>
    </div>
</div>

<!-- 챗봇 채팅창 -->
<div id="chatbot-window"
     class="hidden fixed z-[9999] w-96 h-[520px] bg-white border border-gray-200 rounded-xl flex flex-col overflow-hidden">

    <!-- 헤더 -->
    <div id="chatbot-header" class="bg-gray-50 px-4 py-3 flex items-center justify-between border-b border-gray-200">
        <span class="text-sm font-bold text-gray-800">BlackRabbit AI 어시스턴트</span>
        <button id="chatbot-close" class="text-gray-400 hover:text-gray-700 text-lg leading-none">&times;</button>
    </div>

    <!-- 메시지 영역 -->
    <div id="chatbot-messages" class="flex-1 overflow-y-auto p-3 space-y-3 text-sm bg-white">
        <div class="chatbot-bubble-bot px-3 py-2 max-w-[75%]">안녕하세요! 오늘 매수하기 좋은 종목을 추천해드리거나, 궁금한 종목에 대해 물어보세요.</div>
    </div>

    <!-- 입력 영역 -->
    <div class="border-t border-gray-200 p-2 flex gap-2 bg-white">
        <input type="text" id="chatbot-input" placeholder="메시지를 입력하세요..."
               class="flex-1 bg-gray-50 border border-gray-300 rounded-lg px-3 py-2 text-sm text-gray-800 focus:outline-none">
        <button id="chatbot-send" class="px-4 rounded-lg text-sm font-bold transition-colors">전송</button>
    </div>
</div>

<script src="<c:url value='/resources/js/chatbot.js'/>"></script>