package com.blackrabbit.signup;

import com.blackrabbit.common.dto.ResultDTO;
import com.blackrabbit.common.util.AESUtil;
import com.blackrabbit.kis.KISMapper;
import com.blackrabbit.kis.KISTokenResDTO;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;

@Service("SignupService")
public class SignupServiceImpl implements SignupService {

  @Autowired private KISMapper kisMapper;
  @Autowired private SignupMapper signupMapper;
  @Autowired private BCryptPasswordEncoder pwdEncoder;
  @Autowired private AESUtil aesUtil;

  @Override
  public ResultDTO checkDup(String type, String value){
    // 아이디/ 이메일 중복확인
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
    // 회원가입 확인
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



    // kis 계좌번호&& appkey&& secretkey 존재 시 암호화 사용
    if(user.getTokenData() != null){

      try {
        String enAppKey = encryptKey(user.getAppKey());
        String enSecretKey = encryptKey(user.getAppSecret());

        System.out.println("암호화 결과 길이: " + enSecretKey.length());

        user.setAppKey(enAppKey);
        user.setAppSecret(enSecretKey);

      } catch (Exception e) {
        throw new RuntimeException(e);
      }
    }


    int cnt =  signupMapper.createUser(user);


    if(cnt == 1){
      // 아 여기서 userId에 값 넣어줘야함;
      int userId = kisMapper.getUserIdxByUsername(user.getUsername());

      KISTokenResDTO tokenData = user.getTokenData();
      tokenData.setUserId(userId);

      int saveToken = kisMapper.upsertKisToken(tokenData);

      if(saveToken >= 1){
        res.setState(true);
        res.setFailMsg("회원가입을 성공하였습니다. 로그인 해주세요.");
      }else{
        // 실패
        res.setState(false);
        res.setFailMsg("회원가입에 실패했습니다. 관리자에게 문의 바랍니다.");
      }

    }else{
      // 실패
      res.setState(false);
      res.setFailMsg("회원가입에 실패했습니다. 관리자에게 문의 바랍니다.");
    }

    return res;
  }

  private String encryptKey(String key) throws Exception {
     return aesUtil.encrypt(key);
  }

  private boolean isAllFieldsPresent(SignupDTO user) {
    if (user == null) return false;

    // 3개 필드가 모두 null이 아니고, 공백 문자가 아닌 문자가 하나라도 포함되어 있는지 확인
    return StringUtils.hasText(user.getMockAccount()) &&
        StringUtils.hasText(user.getAppKey()) &&
        StringUtils.hasText(user.getAppSecret());
  }
}
