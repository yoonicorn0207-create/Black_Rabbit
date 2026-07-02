package com.blackrabbit.stock;

public class StockDTO {

    private String stck_shrn_iscd;   // 주식 단축 종목코드
    private String hts_kor_isnm;     // HTS 한글 종목명

    // 가격 정보
    private String stck_prpr;        // 주식 현재가
    private String stck_oprc;        // 주식 시가
    private String stck_hgpr;        // 주식 최고가
    private String stck_lwpr;        // 주식 최저가
    private String stck_prdy_clpr;   // 주식 전일 종가


    // 등락 정보
    private String prdy_vrss;        // 전일 대비
    private String prdy_vrss_sign;   // 전일 대비 부호
    private String prdy_ctrt;        // 전일 대비율


    // 거래량/대금 정보
    private String acml_vol;         // 누적 거래량
    private String acml_tr_pbmn;     // 누적 거래 대금
    private String prdy_vol;         // 전일 거래량
    private String prdy_vrss_vol;    // 전일 대비 거래량
    private String vol_tnrt;         // 거래량 회전율


    // 전일 기록
    private String stck_prdy_oprc;   // 주식 전일 시가
    private String stck_prdy_hgpr;   // 주식 전일 최고가
    private String stck_prdy_lwpr;   // 주식 전일 최저가


    // 호가 정보
    private String askp;             // 매도호가
    private String bidp;             // 매수호가

    // 기타 상세 정보
    private String stck_mxpr;        // 주식 상한가
    private String stck_llam;        // 주식 하한가
    private String stck_fcam;        // 주식 액면가
    private String lstn_stcn;        // 상장 주수
    private String cpfn;             // 자본금
    private String hts_avls;         // HTS 시가총액


    // 지표
    private String per;              // PER
    private String eps;              // EPS
    private String pbr;              // PBR
    private String itewhol_loan_rmnd_ratem; // 전체 융자 잔고 비율


    /* 생성자 영역 */
    public StockDTO() {}

    public StockDTO(String stck_shrn_iscd) {
        this.stck_shrn_iscd = stck_shrn_iscd;
    }


    public StockDTO(String stck_shrn_iscd, String hts_kor_isnm, String stck_prpr, String stck_oprc, String stck_hgpr, String stck_lwpr, String stck_prdy_clpr, String prdy_vrss, String prdy_vrss_sign, String prdy_ctrt, String acml_vol, String acml_tr_pbmn, String prdy_vol, String prdy_vrss_vol, String vol_tnrt, String stck_prdy_oprc, String stck_prdy_hgpr, String stck_prdy_lwpr, String askp, String bidp, String stck_mxpr, String stck_llam, String stck_fcam, String lstn_stcn, String cpfn, String hts_avls, String per, String eps, String pbr, String itewhol_loan_rmnd_ratem) {
        this.stck_shrn_iscd = stck_shrn_iscd;
        this.hts_kor_isnm = hts_kor_isnm;
        this.stck_prpr = stck_prpr;
        this.stck_oprc = stck_oprc;
        this.stck_hgpr = stck_hgpr;
        this.stck_lwpr = stck_lwpr;
        this.stck_prdy_clpr = stck_prdy_clpr;
        this.prdy_vrss = prdy_vrss;
        this.prdy_vrss_sign = prdy_vrss_sign;
        this.prdy_ctrt = prdy_ctrt;
        this.acml_vol = acml_vol;
        this.acml_tr_pbmn = acml_tr_pbmn;
        this.prdy_vol = prdy_vol;
        this.prdy_vrss_vol = prdy_vrss_vol;
        this.vol_tnrt = vol_tnrt;
        this.stck_prdy_oprc = stck_prdy_oprc;
        this.stck_prdy_hgpr = stck_prdy_hgpr;
        this.stck_prdy_lwpr = stck_prdy_lwpr;
        this.askp = askp;
        this.bidp = bidp;
        this.stck_mxpr = stck_mxpr;
        this.stck_llam = stck_llam;
        this.stck_fcam = stck_fcam;
        this.lstn_stcn = lstn_stcn;
        this.cpfn = cpfn;
        this.hts_avls = hts_avls;
        this.per = per;
        this.eps = eps;
        this.pbr = pbr;
        this.itewhol_loan_rmnd_ratem = itewhol_loan_rmnd_ratem;
    }

    /* Getter영역 */
    public String getStck_shrn_iscd() {
        return stck_shrn_iscd;
    }

    public String getHts_kor_isnm() {
        return hts_kor_isnm;
    }

    public String getStck_prpr() {
        return stck_prpr;
    }

    public String getStck_oprc() {
        return stck_oprc;
    }

    public String getStck_hgpr() {
        return stck_hgpr;
    }

    public String getStck_lwpr() {
        return stck_lwpr;
    }

    public String getStck_prdy_clpr() {
        return stck_prdy_clpr;
    }

    public String getPrdy_vrss() {
        return prdy_vrss;
    }

    public String getPrdy_vrss_sign() {
        return prdy_vrss_sign;
    }

