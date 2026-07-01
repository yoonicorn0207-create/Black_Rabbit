package com.blackrabbit.login;

import com.blackrabbit.common.dto.ResultDTO;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.*;

@Controller
public class LoginController {

  @Autowired
  LoginService loginService;


  // 로그인 메인 페이지 호출
  @RequestMapping("/login")
  public String getLoginPage(){return "login";}


  // 로그인 요청 api
  @RequestMapping(value="/api/userLogin", method = RequestMethod.POST)
  @ResponseBody
  public ResultDTO userLogin(@RequestBody LoginDTO loginData){
    return loginService.loginUser(loginData);
  }


  // 토큰 재발급 (refresh를 이용하여 access를 재발급)
  @PostMapping("/api/auth/refresh")
  public ResultDTO newAccessToken(@RequestHeader("Authorization") String refreshToken) {
    // "Bearer " 제거 후 순수 토큰값만 추출
    String token = refreshToken.replace("Bearer ", "");
    return loginService.refreshAccessToken(token);
  }


  // 로그아웃= db에 저장된 refresh 토큰 삭제
  @PostMapping("/api/userLogout")
  public void delRefreshToken(LoginDTO userData){
    loginService.logoutUser(userData);
  }
}
