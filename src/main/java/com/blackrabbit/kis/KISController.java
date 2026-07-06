package com.blackrabbit.kis;

import com.blackrabbit.common.dto.ResultDTO;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.ResponseBody;

@Controller
public class KISController {

  @Autowired KISService kisService;

  // kis api 호출을 위한 token 발급 및 저장 로직
  @RequestMapping(value="/api/getKisToken", method = RequestMethod.POST)
  @ResponseBody
  public ResultDTO getKisToken(@RequestBody KISTokenDTO kisTokenDTO){
    return kisService.getKisToken(kisTokenDTO);
  }
}
