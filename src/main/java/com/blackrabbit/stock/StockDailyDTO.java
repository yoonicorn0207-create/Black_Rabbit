package com.blackrabbit.stock;

public class StockDailyDTO {

    /* 변수영역 */
    private String stck_shrn_iscd; // 종목코드
    private String stck_bsop_date; // 날짜
    private double stck_oprc;      // 시가
    private double stck_hgpr;      // 최고가
    private double stck_lwpr;      // 최저가
    private double stck_clpr;      // 종가


    /* 생성자 영역 */
    /* 기본생성자 */
    public StockDailyDTO() {
    }

    /* 매개변수 생성자 */
    public StockDailyDTO(String stck_shrn_iscd, String stck_bsop_date, double stck_oprc, double stck_hgpr, double stck_lwpr, double stck_clpr) {
        this.stck_shrn_iscd = stck_shrn_iscd;
        this.stck_bsop_date = stck_bsop_date;
        this.stck_oprc = stck_oprc;
        this.stck_hgpr = stck_hgpr;
        this.stck_lwpr = stck_lwpr;
        this.stck_clpr = stck_clpr;
    }


    /* Getter 영역 */
    public String getStck_shrn_iscd() {
        return stck_shrn_iscd;
    }

    public String getStck_bsop_date() {
        return stck_bsop_date;
    }

    public double getStck_oprc() {
        return stck_oprc;
    }

    public double getStck_hgpr() {
        return stck_hgpr;
    }

    public double getStck_lwpr() {
        return stck_lwpr;
    }

    public double getStck_clpr() {
        return stck_clpr;
    }

    /* Setter 영역 */
    public void setStck_shrn_iscd(String stck_shrn_iscd) {
        this.stck_shrn_iscd = stck_shrn_iscd;
    }

    public void setStck_bsop_date(String stck_bsop_date) {
        this.stck_bsop_date = stck_bsop_date;
    }

    public void setStck_oprc(double stck_oprc) {
        this.stck_oprc = stck_oprc;
    }

    public void setStck_hgpr(double stck_hgpr) {
        this.stck_hgpr = stck_hgpr;
    }

    public void setStck_lwpr(double stck_lwpr) {
        this.stck_lwpr = stck_lwpr;
    }

    public void setStck_clpr(double stck_clpr) {
        this.stck_clpr = stck_clpr;
    }


}//stockDailyDTO(일별차트용 DTO) - 2026_0629 생성
