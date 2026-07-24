package com.blackrabbit.chatbot;

import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

public interface ChatService {

  // fastApi의 스트리밍 응답을 실시간으로 받아 return
  void streamChat(String sessionId, String message, SseEmitter emitter);
}