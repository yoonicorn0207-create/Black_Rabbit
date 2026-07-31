// ======================== 챗봇 위젯 로직 ==============================

document.addEventListener('DOMContentLoaded', () => {
  const fab = document.getElementById('chatbot-fab');
  const chatWindow = document.getElementById('chatbot-window');
  const closeBtn = document.getElementById('chatbot-close');
  const sendBtn = document.getElementById('chatbot-send');
  const input = document.getElementById('chatbot-input');
  const messages = document.getElementById('chatbot-messages');

  // ---------------- 드래그 로직 ----------------
  let isDragging = false;
  let hasMoved = false;
  let offsetX = 0, offsetY = 0;

  fab.addEventListener('mousedown', (e) => {
    isDragging = true;
    hasMoved = false;
    fab.style.cursor = 'grabbing';
    fab.classList.add('chatbot-fab-dragging');

    const rect = fab.getBoundingClientRect();
    offsetX = e.clientX - rect.left;
    offsetY = e.clientY - rect.top;

    e.preventDefault();
  });

  document.addEventListener('mousemove', (e) => {
    if (!isDragging) return;
    hasMoved = true;

    let newLeft = e.clientX - offsetX;
    let newTop = e.clientY - offsetY;

    // 화면 밖으로 안 나가게 경계 제한
    const maxLeft = window.innerWidth - fab.offsetWidth;
    const maxTop = window.innerHeight - fab.offsetHeight;
    newLeft = Math.max(0, Math.min(newLeft, maxLeft));
    newTop = Math.max(0, Math.min(newTop, maxTop));

    fab.style.left = `${newLeft}px`;
    fab.style.top = `${newTop}px`;
    fab.style.right = 'auto';
    fab.style.bottom = 'auto';
  });

  document.addEventListener('mouseup', () => {
    if (isDragging) {
      isDragging = false;
      // fab.style.cursor = 'grab';
      // fab.classList.remove('chatbot-fab-dragging');
      // savePosition();
      savePosition();
    }
  });

  // 클릭(드래그 아님)일 때만 채팅창 토글
  fab.addEventListener('click', () => {
    if (hasMoved) return; // 드래그였다면 클릭으로 취급 안 함
    toggleChatWindow();
  });

  // ---------------- 채팅창 드래그 및, 채팅 버튼 위치 기준 채팅창 오픈 ----------------
  const chatHeader = document.getElementById("chatbot-header");

  let draggingWindow = false;
  let winOffsetX = 0;
  let winOffsetY = 0;

  chatHeader.addEventListener("mousedown", (e) => {

    draggingWindow = true;

    const rect = chatWindow.getBoundingClientRect();

    winOffsetX = e.clientX - rect.left;
    winOffsetY = e.clientY - rect.top;

    e.preventDefault();
  });

  document.addEventListener("mousemove", (e) => {

    if (!draggingWindow) return;

    let left = e.clientX - winOffsetX;
    let top = e.clientY - winOffsetY;

    left = Math.max(
      0,
      Math.min(left, window.innerWidth - chatWindow.offsetWidth)
    );

    top = Math.max(
      0,
      Math.min(top, window.innerHeight - chatWindow.offsetHeight)
    );

    chatWindow.style.left = left + "px";
    chatWindow.style.top = top + "px";
    chatWindow.style.right = "auto";
    chatWindow.style.bottom = "auto";
  });

  document.addEventListener("mouseup", () => {
    draggingWindow = false;
  });

  // ---------------- 화면을 줄여도 버튼이 화면 밖으로 사라지지 않게 ----------------
  window.addEventListener("resize", () => {

    const rect = fab.getBoundingClientRect();

    let left = rect.left;
    let top = rect.top;

    left = Math.max(
      10,
      Math.min(left, window.innerWidth - fab.offsetWidth - 10)
    );

    top = Math.max(
      10,
      Math.min(top, window.innerHeight - fab.offsetHeight - 10)
    );

    fab.style.left = left + "px";
    fab.style.top = top + "px";
    fab.style.right = "auto";   // 추가
    fab.style.bottom = "auto";  // 추가

    if (!chatWindow.classList.contains("hidden")) {
      positionChatWindow();
    }
  });

  function saveChatWindowPosition() {
    const rect = chatWindow.getBoundingClientRect();

    localStorage.setItem(
      "chatbotWindowPosition",
      JSON.stringify({
        left: rect.left,
        top: rect.top
      })
    );
  }

  // ---------------- 채팅창 위치 복원 ----------------
  function restoreChatWindowPosition() {

    const saved = localStorage.getItem("chatbotWindowPosition");

    if (!saved) return;

    const {left, top} = JSON.parse(saved);

    chatWindow.style.left = left + "px";
    chatWindow.style.top = top + "px";
    chatWindow.style.right = "auto";
    chatWindow.style.bottom = "auto";
  }

  // ---------------- 위치 저장/복원 (localStorage) ----------------
  function savePosition() {
    const rect = fab.getBoundingClientRect();

    localStorage.setItem(
      "chatbotFabPosition",
      JSON.stringify({
        leftRatio: rect.left / window.innerWidth,
        topRatio: rect.top / window.innerHeight
      })
    );
  }

  function restorePosition() {

    const saved = localStorage.getItem("chatbotFabPosition");

    if (!saved) return;

    const { leftRatio, topRatio } = JSON.parse(saved);

    let left = leftRatio * window.innerWidth;
    let top = topRatio * window.innerHeight;

    // 화면 밖 방지
    left = Math.min(left, window.innerWidth - fab.offsetWidth - 10);
    top = Math.min(top, window.innerHeight - fab.offsetHeight - 10);

    left = Math.max(10, left);
    top = Math.max(10, top);

    fab.style.left = left + "px";
    fab.style.top = top + "px";
    fab.style.right = "auto";
    fab.style.bottom = "auto";
  }

  restorePosition();

  // ---------------- 채팅창 열림 위치 설정 ----------------
  function positionChatWindow() {
    const fabRect = fab.getBoundingClientRect();

    const margin = 12;

    let left = fabRect.left + fab.offsetWidth - chatWindow.offsetWidth;
    let top = fabRect.top - chatWindow.offsetHeight - margin;

    // 화면 경계 처리
    left = Math.max(
      10,
      Math.min(left, window.innerWidth - chatWindow.offsetWidth - 10)
    );

    top = Math.max(
      10,
      Math.min(top, window.innerHeight - chatWindow.offsetHeight - 10)
    );

    chatWindow.style.left = `${left}px`;
    chatWindow.style.top = `${top}px`;
    chatWindow.style.right = "auto";
    chatWindow.style.bottom = "auto";
  }

  // ---------------- 채팅창 토글 ----------------
  function toggleChatWindow() {
    chatWindow.classList.toggle('hidden');

    if (!chatWindow.classList.contains('hidden')) {
      positionChatWindow();
      input.focus();
    }
  }

  closeBtn.addEventListener('click', () => {
    chatWindow.classList.add('hidden');
  });

  // ---------------- 메시지 전송 ----------------
  function appendMessage(text, isUser = false) {
    const bubble = document.createElement('div');
    bubble.className = isUser
      ? "chatbot-bubble-user px-3 py-2 max-w-[75%] ml-auto"
      : "chatbot-bubble-bot px-3 py-2 max-w-[75%]";
    bubble.innerText = text;
    messages.appendChild(bubble);
    messages.scrollTop = messages.scrollHeight;
    return bubble;
  }

  // ---------------- 띄어쓰기 파싱 ----------------
  function escapeHtml(text) {
    const div = document.createElement('div');
    div.innerText = text;
    return div.innerHTML;  // <, >, & 등을 안전하게 이스케이프
  }

  // ---------------- 출처 url에 하이퍼링크 삽입 ----------------
  function linkify(text) {
    const escaped = escapeHtml(text);
    const withBreaks = escaped.replace(/\n/g, '<br>');
    // [텍스트](URL) 마크다운 링크만 파싱 — URL이 괄호 안에 명확히 갇혀 있어 뒤 텍스트 오염 불가능
    const mdLinkRegex = /\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g;
    return withBreaks.replace(mdLinkRegex, (_, label, url) =>
      `<a href="${url}" target="_blank" class="underline text-blue-600">${label}</a>`
    );
  }

  // ---------------- 세션 구분용 함수 ----------------
  function getSessionId() {
    let id = localStorage.getItem('chatSessionId');
    if (!id) {
      id = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
        const r = Math.random() * 16 | 0, v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
      });
      localStorage.setItem('chatSessionId', id);
    }
    return id;
  }

  async function sendMessage() {
    const text = input.value.trim();
    if (!text) return;

    appendMessage(text, true);
    input.value = '';

    const botBubble = appendMessage('...');

    // 버튼 로딩 상태 시작
    sendBtn.disabled = true;
    sendBtn.classList.add('chatbot-send-loading');
    const originalBtnText = sendBtn.innerText;
    sendBtn.innerText = '';

    try {
      const response = await fetch('/api/chat/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text, sessionId: getSessionId() }),
        silent: true
      });

      if (!response.ok) {
        botBubble.innerText = "답변을 가져오지 못했습니다. 잠시 후 다시 시도해주세요.";
        return;
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let firstChunk = true;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n\n').filter(l => l.startsWith('data:'));

        for (const line of lines) {
          const data = line.replace(/^data: ?/, '');
          if (data === '[DONE]') {
            botBubble.innerHTML = linkify(botBubble.innerText);  // 스트림 종료 시 링크 변환
            return;
          }

          if (firstChunk) {
            botBubble.innerText = '';
            firstChunk = false;
          }
          botBubble.innerText += data;   // 스트리밍 중엔 순수 텍스트로 이어붙임
          messages.scrollTop = messages.scrollHeight;
        }
      }

      if (firstChunk) {
        botBubble.innerText = "답변을 가져오지 못했습니다.";
      } else {
        botBubble.innerHTML = linkify(botBubble.innerText);  // 정상 종료(done)로 루프 빠져나온 경우도 처리
      }
    } catch (error) {
      botBubble.innerText = "오류가 발생했습니다. 잠시 후 다시 시도해주세요.";
      console.error('챗봇 응답 실패:', error);
    } finally {
      // 버튼 로딩 상태 종료 (성공/실패/무관하게 항상 실행)
      sendBtn.disabled = false;
      sendBtn.classList.remove('chatbot-send-loading');
      sendBtn.innerText = originalBtnText;
    }
  }

  sendBtn.addEventListener('click', sendMessage);
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') sendMessage();
  });
});