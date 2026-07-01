package com.blackrabbit.signup;

import com.blackrabbit.common.dto.ResultDTO;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.ResponseBody;

import java.util.Map;

@Controller
public class SignupController {

  @Autowired
  SignupService signupService;


  // 사용자 id/ email 중복 확인 api
  @RequestMapping(value="/api/signinDup", method = RequestMethod.POST )
  @ResponseBody
  public ResultDTO signinCheckDup(@RequestBody Map<String, String> req){
    String type = req.get("type"); // id or email
    String value = req.get("value");

   return signupService.checkDup(type, value);
  }

  // 회원가입 진행
  @RequestMapping(value="/api/userSignup", method = RequestMethod.POST)
  @ResponseBody
  public ResultDTO createUser(@RequestBody SignupDTO req){
    // 성공 시 로그인 박스로 redirect 하자
    return signupService.createUser(req);
  }
}
