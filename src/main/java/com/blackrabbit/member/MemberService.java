package com.blackrabbit.member;

import com.blackrabbit.common.dto.ResultDTO;

public interface MemberService {

  // 현재 로그인한 사용자 패스워드 인증
  // 리턴값에 사용자 정보 필요한거 담아서 return해주기
  ResultDTO verifyPwd(MemberDTO memberDTO);

  // 사용자 정보 수정
  ResultDTO editUserInfo(MemberDTO memberDTO);
}
