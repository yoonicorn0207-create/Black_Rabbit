package com.blackrabbit.stock;


import com.blackrabbit.common.dto.ResultDTO;
import com.blackrabbit.kis.KISOrderDTO;
import com.blackrabbit.kis.KISService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.*;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpSession;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Controller
public class StockController {


    @Autowired
    private StockService stockService;
    @Autowired private KISService kisService;

    /* BlackRabbit 메인페이지 호출 */
    @RequestMapping("/stockMain")
    public String getStockMainPage() {
        return "stock_main";
    }//BlackRabbit 메인페이지 호출 (2026_0626에 추가)

    /* 1. BlackRabbit 메인페이지 - WatchList (2026_0626에 추가) */
    @RequestMapping(value = "/api/stockList", method = RequestMethod.GET)
    @ResponseBody
    public StockListResDTO getPresent_stockList(
        @RequestParam(defaultValue = "0") int page,
        @RequestParam(defaultValue = "30") int size,
        @RequestParam(required = false) String keyword
    ) {
        return stockService.getPresent_StockList(page, size, keyword);
    }//BlackRabbit 메인페이지 - WatchList 데이터 호출 [HC_stock_daily1 테이블] (2026_0626에 추가)


    /* 2. BlackRabbit 메인페이지 - 일별/주별/월별 차트 (2026_0629) */
    @RequestMapping("/api/chartData")
    @ResponseBody
    public List<Map<String, Object>> getChartData(@RequestParam("code") String code, @RequestParam("period") String period) {
        // 1. Service를 통해 DB에서 데이터 조회
        List<StockDailyDTO> dailyList = stockService.getDailyStockChartData(code, period);


        // 2. ApexCharts가 인식할 수 있는 JSON 구조로 변환
        return dailyList.stream().map((StockDailyDTO sddto) -> {
            Map<String, Object> map = new HashMap<>();

            // 이제 여기서 sddto를 사용하면 됩니다.
            map.put("x", sddto.getStck_bsop_date());
            map.put("y", new double[]{
                    sddto.getStck_oprc(), // 시가
                    sddto.getStck_hgpr(), // 고가
                    sddto.getStck_lwpr(), // 저가
                    sddto.getStck_clpr()  // 종가
            });
            return map;
        }).collect(Collectors.toList());

    }//BlackRabbit 메인페이지 - 일별/주별/월별 차트


    /* 3. BlackRabbit 메인페이지 - 분봉/시간봉 (2026_0630) */
    @RequestMapping("/api/minHourChartData")
    @ResponseBody
    public List<Map<String, Object>> getMinHourBar(@RequestParam("code") String code, @RequestParam("period") String period) {
        // 1. Service를 통해 DB에서 데이터 조회
        List<StockDailyDTO> dailyList = stockService.getMinHourChart(code, period);


        // 2. ApexCharts가 인식할 수 있는 JSON 구조로 변환
        return dailyList.stream().map((StockDailyDTO sddto) -> {
            Map<String, Object> map = new HashMap<>();

            // 이제 여기서 sddto를 사용하면 됩니다.
            map.put("x", sddto.getStck_bsop_date());
            map.put("y", new double[]{
                    sddto.getStck_oprc(), // 시가
                    sddto.getStck_hgpr(), // 고가
                    sddto.getStck_lwpr(), // 저가
                    sddto.getStck_clpr()  // 종가
            });
            return map;
        }).collect(Collectors.toList());

    }//BlackRabbit 메인페이지 - 분봉/시간봉

    /* 4. BlackRabbit 메인페이지 - 회원 보유종목 리스트  (2026_0630) By.yoonicorn */
    @RequestMapping("/api/myHoldings")
    @ResponseBody
    public ResultDTO getMyHoldings(HttpSession session, HttpServletRequest request) {
        // 1. 세션에서 사용자 ID 가져오기
        String userId = (String) session.getAttribute("userId");

        // 추가) kis api 사용 여부 분기 처리- 260708
        // 인터셉터가 토큰을 뜯어서 넣어준 isUseKis 값을 확인
        Boolean isUseKis = (Boolean) request.getAttribute("isUseKis");

        if (isUseKis != null && isUseKis) {
            // [한투 모의투자 모드]
            return kisService.getCashBalanceAndHoldings(Integer.parseInt(userId));
        }

        // 기존 로직 진행
        Map<String, Object> response = new HashMap<>();

        // 3. 서비스 호출하여 리스트 변수에 담기
        List<UserHoldingStockDTO> userHoldingList = stockService.getMyHoldings(userId);

        // 3-1. 사용자 예수금 반환
        long balance = stockService.getUserBalance(userId);

        response.put("balance", balance);
        response.put("holdings", userHoldingList);

        // 4. 변수 반환
        return new ResultDTO(true, "", response);
    }

    /// BlackRabbit 메인페이지 - 회원 보유종목 리스트


