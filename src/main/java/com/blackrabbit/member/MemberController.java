package com.blackrabbit.member;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.RequestMapping;

@Controller
public class MemberController {


    // 브라우저에서 /helloJSP 입력하면 index.jsp실행됨
    @RequestMapping(value = "/hello")
    public String helloJSP(Model model) {

        model.addAttribute("msg", "hello_javaworld");

        return "index";
    }


}// MemberController
