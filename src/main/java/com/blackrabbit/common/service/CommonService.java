package com.blackrabbit.common.service;

import com.blackrabbit.common.util.AESUtil;
import com.blackrabbit.signup.SignupMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Service;

@Service
public class CommonService {
  @Autowired private BCryptPasswordEncoder pwdEncoder;
  @Autowired private AESUtil aesUtil;
  @Autowired private SignupMapper signupMapper; // 매퍼는 공유해도 됩니다!

  // 1. 비밀번호 암호화
  public String encodePassword(String rawPwd) {
    return pwdEncoder.encode(rawPwd);
  }

  // 비밀번호 매치 여부 확인
  public boolean matchesPwd(String pwd, String checkPwd){
    return pwdEncoder.matches(pwd, checkPwd);
  }

  // 2. 키 암호화 (AES)
  public String encryptKey(String key) {
    try {
      return aesUtil.encrypt(key);
    } catch (Exception e) {
      throw new RuntimeException("암호화 실패", e);
    }
  }

  // 3. 중복 확인 공통 로직
  public boolean isDuplicate(String type, String value) {
    return signupMapper.checkDup(type, value) > 0;
  }
}
