package com.blackrabbit.login;

import com.blackrabbit.common.dto.ResultDTO;
import com.blackrabbit.common.util.JwtProvider;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.web.context.request.RequestContextHolder;
import org.springframework.web.context.request.ServletRequestAttributes;


import javax.servlet.http.HttpSession;
import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.HashMap;
import java.util.Map;

@Service("LoginService")
public class LoginServiceImpl implements LoginService {

  @Autowired
  private LoginMapper loginMapper;
  @Autowired
  private BCryptPasswordEncoder pwdEncoder;
  @Autowired
  private JwtProvider jwtProvider;

  // 사용자 로그인 처리
  @Override
  public ResultDTO loginUser(LoginDTO userData){

    ResultDTO res = new ResultDTO();

    // 값 유효성 검사
    if(userData.getUsername() == null || userData.getPassword() == null){
      res.setState(false);
      res.setFailMsg("아이디 또는 패스워드를 입력해주세요.");
      return res;
    }

    // 아이디 존재 여부 확인
    Map<String, String> dbRes = loginMapper.loginUser(userData);


    if(dbRes == null){
      res.setState(false);
      res.setFailMsg("로그인에 실패하였습니다. 아이디 또는 패스워드를 확인해주세요.");

      return res;
    }

    // 패스워드 일치 여부 확인
    if(!pwdEncoder.matches(userData.getPassword(), dbRes.get("password_hash"))){
      res.setState(false);
      res.setFailMsg("로그인에 실패하였습니다. 아이디 또는 패스워드를 확인해주세요.");

      return res;
    }

     // 사용자 상태 확인
    // ACTIVE 로그인 성공처리
    // INACTIVE 휴면계정
    // SUSPENDED 정지된 계정
    // DELETED 삭제된 계정
    switch(dbRes.get("status")){
      case "INACTIVE":
        res.setState(false);
        res.setFailMsg("장기 미접속으로 휴면 전환된 계정입니다. 관리자에게 문의하세요.");
        return res;
      case "SUSPENDED":
        res.setState(false);
        res.setFailMsg("사용 정지된 계정입니다. 관리자에게 문의해주세요");
        return res;
      case "DELETED":
        res.setState(false);
        res.setFailMsg("존재하지 않는 계정입니다.아이디 또는 패스워드를 확인해주세요"); // 문구 협의 필요
        return res;
      default:
        break;
    }

    // 사용자의 최근 접속일이 30일 초과일 경우 강제 휴면처리 및 로그인 실패 진행
    // 다만 이 방식은 로그인을 시도한 아이디가 아닐 경우엔 잡아내지 못하므로
    // 추후 db batch 로직 추가 및 마이그레이션 필요
    Object lastLoginObj = dbRes.get("last_login_at");

    if (lastLoginObj != null) {
      LocalDateTime lastLogin = ((java.sql.Timestamp) lastLoginObj).toLocalDateTime();
      LocalDateTime now = LocalDateTime.now();

      if (ChronoUnit.DAYS.between(lastLogin, now) >= 30) {
        loginMapper.updateStatusToInactive(userData.getUsername());

        res.setState(false);
        res.setFailMsg("장기 미접속으로 휴면 전환된 계정입니다. 관리자에게 문의하세요.");

        return res;
      }
    }

    // 로그인 성공
    // 세션에 로그인 성공 사용자 idx 저장
    String userId = String.valueOf(dbRes.get("id")); // 세션 저장용 idx
    ServletRequestAttributes attr = (ServletRequestAttributes) RequestContextHolder.currentRequestAttributes();
    HttpSession session = attr.getRequest().getSession(true); // 세션이 없으면 새로 생성
    session.setAttribute("userId", userId);

    // token 발행 진행
    String username = userData.getUsername();
    String accessToken = jwtProvider.createAccessToken(username);
    String refreshToken = jwtProvider.createRefreshToken(username);


    // 토큰 저장하기
    loginMapper.saveOrUpdateRToken(username, refreshToken);

    // 최근 로그인 시간 업데이트
    loginMapper.updateLastLogin(username);

    // 발급 및 저장 완료된 토큰 프론트에 전달
    Map<String, String> data = new HashMap<>();
    data.put("accessToken", accessToken);
    data.put("refreshToken", refreshToken); // 프론트가 보관하게 전달
    data.put("userId", String.valueOf(dbRes.get("id"))); // 타입 주의!
    res.setState(true);
    res.setData(data);

    return res;
  }

  // 새 토큰 발급
  @Override
  public ResultDTO refreshAccessToken(String refreshToken) {
    ResultDTO res = new ResultDTO();

    // 1. 토큰 유효성 검증- refresh 토큰의 만료
    if (!jwtProvider.validateToken(refreshToken)) {
      res.setState(false);
      res.setFailMsg("로그인이 만료 되었습니다. 다시 로그인해주세요.");
      return res;
    }

    // 2. DB에 존재하는 토큰인지 확인
    String dbToken = loginMapper.getRToken(refreshToken);
    if (dbToken == null) {
      res.setState(false);
      res.setFailMsg("정상적이지 않은 로그인 입니다. 다시 로그인해주세요.");
      return res;
    }

    // 3. 새 액세스 토큰 발급
    String username = jwtProvider.getUsernameFromToken(refreshToken);
    String newAccessToken = jwtProvider.createAccessToken(username);

    // 4. 프론트에서 새 토큰을 저장할 수 있도록 반환
    Map<String, String> data = new HashMap<>();

    data.put("accessToken", newAccessToken);
    res.setState(true);
    res.setData(data);

    return res;
  }

  // 정상 로그아웃 시 저장된 refresh 토큰 삭제
  @Override
  public void logoutUser(String username){

    loginMapper.deleteRToken(username);
  }
}
