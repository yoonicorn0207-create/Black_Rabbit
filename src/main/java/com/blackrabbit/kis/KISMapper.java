package com.blackrabbit.kis;

import org.apache.ibatis.annotations.Mapper;

import java.util.Optional;

@Mapper
public interface KISMapper {

  // token 발급
  int upsertKisToken(KISTokenResDTO dto);

  // 저장해둔 key 가져오기
  // Optional사용 시 null 값 명시적 반환 가능해짐
  Optional <KISTokenDTO> getKisApiKey(KISTokenDTO dto);

  int getUserIdxByUsername(String username);
}
