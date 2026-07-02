package com.blackrabbit.common.util;

import javax.servlet.*;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;
import java.io.IOException;
import java.rmi.ServerException;

// 정상적인 로그인을 거치지 않은 사용자가 로그인 외 페이지에 접근하지 못하도록
public class AuthFilter implements Filter {
  public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain)
      throws IOException, ServerException {

    HttpServletRequest httpRequest = (HttpServletRequest) request;
    HttpServletResponse httpResponse = (HttpServletResponse) response;
    HttpSession session = httpRequest.getSession(false);

    // 로그인 여부 및 권한 확인
    boolean isLoggedIn = (session != null && session.getAttribute("userRole") != null);
    String requestURI = httpRequest.getRequestURI();

    // 보호가 필요한 경로인 경우
    if (requestURI.startsWith("/admin") && !"ADMIN".equals(session.getAttribute("userRole"))) {
      httpResponse.sendRedirect(httpRequest.getContextPath() + "/login.jsp?error=unauthorized");
      return;
    }

    try {
      chain.doFilter(request, response);
    } catch (ServletException e) {
      throw new RuntimeException(e);
    }
  }
}
