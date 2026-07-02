package com.blackrabbit.signup;

import java.math.BigInteger;

public class SignupDTO {
  private String username;
  private String password;
  private String email;
  private BigInteger balance;

  public SignupDTO(){}
  public SignupDTO(String username, String password, String email, BigInteger balance){
    this.username = username;
    this.password = password;
    this.email = email;
    this.balance = balance;
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
}