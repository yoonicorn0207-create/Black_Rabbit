package com.blackrabbit.kis;

import com.blackrabbit.common.dto.ResultDTO;

public interface KISService {

  // kis api 호출을 위한 유효기간 1일 token 발급 api
  // 회원가입 시 입력받은 appkey, secretkey가 유효한지 확인하기 위해 사용
  // 로그인 시 token 발급을 위해 사용
  ResultDTO getKisToken(KISTokenDTO kisTokenDTO);
}
