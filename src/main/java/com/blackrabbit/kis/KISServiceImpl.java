package com.blackrabbit.kis;

import com.blackrabbit.common.dto.ResultDTO;
import org.springframework.stereotype.Service;

@Service("KISService")
public class KISServiceImpl implements KISService {

  @Override
  public ResultDTO getKisToken(KISTokenDTO kisTokenDTO){
    ResultDTO res = new ResultDTO();

    return res;
  }
}
