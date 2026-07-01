package com.blackrabbit.login;

import com.blackrabbit.common.dto.ResultDTO;

public interface LoginService {

  // 로그인
  ResultDTO loginUser(LoginDTO userData);

  // 로그아웃
  void logoutUser(LoginDTO userData);

  // 새 토큰 발급(refresh 가지고 새로운 access 발급)
  ResultDTO refreshAccessToken(String refreshToken);
}
