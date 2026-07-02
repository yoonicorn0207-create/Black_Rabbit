package com.blackrabbit.login;

import com.blackrabbit.common.dto.ResultDTO;
import com.blackrabbit.common.util.JwtProvider;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.*;

import javax.servlet.http.HttpSession;
import java.util.HashMap;
import java.util.Map;

@Controller
public class LoginController {

  @Autowired
  LoginMapper loginMapper;
  @Autowired
  LoginService loginService;
  @Autowired
  JwtProvider jwtProvider;


  // 로그인 메인 페이지 호출
  @RequestMapping("/login")
  public String getLoginPage(){return "login";}


  // 로그인 요청 api
  @RequestMapping(value="/api/userLogin", method = RequestMethod.POST)
  @ResponseBody
  public ResultDTO userLogin(@RequestBody LoginDTO loginData){
    return loginService.loginUser(loginData);
  }


  // 토큰 재발급 (refresh를 이용하여 access를 재발급)loginUser.loginUser
  @PostMapping("/api/auth/refresh")
  public ResultDTO newAccessToken(@RequestHeader("Authorization") String refreshToken) {
    // "Bearer " 제거 후 순수 토큰값만 추출
    String token = refreshToken.replace("Bearer ", "");
    return loginService.refreshAccessToken(token);
  }


  // 로그아웃= db에 저장된 refresh 토큰 삭제
  @PostMapping("/api/userLogout")
  public void delRefreshToken(@RequestHeader("Authorization") String authHeader, HttpSession session){
    // 세션 완전 삭제
    if (session != null) {
      session.invalidate();
    }

    // 1. 토큰에서 유저네임 추출 (JWT Provider 사용)
    String token = authHeader.substring(7);
    String username = jwtProvider.getUsernameFromToken(token);

    // 2. DB에서 해당 유저의 Refresh Token 삭제
    loginService.logoutUser(username);
  }

  // 메인 페이지에서 로그인된 사용자 id 출력
  @GetMapping("/api/userInfo")
  @ResponseBody
  public Map<String, Object> getUserInfo(HttpSession session) {
    Map<String, Object> result = new HashMap<>();

    String userIdIdx = (String) session.getAttribute("userId");

    if (userIdIdx != null) {
      int idx = Integer.parseInt(userIdIdx);

      String userId = loginMapper.getUserId(idx);
      result.put("userId", userId);
    } else {
      result.put("userId", null);
    }
    return result;
  }
}
