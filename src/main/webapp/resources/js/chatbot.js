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
      fab.style.cursor = 'grab';
      fab.classList.remove('chatbot-fab-dragging');
      savePosition();
    }
  });

  // 클릭(드래그 아님)일 때만 채팅창 토글
  fab.addEventListener('click', () => {
    if (hasMoved) return; // 드래그였다면 클릭으로 취급 안 함
    toggleChatWindow();
  });

  // ---------------- 위치 저장/복원 (localStorage) ----------------
  function savePosition() {
    const rect = fab.getBoundingClientRect();
    localStorage.setItem('chatbotFabPosition', JSON.stringify({
      left: rect.left,
      top: rect.top
    }));
  }

  function restorePosition() {
    const saved = localStorage.getItem('chatbotFabPosition');
    if (!saved) return;
    try {
      const { left, top } = JSON.parse(saved);
      fab.style.left = `${left}px`;
      fab.style.top = `${top}px`;
      fab.style.right = 'auto';
      fab.style.bottom = 'auto';
    } catch (e) {
      console.error('챗봇 위치 복원 실패:', e);
    }
  }
  restorePosition();

  // ---------------- 채팅창 토글 ----------------
  function toggleChatWindow() {
    chatWindow.classList.toggle('hidden');
    if (!chatWindow.classList.contains('hidden')) {
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

  async function sendMessage() {
    const text = input.value.trim();
    if (!text) return;

    appendMessage(text, true);
    input.value = '';

    const loadingBubble = appendMessage('답변을 생성하는 중...');

    try {
      const response = await fetch('/api/chatbot/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text }),
        silent: true // 전체 화면 로딩창은 안 띄움 (채팅 버블 자체가 로딩 표시)
      });
      const result = await response.json();

      loadingBubble.innerText = result.answer || "답변을 가져오지 못했습니다.";

      // 출처 표기 (있으면 추가)
      if (result.sources && result.sources.length > 0) {
        const sourceDiv = document.createElement('div');
        sourceDiv.className = "text-[10px] text-gray-500 mt-1";
        sourceDiv.innerHTML = "출처: " + result.sources.map(s =>
          `<a href="${s.url}" target="_blank" class="underline hover:text-gray-300">${s.title}</a>`
        ).join(", ");
        messages.appendChild(sourceDiv);
        messages.scrollTop = messages.scrollHeight;
      }
    } catch (error) {
      loadingBubble.innerText = "오류가 발생했습니다. 잠시 후 다시 시도해주세요.";
      console.error('챗봇 응답 실패:', error);
    }
  }

  sendBtn.addEventListener('click', sendMessage);
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') sendMessage();
  });
});