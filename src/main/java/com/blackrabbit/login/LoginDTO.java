package com.blackrabbit.login;

public class LoginDTO {
  private String username;
  private String password;
  private boolean isUseKisApi;

  public LoginDTO(){};
  public LoginDTO(String username, String password){
    this.username = username;
    this.password=password;
  }
  public LoginDTO(String username, String password, Boolean isUseKisApi){
    this.username = username;
    this.password=password;
    this.isUseKisApi = isUseKisApi;
  }

  // getter/ setter
  public String getUsername() {return username;}
  public void setUsername(String username) {this.username = username;}
  public String getPassword() {return password;}
  public void setPassword(String password) {this.password = password;}
  public boolean getIsUseKisApi() {return isUseKisApi;}
  public void setIsUseKisApi(boolean isUseKisApi) {this.isUseKisApi = isUseKisApi;}
}
