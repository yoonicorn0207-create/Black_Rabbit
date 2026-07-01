package com.blackrabbit.common.util;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.servlet.handler.HandlerInterceptorAdapter;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

// 토큰 만료 체킹을 위한 interceptor 로직
// 프론트에서 들어오는 모든 호출은 interceptor를 먼저 거친다
public class JwtInterceptor extends HandlerInterceptorAdapter {

  @Autowired
  private JwtProvider jwtProvider;

  @Override
  public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) throws Exception {
    String authHeader = request.getHeader("Authorization");

    if (authHeader != null && authHeader.startsWith("Bearer ")) {
      String token = authHeader.substring(7);
      if (jwtProvider.validateToken(token)) {
        return true;
      }
    }

    response.sendError(HttpServletResponse.SC_UNAUTHORIZED);
    return false;
  }
}
