package com.blackrabbit.kis;

public class KISOrderDTO {
  private String stockCode; // 종목코드
  private int quantity;     // 수량
  private String orderType; // "BUY" 또는 "SELL"

  public KISOrderDTO(){}
  public KISOrderDTO(String stockCode, int quantity, String orderType) {
    this.stockCode = stockCode;
    this.quantity = quantity;
    this.orderType = orderType;
  }

  public String getStockCode() {
    return stockCode;
  }

  public void setStockCode(String stockCode) {
    this.stockCode = stockCode;
  }

  public int getQuantity() {
    return quantity;
  }

  public void setQuantity(int quantity) {
    this.quantity = quantity;
  }

  public String getOrderType() {
    return orderType;
  }

  public void setOrderType(String orderType) {
    this.orderType = orderType;
  }
}
