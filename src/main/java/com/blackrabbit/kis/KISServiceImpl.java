package com.blackrabbit.kis;

import com.blackrabbit.common.dto.ResultDTO;
import com.blackrabbit.common.util.AESUtil;
import com.blackrabbit.member.MemberDTO;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpHeaders;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.time.LocalDateTime;
import java.util.*;

@Service("KISService")
public class KISServiceImpl implements KISService {

  @Autowired private KISMapper kisMapper;
  @Autowired private AESUtil aesUtil;

  private final HttpClient httpClient = HttpClient.newHttpClient();
  private final ObjectMapper objectMapper = new ObjectMapper();
  private final String url = "https://openapivts.koreainvestment.com:29443";
  private final String contentType = "application/json";
  private final String contentType_utf8 = "application/json; charset=utf-8";


  // ▼ 추가: KIS 초당 호출 제한 방지용
  private static final long MIN_CALL_INTERVAL_MS = 600; // 초당 약 1.6건으로 제한
  private long lastKisCallTime = 0;


  private synchronized void throttleKisCall() {
    long now = System.currentTimeMillis();
    long elapsed = now - lastKisCallTime;
    if (elapsed < MIN_CALL_INTERVAL_MS) {
      try {
        Thread.sleep(MIN_CALL_INTERVAL_MS - elapsed);
      } catch (InterruptedException e) {
        Thread.currentThread().interrupt();
      }
    }
    lastKisCallTime = System.currentTimeMillis();
  }


