package com.blackrabbit.common.util;

import javax.servlet.*;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;
import java.io.IOException;

public class AuthFilter implements Filter {

  // 보호가 필요하지 않은 라우터 리스트- 화이트리스트 방식으로 진행
  // 하위 경로 전체 허용
  private static final String[] PUBLIC_PREFIX_PATHS = { "/login", "/resources" };
  // 정확히 일치할 때만
  private static final String[] PUBLIC_EXACT_PATHS  = {
      "/api/userLogin",
      "/api/userSignup",
      "/api/signinDup",
      "/api/getKisToken" };

  private boolean isPublic(String uri) {
    for (String p : PUBLIC_PREFIX_PATHS) if (uri.startsWith(p)) return true;
    for (String p : PUBLIC_EXACT_PATHS) if (uri.equals(p)) return true;
    return false;
  }


  public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain)
      throws IOException, ServletException { // ServerException 대신 ServletException 사용

    HttpServletRequest httpRequest = (HttpServletRequest) request;
    HttpServletResponse httpResponse = (HttpServletResponse) response;

    String requestURI = httpRequest.getRequestURI();
    HttpSession session = httpRequest.getSession(false);

    // 공개 페이지 접근 시 return
    if (isPublic(requestURI)) {
      chain.doFilter(request, response);
      return;
    }

    // 로그인 여부 확인
    if (session == null || session.getAttribute("userId") == null) {
      httpResponse.sendRedirect(httpRequest.getContextPath() + "/login");
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