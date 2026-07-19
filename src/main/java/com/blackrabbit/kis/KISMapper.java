package com.blackrabbit.kis;

import org.apache.ibatis.annotations.Mapper;

import java.util.Optional;

@Mapper
public interface KISMapper {

  // token upsert
  int upsertKisToken(KISTokenResDTO dto);


  // token 가져오기 -> user idx 이용
  KISTokenResDTO getKisApiToken(int idx);


  // app key/ secret key 가져오기 -> username 이용
  // Optional사용 시 null 값 명시적 반환 가능해짐
  Optional <KISTokenDTO> getKisApiKey(KISTokenDTO dto);


  // username -> useridx
  int getUserIdxByUsername(String username);

  // useridx -> username
  String getUsernameByUserIdx(int id);
}
