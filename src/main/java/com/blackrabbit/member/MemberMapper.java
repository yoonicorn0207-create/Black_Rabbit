package com.blackrabbit.member;

import org.apache.ibatis.annotations.Mapper;

import java.util.Map;

@Mapper
public interface MemberMapper {

  // pwd 인증 후 사용자 정보 받아오기
  Map<String, String> verifyPwd (MemberDTO memberDTO);

  // 사용자 정보 수정or 등록or 삭제하기
  int updateUserInfo(MemberDTO memberDTO);
}
