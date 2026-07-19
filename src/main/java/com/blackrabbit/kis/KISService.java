package com.blackrabbit.kis;

import com.blackrabbit.common.dto.ResultDTO;

public interface KISService {

  // kis api 호출을 위한 유효기간 1일 token 발급 api
  // 회원가입 시 입력받은 appkey, secretkey가 유효한지 확인하기 위해 사용
  // 로그인 시 token 발급을 위해 사용
  ResultDTO getKisToken(KISTokenDTO kisTokenDTO);


  // userid를 이용하여 username을 얻어온 뒤 kis appkey appsecret token 가져오기
  ResultDTO getAllKisToken(int userIdx);

  // kis api를 이용하여 사용자의 예수금/ 보유종목 가져오기
  ResultDTO getCashBalanceAndHoldings(int userIdx);

  // kis api를 이용하여 매수/매도하기
  ResultDTO buyAndSellByKis(int userIdx, KISOrderDTO order);
}
