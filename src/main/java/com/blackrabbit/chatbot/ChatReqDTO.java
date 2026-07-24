package com.blackrabbit.chatbot;

public class ChatReqDTO {
  private String sessionId;
  private String message;

  // getter/setter
  public String getSessionId() { return sessionId; }
  public void setSessionId(String sessionId) { this.sessionId = sessionId; }
  public String getMessage() { return message; }
  public void setMessage(String message) { this.message = message; }
}
