package com.blackrabbit.signup;

import org.apache.ibatis.annotations.Mapper;

import java.util.Map;

@Mapper
public interface SignupMapper {
  // 회원가입을 위한 아이디/ 이메일 중복확인 로직
  int checkDup (String type, String value);

  // 회원가입
  int createUser(SignupDTO user);
}
