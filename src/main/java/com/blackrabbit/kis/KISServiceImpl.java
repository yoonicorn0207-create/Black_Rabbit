package com.blackrabbit.kis;

import com.blackrabbit.common.dto.ResultDTO;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.Map;
import java.util.NoSuchElementException;
import java.util.Optional;

@Service("KISService")
public class KISServiceImpl implements KISService {

  @Autowired
  private KISMapper kisMapper;

  private final HttpClient httpClient = HttpClient.newHttpClient();
  private final ObjectMapper objectMapper = new ObjectMapper();

  @Override
  public ResultDTO getKisToken(KISTokenDTO kisTokenDTO) {
    // 토큰 발급받기
    // 로그인/ 회원가입 두가지 경우에서 모두 사용되며
    // kisTokenDTO 안에 username=id의 존재 유무로 로그인/ 회원가입 분기 판단

    // username 존재: 로그인
    if (StringUtils.hasText(kisTokenDTO.getUsername())) {
      // null이 아니고, 길이가 0보다 크고, 공백 문자가 아닌 문자가 하나라도 포함되어 있을 때 true
      // db에서 key 뽑아오기 -> decrypt
      Optional <KISTokenDTO> dbInfo =kisMapper.getKisApiKey(kisTokenDTO);

      if (dbInfo.isPresent()) {
        KISTokenDTO data = dbInfo.get();
        kisTokenDTO.setAppKey(data.getAppKey());
        kisTokenDTO.setSecretKey(data.getSecretKey());
      } else {
        return new ResultDTO(false, "등록된 KIS 계좌 정보가 없어 KIS 로그인이 불가합니다.", null);
      }
    }

    String url = "https://openapivts.koreainvestment.com:29443/oauth2/tokenP";

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