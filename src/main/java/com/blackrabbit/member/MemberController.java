package com.blackrabbit.member;

import com.blackrabbit.common.dto.ResultDTO;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.ResponseBody;

@Controller
public class MemberController {

    @Autowired MemberService memberService;


    // 패스워드 인증
    // 인증 성공 시 사용자 데이터 return;
    @RequestMapping(value="/api/verifyPassword", method = RequestMethod.POST)
    @ResponseBody
    public ResultDTO verifyPassword(@RequestBody MemberDTO memberDTO){

        return memberService.verifyPwd(memberDTO);
    }

    // 회원정보 수정하기
    @RequestMapping(value="/api/editUserData", method = RequestMethod.POST)
    @ResponseBody
    public  ResultDTO editUserData(@RequestBody MemberDTO memberDTO){

        return memberService.editUserInfo(memberDTO);
    }

}