    public String getPrdy_ctrt() {
        return prdy_ctrt;
    }

    public String getAcml_vol() {
        return acml_vol;
    }

    public String getAcml_tr_pbmn() {
        return acml_tr_pbmn;
    }

    public String getPrdy_vol() {
        return prdy_vol;
    }

    public String getPrdy_vrss_vol() {
        return prdy_vrss_vol;
    }

    public String getVol_tnrt() {
        return vol_tnrt;
    }

    public String getStck_prdy_oprc() {
        return stck_prdy_oprc;
    }

    public String getStck_prdy_hgpr() {
        return stck_prdy_hgpr;
    }

    public String getStck_prdy_lwpr() {
        return stck_prdy_lwpr;
    }

    public String getAskp() {
        return askp;
    }

    public String getBidp() {
        return bidp;
    }

    public String getStck_mxpr() {
        return stck_mxpr;
    }

    public String getStck_llam() {
        return stck_llam;
    }

    public String getStck_fcam() {
        return stck_fcam;
    }

    public String getLstn_stcn() {
        return lstn_stcn;
    }

    public String getCpfn() {
        return cpfn;
    }

    public String getHts_avls() {
        return hts_avls;
    }

    public String getPer() {
        return per;
    }

    public String getEps() {
        return eps;
    }

    public String getPbr() {
        return pbr;
    }

    public String getItewhol_loan_rmnd_ratem() {
        return itewhol_loan_rmnd_ratem;
    }


    /* Setter 영역 */
    public void setStck_shrn_iscd(String stck_shrn_iscd) {
        this.stck_shrn_iscd = stck_shrn_iscd;
    }

    public void setHts_kor_isnm(String hts_kor_isnm) {
        this.hts_kor_isnm = hts_kor_isnm;
    }

    public void setStck_prpr(String stck_prpr) {
        this.stck_prpr = stck_prpr;
    }

    public void setStck_oprc(String stck_oprc) {
        this.stck_oprc = stck_oprc;
    }

    public void setStck_hgpr(String stck_hgpr) {
        this.stck_hgpr = stck_hgpr;
    }

    public void setStck_lwpr(String stck_lwpr) {
        this.stck_lwpr = stck_lwpr;
    }

    public void setStck_prdy_clpr(String stck_prdy_clpr) {
        this.stck_prdy_clpr = stck_prdy_clpr;
    }

    public void setPrdy_vrss(String prdy_vrss) {
        this.prdy_vrss = prdy_vrss;
    }

    public void setPrdy_vrss_sign(String prdy_vrss_sign) {
        this.prdy_vrss_sign = prdy_vrss_sign;
    }

    public void setPrdy_ctrt(String prdy_ctrt) {
        this.prdy_ctrt = prdy_ctrt;
    }

    public void setAcml_vol(String acml_vol) {
        this.acml_vol = acml_vol;
    }

    public void setAcml_tr_pbmn(String acml_tr_pbmn) {
        this.acml_tr_pbmn = acml_tr_pbmn;
    }

    public void setPrdy_vol(String prdy_vol) {
        this.prdy_vol = prdy_vol;
    }

    public void setPrdy_vrss_vol(String prdy_vrss_vol) {
        this.prdy_vrss_vol = prdy_vrss_vol;
    }

    public void setVol_tnrt(String vol_tnrt) {
        this.vol_tnrt = vol_tnrt;
    }

    public void setStck_prdy_oprc(String stck_prdy_oprc) {
        this.stck_prdy_oprc = stck_prdy_oprc;
    }

    public void setStck_prdy_hgpr(String stck_prdy_hgpr) {
        this.stck_prdy_hgpr = stck_prdy_hgpr;
    }

    public void setStck_prdy_lwpr(String stck_prdy_lwpr) {
        this.stck_prdy_lwpr = stck_prdy_lwpr;
    }

    public void setAskp(String askp) {
        this.askp = askp;
    }

    public void setBidp(String bidp) {
        this.bidp = bidp;
    }

    public void setStck_mxpr(String stck_mxpr) {
        this.stck_mxpr = stck_mxpr;
    }

    public void setStck_llam(String stck_llam) {
        this.stck_llam = stck_llam;
    }

    public void setStck_fcam(String stck_fcam) {
        this.stck_fcam = stck_fcam;
    }

    public void setLstn_stcn(String lstn_stcn) {
        this.lstn_stcn = lstn_stcn;
    }

    public void setCpfn(String cpfn) {
        this.cpfn = cpfn;
    }

    public void setHts_avls(String hts_avls) {
        this.hts_avls = hts_avls;
    }

    public void setPer(String per) {
        this.per = per;
    }

    public void setEps(String eps) {
        this.eps = eps;
    }

    public void setPbr(String pbr) {
        this.pbr = pbr;
    }

    public void setItewhol_loan_rmnd_ratem(String itewhol_loan_rmnd_ratem) {
        this.itewhol_loan_rmnd_ratem = itewhol_loan_rmnd_ratem;
    }
}// StockDTO (2026_0626 수정)