  @Override
  public ResultDTO getKisToken(KISTokenDTO kisTokenDTO) {
    // 한투 api 호출용 토큰 발급받기
    // 로그인/ 회원가입 두가지 경우에서 사용되는 함수이며
    // kisTokenDTO 안에 username=id의 존재 유무로 로그인/ 회원가입 분기 판단

    // username 존재: 로그인
    if (StringUtils.hasText(kisTokenDTO.getUsername())) {
      // null이 아니고, 길이가 0보다 크고, 공백 문자가 아닌 문자가 하나라도 포함되어 있을 때 true
      // db에서 key 뽑아오기 -> decrypt
      Optional<KISTokenDTO> dbInfo = kisMapper.getKisApiKey(kisTokenDTO);

      if (dbInfo.isPresent()) {
        KISTokenDTO data = dbInfo.get();
        try {
          kisTokenDTO.setAppKey(aesUtil.decrypt(data.getAppKey()));
          kisTokenDTO.setSecretKey(aesUtil.decrypt(data.getSecretKey()));
        } catch (Exception e) {
          e.printStackTrace();
          return new ResultDTO(false, "복호화 중 오류가 발생했습니다.");
        }

      } else {
        return new ResultDTO(false, "등록된 KIS 계좌 정보가 없어 KIS 로그인이 불가합니다.", null);
      }
    }


    Map<String, String> bodyMap = Map.of(
        "grant_type", "client_credentials",
        "appkey", kisTokenDTO.getAppKey(),
        "appsecret", kisTokenDTO.getSecretKey()
    );

    try {
      String jsonBody = objectMapper.writeValueAsString(bodyMap);

      HttpRequest request = HttpRequest.newBuilder()
          .uri(URI.create(url + "/oauth2/tokenP"))
          .header("Content-Type", contentType)
          .POST(HttpRequest.BodyPublishers.ofString(jsonBody))
          .build();

      throttleKisCall();// 초당 api 호출 에러 방지를 위해 삽입
      HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());

      System.out.println(response);
      if (response.statusCode() == 200) {
        KISTokenResDTO resDto = objectMapper.readValue(response.body(), KISTokenResDTO.class);

        // [핵심 로직] 로그인일 때만 DB 저장을 수행한다.
        // 회원가입 시에는 이미 kisTokenDTO.getUsername()이 비어있거나,
        // 저장을 원치 않는 상황이므로 이 블록을 타지 않게 됩니다.
        if (StringUtils.hasText(kisTokenDTO.getUsername())) {

          Integer userId = kisMapper.getUserIdxByUsername(kisTokenDTO.getUsername());

          if (userId != null) {
            resDto.setUserId(userId);
            kisMapper.upsertKisToken(resDto);
            return new ResultDTO(true, "토큰 발급 및 DB 저장 성공", resDto);
          } else {
            return new ResultDTO(false, "사용자를 찾을 수 없습니다.", null);
          }
        }

        // 회원가입인 경우: 저장은 안 하고 토큰 정보만 클라이언트에게 전달
        return new ResultDTO(true, "토큰 발급 성공", resDto);

      } else {
        return new ResultDTO(false, "API 호출 실패: " + response.body(), null);
      }
    } catch (Exception e) {
      e.printStackTrace();
      return new ResultDTO(false, "오류 발생: " + e.getMessage(), null);
    }
  }


  @Override
  public ResultDTO getAllKisToken (int userIdx){
    // 사용자 idx를 받아 appkey, secretkey, token을 return한다.
    // 1 사용자 idx를 이용하여 username 가져오기
    String username = kisMapper.getUsernameByUserIdx(userIdx);

    // 2 appkey, secretkey- username
    KISTokenDTO dto = new KISTokenDTO(username);

    Optional<KISTokenDTO> dbInfo = kisMapper.getKisApiKey(dto);

    KISTokenDTO data = null; // null로 초기화

    if (dbInfo.isPresent()){
      data = dbInfo.get();

      try {
        data.setSecretKey(aesUtil.decrypt(data.getSecretKey()));
        data.setAppKey(aesUtil.decrypt(data.getAppKey()));

      } catch (Exception e) {
        e.printStackTrace();
        return new ResultDTO(false, "복호화 중 오류가 발생했습니다.");
      }
    }

    // 3 token- useridx
    KISTokenResDTO tokenDto = kisMapper.getKisApiToken(userIdx);

    if(tokenDto == null || tokenDto.getAccess_token() == null || tokenDto.getAccess_token().trim().isEmpty()){
      return new ResultDTO(false, "token이 발급되어 있지 않습니다.");
    }

    // expires_at을 체킹하여 토큰 재발급
    if(isTokenExpiredSoon(tokenDto.getExpires_at())){
      // 재발급 진행 필요!
      return new ResultDTO(false, "토큰 만료가 임박하여 갱신이 필요합니다.");
    }

    Map<String, Object> obj = new HashMap<>();
    obj.put("id", userIdx);
    obj.put("username", username);
    obj.put("appkey", data.getAppKey());
    obj.put("appsecret", data.getSecretKey());
    obj.put("CANO", data.getMockAccount());
    obj.put("authorization", tokenDto.getAccess_token());


    return new ResultDTO(true, "", obj);
  }

  private boolean isTokenExpiredSoon(LocalDateTime expiresAt) {
    if (expiresAt == null) return true; // 데이터가 없으면 만료로 간주

    LocalDateTime now = LocalDateTime.now();

    // 두 시간 사이의 차이를 계산
    Duration duration = Duration.between(now, expiresAt);

    // 차이가 6시간보다 작은지 확인
    return duration.toHours() < 6;
  }


  @Override
  public ResultDTO getCashBalanceAndHoldings(int userIdx) {
    // KIS api 사용 옵션을 선택하고 로그인한 사용자의 예수금/ 보유종목 리스트 가져오기

    // kis api 호출을 위한 key, token 가져오기
    ResultDTO keyRes = getAllKisToken(userIdx);

    if(!keyRes.getState()){
      return new ResultDTO<>(false, keyRes.getFailMsg());
    }

    Map<String, Object> keys = (Map<String, Object>) keyRes.getData();

    String cano = (String) keys.get("CANO");
    String appKey = (String) keys.get("appkey");
    String appSecret = (String) keys.get("appsecret");
    String token = (String) keys.get("authorization");

    String availableCash = "0";

    // 1. 실시간 매수가능 금액 조회 API 호출 (VTTC8908R)
    try {
      String psblApiPath = "/uapi/domestic-stock/v1/trading/inquire-psbl-order";
      // 명세에 따른 Query Parameter 구성 (종목코드, 주문단가 공란 시 매수금액 위주로 조회 가능, 시장가 01 등 활용)
      String psblQueryStr = "?CANO=" + cano +
          "&ACNT_PRDT_CD=01" +
          "&PDNO=" +
          "&ORD_UNPR=" +
          "&ORD_DVSN=01" +
          "&CMA_EVLU_AMT_ICLD_YN=N" +
          "&OVRS_ICLD_YN=N";

      HttpRequest psblRequest = HttpRequest.newBuilder()
          .uri(URI.create(url + psblApiPath + psblQueryStr))
          .header("Content-Type", contentType)
          .header("authorization", "Bearer " + token)
          .header("appkey", appKey)
          .header("appsecret", appSecret)
          .header("tr_id", "VTTC8908R") // [모의투자] 매수 가능 조회
          .header("tr_cont", "N")
          .GET()
          .build();


      throttleKisCall();// 초당 api 호출 에러 방지를 위해 삽입
      HttpResponse<String> psblResponse = httpClient.send(psblRequest, HttpResponse.BodyHandlers.ofString());

      if (psblResponse.statusCode() == 200) {
        Map<String, Object> psblBody = objectMapper.readValue(psblResponse.body(), Map.class);
        if ("0".equals(psblBody.get("rt_cd"))) {
          Map<String, String> output = (Map<String, String>) psblBody.get("output");
          if (output != null) {
            // 매수가능금액(ord_psbl_cash) 또는 주문가능현금 관련 필드 매핑
            availableCash = output.get("ord_psbl_cash");
          }
        }
      }
    } catch (Exception e) {
      e.printStackTrace();
      // 매수가능 조회 실패 시 로깅만 하고 잔고 조회는 계속 진행할 수 있습니다.
    }

    // 2. 기존 보유 종목 리스트 및 잔고 총괄 조회 API 호출 (VTTC8434R)
    try{
      String apiPath = "/uapi/domestic-stock/v1/trading/inquire-balance";
      String queryStr = "&ACNT_PRDT_CD=01&AFHR_FLPR_YN=N&OFL_YN=N&INQR_DVSN=01&UNPR_DVSN=01&FUND_STTL_ICLD_YN=N&FNCG_AMT_AUTO_RDPT_YN=N&PRCS_DVSN=00&CTX_AREA_FK100=&CTX_AREA_NK100=";

      HttpRequest request = HttpRequest.newBuilder()
          .uri(URI.create(url + apiPath + "?CANO=" + cano + queryStr))
          .header("Content-Type", contentType)
          .header("authorization", "Bearer " + token)
          .header("appkey", appKey)
          .header("appsecret", appSecret)
          .header("tr_id", "VTTC8434R")
          .header("tr_cont", "N")
          .GET()
          .build();

      throttleKisCall();// 초당 api 호출 에러 방지를 위해 삽입
      HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());

      if (response.statusCode() == 200) {
        Map<String, Object> resultBody = objectMapper.readValue(response.body(), Map.class);

        // 한투 API는 200이 나와도 rt_cd가 "0"이 아니면 실패인 경우가 많음
        if ("0".equals(resultBody.get("rt_cd"))) {
          Map<String, Object> data = new HashMap<>();
          List<Map<String, String>> output2List = (List<Map<String, String>>) resultBody.get("output2");

          if (output2List != null && !output2List.isEmpty()) {
            Map<String, String> firstItem = output2List.get(0);

            // 1번 API에서 조회한 실시간 매수가능금액(availableCash)을 우선 매핑하고,
            // 필요에 따라 기존 계좌 총액 데이터도 함께 담아줍니다.
            data.put("balance", availableCash);                  // 화면 헤더 AVAILABLE BALANCE용 실시간 매수가능금액
            data.put("dncaTotAmt", firstItem.get("dnca_tot_amt")); // 예수금 총액
            data.put("holdings", resultBody.get("output1"));       // 보유 종목 리스트

          }

          return new ResultDTO(true, "조회 성공", data);
        } else {
          return new ResultDTO(false, "조회 실패", resultBody.get("msg1"));
        }
      } else {
        return new ResultDTO(false, "API 조회 실패: " + response.body(), null);
      }

    }catch(Exception e){
      e.printStackTrace();
      return new ResultDTO(false, "오류 발생: " + e.getMessage(), null);
    }
  }

  @Override
  public ResultDTO buyAndSellByKis(int userIdx, KISOrderDTO orderDTO) {
    // KIS api 사용 옵션을 선택하고 로그인한 사용자의 주식 매수/매도 구현
    ResultDTO keyRes = getAllKisToken(userIdx);

    if(!keyRes.getState()){
      return new ResultDTO<>(false, keyRes.getFailMsg());
    }

    Map<String, Object> keys = (Map<String, Object>) keyRes.getData();

    String cano = (String) keys.get("CANO");
    String appKey = (String) keys.get("appkey");
    String appSecret = (String) keys.get("appsecret");
    String token = (String) keys.get("authorization");

    try{
      String apiPath = "/uapi/domestic-stock/v1/trading/order-cash";
      String trId = "BUY".equalsIgnoreCase(orderDTO.getOrderType()) ? "VTTC0012U" : "VTTC0011U";

      // 요청 Body 구성
      Map<String, String> bodyMap = new HashMap<>();
      bodyMap.put("CANO", cano);
      bodyMap.put("ACNT_PRDT_CD", "01");
      bodyMap.put("PDNO", orderDTO.getStockCode());
      bodyMap.put("ORD_DVSN", "01"); // 시장가
      bodyMap.put("ORD_QTY", String.valueOf(orderDTO.getQuantity()));
      bodyMap.put("ORD_UNPR", "0");  // 시장가

      String jsonBody = objectMapper.writeValueAsString(bodyMap);

      // API 호출
      HttpRequest request = HttpRequest.newBuilder()
          .uri(URI.create(url + "/uapi/domestic-stock/v1/trading/order-cash"))
          .header("Content-Type", contentType)
          .header("authorization", "Bearer " + token)
          .header("appkey", appKey)
          .header("appsecret", appSecret)
          .header("tr_id", trId) // 매수/매도 TR_ID
          .POST(HttpRequest.BodyPublishers.ofString(jsonBody))
          .build();

      throttleKisCall();// 초당 api 호출 에러 방지를 위해 삽입
      HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());

      // 응답 확인
      if (response.statusCode() == 200) {
        Map<String, Object> resBody = objectMapper.readValue(response.body(), Map.class);

        // 한투 API는 200이 나와도 rt_cd가 "0"이 아니면 실패인 경우가 많음
        if ("0".equals(resBody.get("rt_cd"))) {
          return new ResultDTO(true, "주문 성공: " + resBody.get("msg1"), resBody.get("output"));
        } else {
          return new ResultDTO(false, "주문 실패: " + resBody.get("msg1"), null);
        }
      } else {
        return new ResultDTO(false, "API 요청 실패: " + response.body(), null);
      }

    }catch(Exception e){
      e.printStackTrace();
      return new ResultDTO(false, "오류 발생: " + e.getMessage(), null);
    }
  }
}
