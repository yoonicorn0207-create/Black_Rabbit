package com.blackrabbit.stock;

import java.math.BigDecimal;

public class UserHoldingStockDTO {


    private String stck_shrn_iscd;   // 종목 코드 (기본키 및 조인 키)
    private String stock_name;       // 종목명 (HC_stock_daily1 테이블에서 JOIN)
    private int total_quantity;      // 총 보유 수량 (HC_user_holdings에서 가져옴)
    private BigDecimal avg_buy_price;// 평균 매수 단가 (HC_user_holdings에서 가져옴)
    private BigDecimal current_price;// 현재가 (HC_stock_daily1 테이블에서 JOIN)
    private double profit_rate;      // 실시간 수익률 (쿼리 결과 계산값)

    /* 1. 기본 생성자 (MyBatis 등이 객체 생성 시 필요)*/
    public UserHoldingStockDTO() {
    }

    /* 2. 전체 필드 생성자 (필요 시 사용) */
    public UserHoldingStockDTO(String stck_shrn_iscd, String stock_name, int total_quantity,
                               BigDecimal avg_buy_price, BigDecimal current_price, double profit_rate) {
        this.stck_shrn_iscd = stck_shrn_iscd;
        this.stock_name = stock_name;
        this.total_quantity = total_quantity;
        this.avg_buy_price = avg_buy_price;
        this.current_price = current_price;
        this.profit_rate = profit_rate;
    }

    /* 3. Getter 및 Setter 메서드 */
    //Getter 영역
    public String getStck_shrn_iscd() {
        return stck_shrn_iscd;
    }

    public String getStock_name() {
        return stock_name;
    }

    public int getTotal_quantity() {
        return total_quantity;
    }

    public BigDecimal getAvg_buy_price() {
        return avg_buy_price;
    }

    public BigDecimal getCurrent_price() {
        return current_price;
    }

    public double getProfit_rate() {
        return profit_rate;
    }


    //Setter 영역
    public void setStck_shrn_iscd(String stck_shrn_iscd) {
        this.stck_shrn_iscd = stck_shrn_iscd;
    }

    public void setStock_name(String stock_name) {
        this.stock_name = stock_name;
    }

    public void setTotal_quantity(int total_quantity) {
        this.total_quantity = total_quantity;
    }

    public void setAvg_buy_price(BigDecimal avg_buy_price) {
        this.avg_buy_price = avg_buy_price;
    }

    public void setCurrent_price(BigDecimal current_price) {
        this.current_price = current_price;
    }

    public void setProfit_rate(double profit_rate) {
        this.profit_rate = profit_rate;
    }

}// UserHoldingStockDTO(회원 보유종목 DTO) - 20260630생성(yoonicorn)
