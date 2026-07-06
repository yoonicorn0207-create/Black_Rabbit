<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8" %>
<div class="container__form container--signin">
    <form class="form" onsubmit="return false;" autocomplete="on">
        <div class="logo-text"><span class="text-white">BLACK</span><span class="text-rabbit">RABBIT</span></div>
        <input id="loginId" name="username" type="text" placeholder="아이디" class="input mb-4"
               autocomplete="username" />
        <input id="loginPwd" name="current-password" type="password" placeholder="비밀번호" class="input mb-4"
               autocomplete="current-password" />

        <!-- KIS API 사용 여부 체크박스 -->
        <div class="flex items-center mb-4 self-start pl-1">
            <input type="checkbox" id="useKisApi" class="w-4 h-4 accent-yellow-400 cursor-pointer" />
            <label for="useKisApi" class="ml-2 text-white text-sm cursor-pointer">한국투자증권 모의투자 사용</label>
        </div>

        <button class="btn" onclick="submitLogin()">로그인</button>
    </form>
</div>