package com.blackrabbit.kis;

public class KISTokenDTO {
  private String kisAppKey;
  private String kisSecretKey;

  public KISTokenDTO(){};
  public KISTokenDTO(String kisAppKey, String kisSecretKey){this.kisAppKey = kisAppKey; this.kisSecretKey = kisSecretKey;};

  // getter/ setter
  public String getKisAppKey() {
    return kisAppKey;
  }

  public void setKisAppKey(String kisAppKey) {
    this.kisAppKey = kisAppKey;
  }

  public String getKisSecretKey() {
    return kisSecretKey;
  }

  public void setKisSecretKey(String kisSecretKey) {
    this.kisSecretKey = kisSecretKey;
  }
}
