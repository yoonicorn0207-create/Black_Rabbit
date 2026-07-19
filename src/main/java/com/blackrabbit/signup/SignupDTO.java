package com.blackrabbit.signup;

import com.blackrabbit.kis.KISTokenResDTO;

import java.math.BigInteger;

public class SignupDTO {
  private String username;
  private String password;
  private String email;
  private BigInteger balance;
  // kis
  private String mockAccount;
  private String appKey;
  private String appSecret;
  private KISTokenResDTO tokenData;

  public SignupDTO(){}
  public SignupDTO(String username, String password, String email, BigInteger balance){
    this.username = username;
    this.password = password;
    this.email = email;
    this.balance = balance;
  }
  public SignupDTO(String username,
                   String password,
                   String email,
                   BigInteger balance,
                   String mockAccount,
                   String appKey,
                   String appSecret){
    this.username = username;
    this.password = password;
    this.email = email;
    this.balance = balance;
    this.mockAccount = mockAccount;
    this.appKey = appKey;
    this.appSecret = appSecret;
  }

  /* getter/ setter */
  public String getUsername() {
    return username;
  }
  public void setUsername(String username) {
    this.username = username;
  }
  public String getPassword() {
    return password;
  }
  public void setPassword(String password) {
    this.password = password;
  }
  public String getEmail() {
    return email;
  }
  public void setEmail(String email) {
    this.email = email;
  }
  public BigInteger getBalance() {
    return balance;
  }
  public void setBalance(BigInteger balance) {
    this.balance = balance;
  }

  // kis
  public String getMockAccount() {
    return mockAccount;
  }
  public void setMockAccount(String mockAccount) {
    this.mockAccount = mockAccount;
  }
  public String getAppKey() {
    return appKey;
  }
  public void setAppKey(String appKey) {
    this.appKey = appKey;
  }
  public String getAppSecret() {
    return appSecret;
  }
  public void setAppSecret(String appSecret) {
    this.appSecret = appSecret;
  }
  public KISTokenResDTO getTokenData() { return tokenData; }
  public void setTokenData(KISTokenResDTO tokenData) { this.tokenData = tokenData; }
}