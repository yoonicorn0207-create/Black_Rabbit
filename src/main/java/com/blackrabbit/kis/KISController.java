package com.blackrabbit.kis;

import com.blackrabbit.common.dto.ResultDTO;
import com.blackrabbit.login.LoginMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.ResponseBody;

import javax.servlet.http.HttpSession;
import java.util.concurrent.locks.ReentrantLock;

@Controller
public class KISController {

  @Autowired KISService kisService;
  @Autowired LoginMapper loginMapper;

  // kis api 호출을 위한 token 발급 및 저장 로직
  @RequestMapping(value="/api/getKisToken", method = RequestMethod.POST)
  @ResponseBody
  public ResultDTO getKisToken(@RequestBody KISTokenDTO kisTokenDTO){

    return kisService.getKisToken(kisTokenDTO);
  }

  // kis api: 보유종목+ 예수금
  @RequestMapping(value="/api/kisHoldingsBalance", method = RequestMethod.POST)
  @ResponseBody
  public ResultDTO getKisHB(HttpSession session){

    String userIdIdx = (String) session.getAttribute("userId");

    if(userIdIdx == null){
      return new ResultDTO(false, "정상적인 접근이 아닙니다. <br/>다시 로그인해주세요.");
    }

    return kisService.getCashBalanceAndHoldings(Integer.parseInt(userIdIdx));
  }


  // kis api: 매수/ 매도
  @RequestMapping(value="/api/tradeStockByKis", method = RequestMethod.POST)
  @ResponseBody
  public ResultDTO tradeStockByKis(HttpSession session, @RequestBody KISOrderDTO orderDto){
    // 종목명, 매수/매도, 갯수

    String userIdIdx = (String) session.getAttribute("userId");

    if(userIdIdx == null){
      return new ResultDTO(false, "정상적인 접근이 아닙니다. <br/>다시 로그인해주세요.");
    }

    return kisService.buyAndSellByKis(Integer.parseInt(userIdIdx), orderDto);
  }
}
