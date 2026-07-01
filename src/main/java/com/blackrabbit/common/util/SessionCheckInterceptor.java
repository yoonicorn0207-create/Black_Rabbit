package com.blackrabbit.common.util;

import org.springframework.web.servlet.HandlerInterceptor;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;

public class SessionCheckInterceptor implements HandlerInterceptor {
  @Override
  public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) throws Exception {
    HttpSession session = request.getSession(false); // 세션이 없으면 새로 생성하지 않음

    // 1. 세션이 아예 없거나, userId가 없으면 인증 실패 처리
    if (session == null || session.getAttribute("userId") == null) {
      response.setStatus(419); // 419 세션 만료
      return false; // 컨트롤러로 가는 길을 막음 (로직 실행 방지)
    }

    // 2. 세션이 살아있다면 통과! (원래 호출하려던 컨트롤러로 진행)
    return true;
  }
}
