package com.blackrabbit.stock;

import java.util.List;

public class StockListResDTO {
  private List<StockDTO> list;
  private int total;

  public StockListResDTO(List<StockDTO> list, int total) {
    this.list = list;
    this.total = total;
  }

  public List<StockDTO> getList() { return list; }
  public void setList(List<StockDTO> list) { this.list = list; }

  public int getTotal() { return total; }
  public void setTotal(int total) { this.total = total; }
}
