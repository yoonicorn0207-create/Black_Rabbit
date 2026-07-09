package com.blackrabbit.kis;

public class KISTokenResDTO {
  private int userId;
  public String access_token;
  public String token_type;
  public long expires_at;
  public String access_token_token_expired;

  public KISTokenResDTO() {}
  public KISTokenResDTO(int userId, String access_token, String token_type, long expires_at, String access_token_token_expired) {
    this.userId = userId;
    this.access_token = access_token;
    this.token_type = token_type;
    this.expires_at = expires_at;
    this.access_token_token_expired = access_token_token_expired;
  }

  public void setUserId(int userId) { this.userId = userId; }
  public int getUserId() { return userId; }

  public String getAccess_token() {
    return access_token;
  }

  public void setAccess_token(String access_token) {
    this.access_token = access_token;
  }

  public String getToken_type() {
    return token_type;
  }

  public void setToken_type(String token_type) {
    this.token_type = token_type;
  }

  public long getExpires_at() {
    return expires_at;
  }

  public void setExpires_at(long expires_at) {
    this.expires_at = expires_at;
  }

  public String getAccess_token_token_expired() {
    return access_token_token_expired;
  }

  public void setAccess_token_token_expired(String access_token_token_expired) {
    this.access_token_token_expired = access_token_token_expired;
  }
}
