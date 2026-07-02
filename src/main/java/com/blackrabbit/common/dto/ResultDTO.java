package com.blackrabbit.common.dto;

// 성공/ 실패 여부와 출력할 안내 문구용 DTO
public class ResultDTO<T> {
  private Boolean state; // true/ false
  private String failMsg; // 안내 메시지
  private T data; // 상황에 따라 리스트 또는 객체 추가 가능

  public ResultDTO(){}
  public ResultDTO(Boolean state){this.state = state;}
  public ResultDTO(Boolean state, String failMsg){this.state = state; this.failMsg = failMsg;}

  // getter/ setter
  public Boolean getState() {
    return state;
  }
  public void setState(Boolean state) {
    this.state = state;
  }
  public String getFailMsg() {
    return failMsg;
  }
  public void setFailMsg(String failMsg) {
    this.failMsg = failMsg;
  }
  public T getData(){return data;}
  public void setData(T data){this.data = data;}
}
