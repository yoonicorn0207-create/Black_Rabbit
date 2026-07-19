package com.blackrabbit.member;

import com.blackrabbit.common.dto.ResultDTO;
import com.blackrabbit.common.service.CommonService;
import com.blackrabbit.kis.KISService;
import com.blackrabbit.kis.KISTokenDTO;
import com.blackrabbit.kis.KISTokenResDTO;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.Map;

@Service("MemberService")
public class MemberServiceImpl implements MemberService {

  @Autowired MemberMapper memberMapper;
  @Autowired CommonService commonService;
  @Autowired KISService kisService;

  // 사용자 패스워드 받아서 인증 성공 시 사용자 정보 return
  @Override
  public ResultDTO verifyPwd(MemberDTO memberDTO){

    ResultDTO dto = new ResultDTO<>();

    Map<String, String> res = memberMapper.verifyPwd(memberDTO);

    if(res == null || !commonService.matchesPwd(
        memberDTO.getPassword(), res.get("password_hash")
    )) {
      dto.setState(false);
      dto.setFailMsg("패스워드 인증에 실패하였습니다.");

      return dto;
    }

    res.remove("password_hash");

    dto.setData(res);
    dto.setState(true);
    dto.setFailMsg("인증 성공");

    return dto;
  }

  // 사용자 입력값 가지고 수정 진행
  @Override
  public ResultDTO editUserInfo(MemberDTO memberDTO){

    ResultDTO dto = new ResultDTO<>();

    // 사용자가 email 수정 요청 시- 중복확인 진행
    boolean isDup = commonService.isDuplicate("email", memberDTO.getEmail());

    if(!isDup){
      dto.setState(isDup);
      dto.setFailMsg("이미 사용중인 이메일입니다.");

      return dto;
    }


    // kis 데이터 존재 시 암호화+ 사용 가능 데이터인지 hashtoken 발급해보기
    if(memberDTO.getAppSecret() != null && memberDTO.getAppSecret() != ""){
      KISTokenDTO kisDto = new KISTokenDTO();

//      kisDto.setUsername(memberDTO.getUsername());
      kisDto.setAppKey(memberDTO.getAppKey());
      kisDto.setSecretKey(memberDTO.getAppSecret());
      kisDto.setMockAccount(memberDTO.getMockAccount());

      ResultDTO tokenRes = kisService.getKisToken(kisDto);

      if(!tokenRes.getState()){
        dto.setState(false);
        dto.setFailMsg("올바르지 않은 한국투자증권 appkey 또는 secretkey 입니다.");

        return dto;
      }
    }

    // upsert 전 데이터 암호화 진행
    memberDTO.setAppKey(
        commonService.encryptKey(
            memberDTO.getAppKey()
        )
    );
    memberDTO.setAppSecret(
        commonService.encryptKey(
            memberDTO.getAppSecret()
        )
    );

    int res = memberMapper.updateUserInfo(memberDTO);

    if(res == 1){
      dto.setState(true);
      dto.setFailMsg("회원 정보 수정에 성공하였습니다. 다시 로그인해주세요.");
    }else{
      dto.setState(false);
      dto.setFailMsg("회원 정보 수정에 실패하였습니다. 관리자에게 문의해주세요.");
    }

    return dto;
  }
}
