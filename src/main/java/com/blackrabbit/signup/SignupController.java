package com.blackrabbit.signup;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;

@Controller
public class SignupController {

  // 로그인 메인 페이지 호출
  @RequestMapping("/login")
  public String getLoginPage(){return "login";}

}
