package com.blackrabbit.kis;

import com.blackrabbit.common.dto.ResultDTO;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.Map;

@Service("KISService")
public class KISServiceImpl implements KISService {

  @Autowired
  private KISMapper kisMapper;

  private final HttpClient httpClient = HttpClient.newHttpClient();
  private final ObjectMapper objectMapper = new ObjectMapper();

  @Override
  public ResultDTO getKisToken(KISTokenDTO kisTokenDTO) {
    String url = "https://openapivts.koreainvestment.com:29443/oauth2/tokenP";

    // 1. 요청 바디 생성 (DTO에서 암호화된 키를 복호화해서 가져온다고 가정)
    // ※ 실제 구현 시에는 이 부분에서 암호화된 키를 복호화하는 로직이 들어가야 합니다.
    Map<String, String> bodyMap = Map.of(
        "grant_type", "client_credentials",
        "appkey", kisTokenDTO.getAppKey(),
        "appsecret", kisTokenDTO.getSecretKey()
    );

    try {
      String jsonBody = objectMapper.writeValueAsString(bodyMap);

      HttpRequest request = HttpRequest.newBuilder()
          .uri(URI.create(url))
          .header("Content-Type", "application/json")
          .POST(HttpRequest.BodyPublishers.ofString(jsonBody))
          .build();

      HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());

      if (response.statusCode() == 200) {
        // 2. 응답 데이터를 DTO로 변환
        KISTokenResDTO resDto = objectMapper.readValue(response.body(), KISTokenResDTO.class);

        // 3. UserId 할당 (DB 저장을 위해 필요)
//        resDto.setUserId(kisTokenDTO.getUserId());

        // 4. DB에 Upsert (저장/갱신)
        kisMapper.upsertKisToken(resDto);

        return new ResultDTO(true, "토큰 발급 및 저장 성공", resDto);
      } else {
        return new ResultDTO(false, "API 호출 실패: " + response.body(), null);
      }
    } catch (Exception e) {
      e.printStackTrace();
      return new ResultDTO(false, "오류 발생: " + e.getMessage(), null);
    }
  }
}