package com.blackrabbit.common.util;

import io.jsonwebtoken.Jwt;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import java.util.Date;

@Component
public class JwtProvider {
  // 토큰 서명을 위해 서버가 사용하는 비밀 키
  @Value("${jwt.secret.key}")
  private String SECRET_KEY;

  // 1. 액세스 토큰 생성
  public String createAccessToken(String username, boolean isUseKis) {
    return Jwts.builder()
        .setSubject(username)
        .claim("isUseKis", isUseKis)
        .setIssuedAt(new Date())
        .setExpiration(new Date(System.currentTimeMillis() + 1000 * 60 * 60 * 24 * 7)) // 30분(이게 기본임): 1000 * 60 * 30
        .signWith(Keys.hmacShaKeyFor(SECRET_KEY.getBytes()))
        .compact();
  }

  // 2. 리프레시 토큰 생성
  public String createRefreshToken(String username, boolean isUseKis) {
    return Jwts.builder()
        .setSubject(username)
        .claim("isUseKis", isUseKis)
        .setExpiration(new Date(System.currentTimeMillis() + 1000 * 60 * 60 * 24 * 7)) // 1주일
        .signWith(Keys.hmacShaKeyFor(SECRET_KEY.getBytes()))
        .compact();
  }

  // 토큰 검증 (만료 여부 확인)
  public boolean validateToken(String token) {
    try {
      Jwts.parserBuilder().setSigningKey(Keys.hmacShaKeyFor(SECRET_KEY.getBytes())).build()
          .parseClaimsJws(token);
      return true;
    } catch (Exception e) {
      return false;
    }
  }

  // 토큰에서 username 뽑아내기
  public String getUsernameFromToken(String token) {
    return Jwts.parserBuilder().setSigningKey(Keys.hmacShaKeyFor(SECRET_KEY.getBytes())).build()
        .parseClaimsJws(token).getBody().getSubject();
  }

  // 토큰에서 isUseKis 정보 뽑아내기
  public boolean getIsUseKisFromToken(String token) {
    return Jwts.parserBuilder()
        .setSigningKey(Keys.hmacShaKeyFor(SECRET_KEY.getBytes())).build()
        .parseClaimsJws(token).getBody().get("isUseKis", Boolean.class);
  }

}
