package com.blackrabbit.kis;

import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface KISMapper {

  // token 발급
  void upsertKisToken(KISTokenResDTO dto);
}
