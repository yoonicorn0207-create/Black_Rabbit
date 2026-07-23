package com.blackrabbit.chatbot;

import org.springframework.core.io.buffer.DataBuffer;
import org.springframework.core.io.buffer.DataBufferUtils;
import org.springframework.http.HttpMethod;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import javax.annotation.Resource;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Map;

@Service("ChatService")
public class ChatServiceImpl implements ChatService {

  @Resource
  private WebClient webClient;

  private static final String FASTAPI_URL = "http://localhost:8000/chat";

  public void streamChat(String sessionId, String message, SseEmitter emitter) {
    Map<String, String> body = new HashMap<>();
    body.put("session_id", sessionId);
    body.put("message", message);

    webClient.method(HttpMethod.POST)
        .uri(FASTAPI_URL)
        .contentType(MediaType.APPLICATION_JSON)
        .accept(MediaType.valueOf("text/event-stream"))
        .bodyValue(body)
        .exchangeToFlux(response -> response.bodyToFlux(DataBuffer.class))
        .map(dataBuffer -> {
          // 원본 바이트를 직접 꺼내서 우리가 명시적으로 UTF-8로 디코딩
          byte[] bytes = new byte[dataBuffer.readableByteCount()];
          dataBuffer.read(bytes);
          DataBufferUtils.release(dataBuffer);
          return new String(bytes, StandardCharsets.UTF_8);
        })
        .doOnNext(chunk -> {
          try {
            String cleaned = chunk.replace("data: ", "").trim();

            if (cleaned.isEmpty()) return;  // 빈 청크는 무시

            if (cleaned.equals("[DONE]")) {
              emitter.complete();
              return;
            }

            emitter.send(SseEmitter.event().data(cleaned, MediaType.valueOf("text/plain;charset=UTF-8")));
          } catch (Exception e) {
            emitter.completeWithError(e);
          }
        })
        .doOnError(emitter::completeWithError)
        .doOnComplete(emitter::complete)
        .subscribe();
  }
}