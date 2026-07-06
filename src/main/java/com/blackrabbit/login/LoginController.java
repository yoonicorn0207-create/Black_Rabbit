package com.blackrabbit.login;

import com.blackrabbit.common.dto.ResultDTO;
import com.blackrabbit.common.util.JwtProvider;
import com.blackrabbit.kis.KISService;
import com.blackrabbit.kis.KISTokenDTO;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.*;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpSession;
import java.util.HashMap;
import java.util.Map;

@Controller
public class LoginController {

  @Autowired LoginMapper loginMapper;
  @Autowired LoginService loginService;
  @Autowired JwtProvider jwtProvider;
  @Autowired KISService kisService;



  // 로그인 메인 페이지 호출
  @RequestMapping("/login")
  public String getLoginPage(){return "login";}


  // 로그인 요청 api
  @RequestMapping(value="/api/userLogin", method = RequestMethod.POST)
  @ResponseBody
  public ResultDTO userLogin(@RequestBody LoginDTO loginData){

    // 사용자 로그인 확인
    ResultDTO loginResult = loginService.loginUser(loginData);

    // 로그인 성공+ KIS api 사용
    if (loginResult.getState() && loginData.getIsUseKisApi()) {
      // 토큰 발행하기
      ResultDTO tokenRes =   kisService.getKisToken(new KISTokenDTO(loginData.getUsername()));

      loginResult.setFailMsg(tokenRes.getFailMsg());
      loginResult.setState(tokenRes.getState());
    }

    return loginResult;
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
  public void delRefreshToken(@RequestHeader("Authorization") String authHeader, HttpServletRequest request){
    HttpSession session = request.getSession(false); // 있으면 가져오고, 없으면 null (새로 안 만듦)

    if (session != null) {
      session.invalidate();
    }

    String token = authHeader.substring(7);
    String username = jwtProvider.getUsernameFromToken(token);
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
