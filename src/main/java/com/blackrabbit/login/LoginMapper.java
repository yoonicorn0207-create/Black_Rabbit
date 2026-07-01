package com.blackrabbit.login;

import com.blackrabbit.common.dto.ResultDTO;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.Map;

@Mapper
public interface LoginMapper {

  // 로그인
  Map<String, String> loginUser(LoginDTO userData);

  // 최근 로그인 시점 업데이트
  void updateLastLogin(String username);

  // 사용자 계정 휴면 전환
  void updateStatusToInactive(String username);

  // 토큰 저장
  int saveOrUpdateRToken(@Param("username") String username, @Param("refreshToken") String refreshToken);

  // 토큰 조회
  String getRToken(String refreshToken);

  // 로그아웃- 저장 토큰 삭제
  void deleteRToken(String username);
}
