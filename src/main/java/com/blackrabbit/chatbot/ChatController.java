package com.blackrabbit.chatbot;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import javax.servlet.http.HttpServletResponse;

@Controller
public class ChatController {

  @Autowired ChatService chatService;

  @RequestMapping(value = "/api/chat/stream", method = RequestMethod.POST)
  public SseEmitter chatStream(@RequestBody ChatReqDTO chatRequestDTO, HttpServletResponse response) {
    // 핵심: SseEmitter가 내부적으로 문자열 변환할 때 이 응답의 실제 Content-Type/인코딩을 참조함
    response.setCharacterEncoding("UTF-8");
    response.setContentType("text/event-stream;charset=UTF-8");

    SseEmitter emitter = new SseEmitter(0L);
    chatService.streamChat(chatRequestDTO.getSessionId(), chatRequestDTO.getMessage(), emitter);
    return emitter;
  }
}