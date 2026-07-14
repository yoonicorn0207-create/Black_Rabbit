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

    /*2026_0714 Swagger UI 설정*/
    // 1. URI 값을 먼저 가져와야 합니다.
    String uri = request.getRequestURI();
    System.out.println("현재 인터셉터가 확인하는 URI: " + uri); // 이 로그가 콘솔에 찍히는지 보세요!
    // 2. Swagger 및 로그인 관련 경로는 무조건 통과시킵니다.
    // 주의: 실제 프로젝트의 로그인 경로가 /login 이라면 포함시켜 주세요.
    if (uri.contains("/login") ||
            uri.contains("/swagger") ||
            uri.contains("/v2/api-docs") ||
            uri.contains("/webjars")) {
      return true;
    }//

    /*2026_0714 Swagger UI 설정*/


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
