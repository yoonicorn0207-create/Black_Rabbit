package com.blackrabbit.kis;

public class KISTokenDTO {
  private String appKey;
  private String secretKey;

  public KISTokenDTO(){};
  public KISTokenDTO(String appKey, String secretKey){this.appKey = appKey; this.secretKey = secretKey;};

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
}
