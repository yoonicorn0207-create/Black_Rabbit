package com.blackrabbit.common.util;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.servlet.handler.HandlerInterceptorAdapter;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

// 토큰 만료 체킹을 위한 interceptor 로직
// 프론트에서 들어오는 모든 호출은 interceptor를 먼저 거친다
// accesstoken 안에 들어있는 isUseKisApi 값을 확인하여 호출 api 기존 로직/ kis api 분기 처리 진행
public class JwtInterceptor extends HandlerInterceptorAdapter {

  @Autowired
  private JwtProvider jwtProvider;

  @Override
  public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) throws Exception {
    String authHeader = request.getHeader("Authorization");

    if (authHeader != null && authHeader.startsWith("Bearer ")) {
      String token = authHeader.substring(7);

      if (jwtProvider.validateToken(token)) {
        // [추가된 로직] 토큰에서 모의투자 사용 여부를 추출
        boolean isUseKis = jwtProvider.getIsUseKisFromToken(token);
        String username = jwtProvider.getUsernameFromToken(token);

        // [추가된 로직] request 속성에 담아서 컨트롤러까지 전달
        request.setAttribute("isUseKis", isUseKis);
        request.setAttribute("username", username);

        return true; // 인증 성공
      }
    }

    response.sendError(HttpServletResponse.SC_UNAUTHORIZED);
    return false; // 인증 실패
  }
}