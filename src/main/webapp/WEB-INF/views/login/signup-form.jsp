<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8" %>
<div class="container__form container--signup">
    <form class="form" onsubmit="return false;" autocomplete="off">
        <div class="logo-text"><span class="text-white">BLACK</span><span class="text-rabbit">RABBIT</span></div>

        <label class="field-label" for="userId">아이디 <span class="required-mark">*</span></label>
        <div class="flex w-full gap-2">
            <input type="text" placeholder="아이디" class="input" id="userId" name="new-userid"
                   autocomplete="off" />
            <button type="button" class="btn-check" onclick="checkDuplicate('id')">중복확인</button>
        </div>
        <p id="idValidationText" class="val_check"></p>

        <label class="field-label" for="userEmail">이메일 <span class="required-mark">*</span></label>
        <div class="flex w-full gap-2">
            <input type="email" placeholder="이메일" class="input" id="userEmail" name="new-email"
                   autocomplete="off" />
            <button type="button" class="btn-check" onclick="checkDuplicate('email')">중복확인</button>
        </div>
        <p id="emailValidationText" class="val_check"></p>

        <label class="field-label" for="signupPwd">비밀번호 <span class="required-mark">*</span></label>
        <input type="password" placeholder="비밀번호" class="input" id="signupPwd" name="new-password-field"
               autocomplete="new-password" oninput="checkPasswordMatch()" />
        <p id="pwdValidationText" class="val_check"></p>

        <label class="field-label" for="signupRepwd">비밀번호 확인 <span class="required-mark">*</span></label>
        <input type="password" placeholder="비밀번호 확인" class="input" id="signupRepwd" name="new-password-confirm"
               autocomplete="new-password" oninput="checkPasswordMatch()" />
        <p id="repwdValidationText" class="val_check"></p>

        <label class="field-label" for="initialBalance">초기 예수금 <span class="required-mark">*</span></label>
        <select class="input mb-2" name="balance" id="initialBalance">
            <option value="" disabled selected hidden>초기 예수금 선택</option>
            <option class="text-black" value="10000000">1,000만 원</option>
            <option class="text-black" value="50000000">5,000만 원</option>
            <option class="text-black" value="100000000">10,000만 원</option>
            <option class="text-black" value="500000000">50,000만 원</option>
        </select>

        <!-- KIS 모의투자 연동 정보 -->
        <label class="field-label" for="kisAccount">KIS 모의투자 계좌번호</label>
        <input type="text" placeholder="ex: 500xxxxx-01" class="input mb-2" id="kisAccount"
               name="kis-account" autocomplete="off" />

        <label class="field-label" for="kisAppKey">App Key</label>
        <input type="text" placeholder="App Key" class="input mb-2" id="kisAppKey"
               name="kis-app-key" autocomplete="off" />

        <label class="field-label" for="kisSecretKey">Secret Key</label>
        <input type="text" placeholder="Secret Key" class="input mb-2" id="kisSecretKey"
               name="kis-secret-key" autocomplete="off" />

        <button class="btn mx-auto" onclick="submitSignup()">회원가입 하기</button>
    </form>
</div>