    /* 5. BlackRabbit 메인페이지 - 주식 매수 (2026_0701 추가) */
    @RequestMapping(value = "/api/buyStock", method = RequestMethod.POST)
    @ResponseBody
    public ResultDTO buyStock(
        @RequestBody Map<String, Object> orderData,
        HttpSession session,
        HttpServletRequest request
    ) {
        try {
            // 1. 세션에서 사용자 ID 가져오기
            String userId = (String) session.getAttribute("userId");

            // 추가) kis api 사용 여부 분기 처리- 260709
            // 인터셉터가 토큰을 뜯어서 넣어준 isUseKis 값을 확인
            Boolean isUseKis = (Boolean) request.getAttribute("isUseKis");

            // 2. 요청 데이터 파싱
            String stockCode = (String) orderData.get("stockCode");
            String stockName = (String) orderData.get("stockName");
            int quantity = Integer.parseInt(orderData.get("quantity").toString());

            if (isUseKis != null && isUseKis) {
                // [한투 모의투자 모드]
                // 매수 진행
                KISOrderDTO orderDTO = new KISOrderDTO(stockCode, quantity, "BUY");
                return kisService.buyAndSellByKis(Integer.parseInt(userId), orderDTO);
            }

            // 3. 서비스 호출하여 DB 처리 (매수 로직 수행)
            // stockService 내부에 매수 트랜잭션 처리(잔액 차감, 보유종목 추가/갱신) 메서드가 있어야 합니다.
            boolean result = stockService.buyStock(userId, stockCode, stockName, quantity);

            if (result) {
                // 여기서 예수금 가져오기 진행
                return new ResultDTO(true, "매수 성공");
            } else {
                return new ResultDTO(true, "거래 처리에 실패했습니다. 잔액 또는 보유 수량을 확인하세요.");
            }
        } catch (Exception e) {
            e.printStackTrace();
            return new ResultDTO(true, "서버 오류 발생");
        }
    }//BlackRabbit 메인페이지 - 주식 매수


    /* 6. BlackRabbit 메인페이지 - 주식 매도 (2026_0701 추가) */
    @RequestMapping(value = "/api/sellStock", method = RequestMethod.POST)
    @ResponseBody
    public ResultDTO sellStock(
        @RequestBody Map<String, Object> orderData,
        HttpSession session,
        HttpServletRequest request
    ) {
        try {
            // 1. 세션 사용자 ID 처리
            String userId = (String) session.getAttribute("userId");

            // 추가) kis api 사용 여부 분기 처리- 260709
            // 인터셉터가 토큰을 뜯어서 넣어준 isUseKis 값을 확인
            Boolean isUseKis = (Boolean) request.getAttribute("isUseKis");

            // 2. 요청 데이터 파싱
            String stockCode = (String) orderData.get("stockCode");
            int quantity = Integer.parseInt(orderData.get("quantity").toString());

            if (isUseKis != null && isUseKis) {
                // [한투 모의투자 모드]
                // 매수 진행
                KISOrderDTO orderDTO = new KISOrderDTO(stockCode, quantity, "SELL");
                return kisService.buyAndSellByKis(Integer.parseInt(userId), orderDTO);
            }

            // 3. 서비스 호출하여 매도 로직 수행
            // 서비스에서 매도(수량 차감/삭제 및 잔액 증가)를 처리합니다.
            boolean result = stockService.sellStock(userId, stockCode, quantity);

            if (result) {
                // 여기서 예수금 가져오기 진행
                return new ResultDTO(true, "매도 성공");
            } else {
                return new ResultDTO(true, "거래 처리에 실패했습니다. 잔액 또는 보유 수량을 확인하세요.");
            }
        } catch (Exception e) {
            e.printStackTrace();
            return new ResultDTO(true, "서버 오류 발생");
        }
    }

    /// /BlackRabbit 메인페이지 - 주식 매도


    /* 7. 예수금 조회 API */
    @RequestMapping(value = "/api/userBalance", method = RequestMethod.GET)
    @ResponseBody
    public Map<String, Object> getUserBalance(HttpSession session) {
        String userId = (String) session.getAttribute("userId");
        // 서비스 단에서 DB의 HC_user 테이블의 balance를 가져오는 메서드 필요
        long balance = stockService.getUserBalance(userId);

        Map<String, Object> response = new HashMap<>();
        response.put("balance", balance);
        return response;
    }//예수금 조회 API

    /* 8. KOSPI & KOSDAQ 지수 호츨API (2026_0708) */
    @RequestMapping(value = "/api/market-indices", method = RequestMethod.GET)
    @ResponseBody
    public ResponseEntity<MarketIndexDTO> getMarketIndices() {
        // 1. 단일 객체로 서비스 호출
        MarketIndexDTO marketIndex = stockService.getLatestIndex();

        // 2. 데이터가 없을 경우 처리
        if (marketIndex == null) {
            return ResponseEntity.noContent().build();
        }

        // 3. 단일 객체 그대로 반환
        return ResponseEntity.ok(marketIndex);
    }

}// StockController
