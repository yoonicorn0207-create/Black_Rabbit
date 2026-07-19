package com.blackrabbit.kis;

public class KISTokenDTO {
  private String username;
  private String appKey;
  private String secretKey;
  private String mockAccount;

  public KISTokenDTO(){};
  public KISTokenDTO(String username){ this.username = username;};
  public KISTokenDTO(String appKey, String secretKey){this.appKey = appKey; this.secretKey = secretKey;};
  public KISTokenDTO(String appKey, String secretKey, String mockAccount){this.appKey = appKey; this.secretKey = secretKey; this.mockAccount = mockAccount;};

  // getter/ setter
  public String getAppKey() {
    return appKey;
  }
  public void setAppKey(String appKey) {
    this.appKey = appKey;
  }
  public String getSecretKey() {
    return secretKey;
  }
  public void setSecretKey(String secretKey) {
    this.secretKey = secretKey;
  }
  public String getUsername() {
    return username;
  }
  public void setUsername(String username) {
    this.username = username;
  }
  public String getMockAccount() {
    return mockAccount;
  }
  public void setMockAccount(String mockAccount) {
    this.mockAccount = mockAccount;
  }
}
