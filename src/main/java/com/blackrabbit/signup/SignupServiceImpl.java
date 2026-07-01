package com.blackrabbit.signup;

import com.blackrabbit.common.dto.ResultDTO;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Service;

@Service("SignupService")
public class SignupServiceImpl implements SignupService {

  @Autowired
  private SignupMapper signupMapper;
  @Autowired
  private BCryptPasswordEncoder pwdEncoder;

  @Override
  public ResultDTO checkDup(String type, String value){
    int cnt =  signupMapper.checkDup(type,value);

    String fieldName = "id".equals(type) ? "아이디" : "이메일";
    String resultTxt = cnt != 0 ? "이미 사용 중인 " :"사용 가능한 ";

    ResultDTO res = new ResultDTO();
    res.setState(cnt == 0 );
    res.setFailMsg( resultTxt + fieldName + "입니다.");

    return res;
  }

  @Override
  public ResultDTO createUser(SignupDTO user){
    ResultDTO res = new ResultDTO();


    // 회원가입 진행 전 존재 아이디/ 이메일 여부 한번 더 체킹
    // 중복 확인용 api가 존재하지만 해당 api내에서도 유효성 검사를 진행한다
    ResultDTO dupId= checkDup("id", user.getUsername());
    if (!dupId.getState()) {
      return dupId;
    }
    ResultDTO dupEmail = checkDup("email", user.getEmail());
    if (!dupEmail.getState()) {
      return dupEmail;
    }


    // 비밀번호 해시처리 선행- BCrypto 사용한다
    String rawPwd = user.getPassword();
    String encodedPwd = pwdEncoder.encode(rawPwd);
    user.setPassword(encodedPwd);

    int cnt =  signupMapper.createUser(user);

    if(cnt == 1){
      // 성공
      res.setState(true);
      res.setFailMsg("회원가입을 성공하였습니다. 로그인 해주세요.");
    }else{
      // 실패
      res.setState(false);
      res.setFailMsg("회원가입에 실패했습니다. 관리자에게 문의 바랍니다.");
    }

    return res;
  }
}
