package com.blackrabbit.common.util;

import javax.servlet.*;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;
import java.io.IOException;

public class AuthFilter implements Filter {
  // 보호가 필요하지 않은 라우터 리스트- 화이트리스트 방식으로 진행
  private static final String[] PUBLIC_PATHS = {
          "/login",
          "/resources",
          "/api/userLogin",     // 로그인 처리
          "/api/userSignup",    // 회원가입 처리
          "/api/signinDup",
  };

  private boolean isPublic(String uri) {
    for (String path : PUBLIC_PATHS) {
      if (uri.startsWith(path)) return true;
    }
    return false;
  }

  public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain)
          throws IOException, ServletException { // ServerException 대신 ServletException 사용

    HttpServletRequest httpRequest = (HttpServletRequest) request;
    HttpServletResponse httpResponse = (HttpServletResponse) response;

    // 1. [추가] 컨텍스트 경로(앱 이름)를 가져오고 순수 경로를 추출
    String contextPath = httpRequest.getContextPath();
    String requestURI = httpRequest.getRequestURI();
    String pathOnly = requestURI.substring(contextPath.length()); // <--- 핵심! "/blackrabbit" 제거

    HttpSession session = httpRequest.getSession(false);

    // 2. [변경] requestURI 대신 추출한 pathOnly를 검사
    if (isPublic(pathOnly)) {
      chain.doFilter(request, response);
      return;
    }

    // 3. [변경] 리다이렉트 시 contextPath를 붙여서 안전하게 이동
    if (session == null || session.getAttribute("userId") == null) {
      httpResponse.sendRedirect(contextPath + "/login"); // <--- 안전한 경로 지정
      return;
    }

    // 추후 관리자 페이지 생성 시 접근자의 권한 확인
//      if (!"ADMIN".equals(session.getAttribute("userRole"))) {
//        httpResponse.sendRedirect(httpRequest.getContextPath() + "/login.jsp?error=unauthorized");
//        return;
//      }

    // 조건에 해당하지 않거나, 권한이 확인된 경우 요청을 통과시킴
    chain.doFilter(request,response);
  }
}