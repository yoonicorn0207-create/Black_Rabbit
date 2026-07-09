package com.blackrabbit.stock;

public class MarketIndexDTO {
    private double kospi;
    private double kosdaq;
    private String collectedDate; // 혹은 LocalDateTime

    /* 생성자 영역 */

    /*기본 생성자*/
    public MarketIndexDTO() {
    }

    /* 매개변수 생성자 */
    public MarketIndexDTO(double kospi, double kosdaq, String collectedDate) {
        this.kospi = kospi;
        this.kosdaq = kosdaq;
        this.collectedDate = collectedDate;
    }

    /* Getter 영역 */
    public double getKospi() {
        return kospi;
    }

    public double getKosdaq() {
        return kosdaq;
    }

    public String getCollectedDate() {
        return collectedDate;
    }

    /* Setter 영역 */
    public void setKospi(double kospi) {
        this.kospi = kospi;
    }

    public void setKosdaq(double kosdaq) {
        this.kosdaq = kosdaq;
    }

    public void setCollectedDate(String collectedDate) {
        this.collectedDate = collectedDate;
    }


}//MarketIndexDTO(코스피 & 코스닥 DTO)
