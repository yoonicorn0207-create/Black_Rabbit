package com.blackrabbit.signup;

import com.blackrabbit.common.dto.ResultDTO;

public interface SignupService {

  // 회원가입 전 id/ email 중복 확인
  // true/ false
  // failMsg
  ResultDTO checkDup(String type, String value);

  // 회원가입
  // true/ false
  // failMsg
  ResultDTO createUser(SignupDTO user);
}
