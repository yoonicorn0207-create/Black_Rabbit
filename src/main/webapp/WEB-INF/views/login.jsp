<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8" %>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BlackRabbit Login</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        :root {
            --glass-bg: rgba(20, 25, 35, 0.85);
            --accent-yellow: #f7df1e;
            --text-white: #ffffff;
            --text-red: #ff3e3e;
            --input-bg: rgba(255, 255, 255, 0.1);
        }

        body { margin: 0; padding: 0; display: grid; height: 100vh; place-items: center; overflow: hidden; font-family: sans-serif; background-color: #0e1118; }

        #bg-video { position: fixed; top: 50%; left: 50%; min-width: 100%; min-height: 100%; transform: translateX(-50%) translateY(-50%); z-index: -1; object-fit: cover; }

        .container { background-color: var(--glass-bg); backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.1); border-radius: 1rem; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5); height: 650px; max-width: 900px; width: 100%; position: relative; overflow: hidden; }

        .logo-text { font-size: 2.2rem; font-weight: 900; margin-bottom: 1rem; letter-spacing: 2px; }
        .text-rabbit { color: var(--text-red); }

        .container__form { height: 100%; position: absolute; top: 0; transition: all 0.6s ease-in-out; }
        .container--signin { left: 0; width: 50%; z-index: 2; }
        .container--signup { left: 0; width: 50%; z-index: 1; opacity: 0; }
        .container.right-panel-active .container--signin { transform: translateX(100%); opacity: 0; }
        .container.right-panel-active .container--signup { transform: translateX(100%); opacity: 1; z-index: 5; }

        .form { display: flex; align-items: center; justify-content: center; flex-direction: column; padding: 0 2.5rem; height: 100%; box-sizing: border-box; }

        .input { background-color: var(--input-bg); border: 1px solid rgba(255,255,255,0.2); padding: 0.7rem 1rem; width: 100%; border-radius: 8px; color: white; font-size: 0.9rem; }
        .input:focus { outline: none; border-color: var(--accent-yellow); }

        /* 중복확인 버튼 */
        .btn-check { border: 1px solid rgba(255,255,255,0.5); color: white; padding: 0 1rem; border-radius: 8px; font-size: 0.75rem; white-space: nowrap; height: 42px; transition: 0.3s; }
        .btn-check:hover { background: white; color: black; }

        /* 유효성 문구 영역 (밀림 방지용) */
        .val_check { width: 100%; min-height: 1.4rem; font-size: 0.75rem; text-align: left; padding: 0 0.5rem; margin-bottom: 0.2rem; color: #ff3e3e; visibility: hidden; }
        .val_check.show { visibility: visible; }

        .btn { background-color: var(--accent-yellow); color: #000; font-weight: 800; border-radius: 50px; padding: 0.8rem 3rem; cursor: pointer; border: none; text-transform: uppercase; margin-top: 1rem; transition: 0.3s; }
        .btn:hover { box-shadow: 0 0 15px var(--accent-yellow); }

        .btn-overlay { background: transparent; border: 2px solid var(--text-white); color: var(--text-white); padding: 1rem 3rem; border-radius: 50px; }
        .btn-overlay:hover { background: var(--text-white); color: #000; }

        .container__overlay { height: 100%; left: 50%; overflow: hidden; position: absolute; top: 0; transition: transform 0.6s ease-in-out; width: 50%; z-index: 100; }
        .container.right-panel-active .container__overlay { transform: translateX(-100%); }
        .overlay { background: linear-gradient(135deg, rgba(20, 25, 35, 0.95), rgba(40, 50, 70, 0.95)); height: 100%; width: 200%; display: flex; position: relative; left: -100%; transition: transform 0.6s ease-in-out; }
        .container.right-panel-active .overlay { transform: translateX(50%); }
        .overlay__panel { width: 50%; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; text-align: center; padding: 0 2rem; }
    </style>
</head>
<body>
    <video id="bg-video" autoplay muted loop playsinline>
        <source src="<c:url value='/resources/video/login_vedio.mp4'/>" type="video/mp4">
    </video>

    <div class="container" id="container">
        <div class="container__form container--signup">
            <form class="form" onsubmit="return false;">
                <div class="logo-text"><span class="text-white">BLACK</span><span class="text-rabbit">RABBIT</span></div>

                <div class="flex w-full gap-2">
                    <input type="text" placeholder="아이디" class="input" id="userId" />
                    <button type="button" class="btn-check" onclick="checkDuplicate('id')">중복확인</button>
                </div>
                <p id="idValidationText" class="val_check"></p>

                <div class="flex w-full gap-2">
                    <input type="email" placeholder="이메일" class="input" id="userEmail" />
                    <button type="button" class="btn-check" onclick="checkDuplicate('email')">중복확인</button>
                </div>
                <p id="emailValidationText" class="val_check"></p>

                <input type="password" placeholder="비밀번호" class="input" id="signupPwd" oninput="checkPasswordMatch()" />
                <p id="pwdValidationText" class="val_check"></p>

                <input type="password" placeholder="비밀번호 확인" class="input" id="signupRepwd" oninput="checkPasswordMatch()" />
                <p id="repwdValidationText" class="val_check"></p>

                <select class="input mb-2" name="balance">
                    <option value="" disabled selected hidden>초기 예수금 선택</option>
                    <option class="text-black" value="10000000">1,000만 원</option>
                    <option class="text-black" value="50000000">5,000만 원</option>
                    <option class="text-black" value="100000000">10,000만 원</option>
                    <option class="text-black" value="500000000">50,000만 원</option>
                </select>

                <button class="btn mx-auto" onclick="submitSignup()">회원가입 하기</button>
            </form>
        </div>

        <div class="container__form container--signin">
            <form class="form" onsubmit="return false;">
                <div class="logo-text"><span class="text-white">BLACK</span><span class="text-rabbit">RABBIT</span></div>
                <input id="loginId" type="text" placeholder="아이디" class="input mb-4" />
                <input id="loginPwd" type="password" placeholder="비밀번호" class="input mb-4" />
                <button class="btn" onclick="submitLogin()">로그인</button>
            </form>
        </div>

        <div class="container__overlay">
            <div class="overlay">
                <div class="overlay__panel">
                    <h2 class="text-xl text-white font-bold mb-4">이미 계정이 있으신가요?</h2>
                    <button class="btn-overlay" id="signIn">로그인 하기</button>
                </div>
                <div class="overlay__panel">
                    <h2 class="text-xl text-white font-bold mb-4">처음이신가요?</h2>
                    <button class="btn-overlay" id="signUp">회원가입</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        // ============================ 회원가입을 위한 사용자 입력값 실시간 유효성 검사 ============================
        const container = document.getElementById("container");
        document.getElementById("signUp").onclick = () => container.classList.add("right-panel-active");
        document.getElementById("signIn").onclick = () => container.classList.remove("right-panel-active");

        // 유효성 검사 메시지 표시 함수
        // isError: true(빨간색, 실패), false(흰색, 성공)
        function showValidation(id, isShow, message = "", isError = true) {
            const el = document.getElementById(id);
            el.innerText = message;
            el.style.color = isError ? "#ff3e3e" : "#ffffff"; // 실패:빨강, 성공:흰색
            el.classList.toggle('show', isShow);
        }

        // ============================ 회원가입을 위한 유효성 검사 ============================
        // 상태 관리 변수
        let isIdChecked = false;
        let isEmailChecked = false;

        // 유효성 검사 패턴
        const regexId = /^[a-zA-Z0-9_-]{5,20}$/;
        const regexPwd = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d!\"\#\$%&'()*+,\-./:;<=>?@\[\\\]^_`{|}~]{8,20}$/;
        const regexEmail = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

        // 실시간 검사 이벤트 리스너 추가
        document.getElementById('userId').addEventListener('input', () => {
            isIdChecked = false; // 내용 변경 시 중복 검사 초기화
            const val = document.getElementById('userId').value;
            if (!regexId.test(val)) showValidation('idValidationText', true, "5~20자의 영문, 숫자, _, -만 사용 가능합니다.", true);
            else showValidation('idValidationText', true, "사용 가능한 형식입니다.", false);
        });

        // 이메일 입력 실시간 체크
        document.getElementById('userEmail').addEventListener('input', () => {
            isEmailChecked = false; // 내용 변경 시 중복 검사 초기화
            const val = document.getElementById('userEmail').value;

            if (!regexEmail.test(val)) {
                showValidation('emailValidationText', true, "올바른 이메일 형식이 아닙니다.", true);
            } else {
                showValidation('emailValidationText', true, "사용 가능한 이메일 형식입니다.", false);
            }
        });

        // 비밀번호 실시간 체크 (비밀번호, 비밀번호 확인 input에 각각 ID 부여 필요)
        function checkPasswordMatch() {
            const pwd = document.getElementById('signupPwd').value;
            const repwd = document.getElementById('signupRepwd').value;

            if (!regexPwd.test(pwd)) showValidation('pwdValidationText', true, "영문/숫자 포함 8~20자 입력하세요.", true);
            else showValidation('pwdValidationText', true, "사용 가능한 비밀번호입니다.", false);

            if (pwd !== repwd || repwd === "") showValidation('repwdValidationText', true, "비밀번호가 일치하지 않습니다.", true);
            else showValidation('repwdValidationText', true, "비밀번호가 일치합니다.", false);
        }

        // ============================ 중복 확인 api 호출 함수 ============================
        async function checkDuplicate(type) {
            const isId = type === 'id';
            const inputEl = document.getElementById(isId ? 'userId' : 'userEmail');
            const val = inputEl.value;
            const msgId = isId ? 'idValidationText' : 'emailValidationText';

            // 1. 형식 검사 (통과 못하면 바로 모달)
            const isValid = isId ? regexId.test(val) : regexEmail.test(val);
            if (!isValid) {
                openModal(isId ? "아이디 형식을 확인해주세요.<br>(5~20자의 영문, 숫자, _, -)" : "올바른 이메일 형식이 아닙니다.");
                return;
            }

            // 2. 서버 중복 검사 호출
            try {
                const response = await fetch(`/api/signinDup`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ type: type, value: val })
                });
                const data = await response.json();

                if (data.state) {
                    showValidation(msgId, true, "사용 가능한 " + (isId ? "아이디" : "이메일") + "입니다.", false);
                    if (isId) isIdChecked = true;
                    else isEmailChecked = true;
                } else {
                    showValidation(msgId, true, data.failMsg, true);
                }
            } catch (e) {
                openModal("서버 연결에 실패했습니다.");
            }
        }

        // ============================ 회원가입 ============================
        async function submitSignup() {
            const userId = document.getElementById('userId').value;
            const userEmail = document.getElementById('userEmail').value;
            const pwd = document.getElementById('signupPwd').value;
            const repwd = document.getElementById('signupRepwd').value;
            const balance = document.querySelector('select[name="balance"]').value;

            // 1. 전체 빈 값 체크
            if (!userId || !userEmail || !pwd || !repwd || !balance) {
                openModal("모든 항목을 입력/선택해주세요.");
                return;
            }

            // 2. 아이디/이메일 중복 확인 여부 체크
            if (!isIdChecked || !isEmailChecked) {
                openModal("아이디 또는 이메일 중복 확인을<br>먼저 진행해주세요.");
                return;
            }

            // 3. 비밀번호 유효성 검사 (형식 확인)
            if (!regexPwd.test(pwd)) {
                openModal("비밀번호 형식이 올바르지 않습니다.<br>(영문/숫자 포함 8~20자)");
                return;
            }

            // 4. 비밀번호 일치 확인
            if (pwd !== repwd) {
                openModal("비밀번호가 일치하지 않습니다.");
                return;
            }

            // 5. 최종 데이터 전송
            const signupData = { username: userId, email: userEmail, password: pwd, balance: balance };

            try {
                const response = await fetch('/api/userSignup', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(signupData)
                });
                const result = await response.json();

                if (result.state) {
                    // 화면 로그인 폼 전환
                    container.classList.remove("right-panel-active");

                    // 회원가입 input 초기화
                    resetSignupForm();
                }

                openModal(result.failMsg );

            } catch (e) {
                openModal("서버 연결에 실패했습니다.");
            }
        }
        // 회원가입 폼 초기화 함수
        function resetSignupForm() {
            // 입력창 비우기
            document.getElementById('userId').value = "";
            document.getElementById('userEmail').value = "";
            document.getElementById('signupPwd').value = "";
            document.getElementById('signupRepwd').value = "";
            document.querySelector('select[name="balance"]').value = "";

            // 유효성 검사 문구 숨기기 및 상태 초기화
            isIdChecked = false;
            isEmailChecked = false;

            const validations = ['idValidationText', 'emailValidationText', 'pwdValidationText', 'repwdValidationText'];
            validations.forEach(id => {
                showValidation(id, false, "", true);
            });
        }


        // ============================ 로그인 ============================
        async function submitLogin() {
            const loginData = {
                username: document.getElementById('loginId').value, // 로그인 input ID 수정 필요
                password: document.getElementById('loginPwd').value
            };

            try {
                const response = await fetch('/api/userLogin', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(loginData)
                });

                const result = await response.json();

                if (result.state) {
                    // 서버에서 받은 토큰 저장
                    localStorage.setItem("accessToken", result.data.accessToken);
                    localStorage.setItem("refreshToken", result.data.refreshToken);

                    window.location.href = "<c:url value='/stockMain'/>"; // 메인 페이지 이동
                } else {
                    openModal(result.failMsg || "로그인에 실패하였습니다.");
                }
            } catch (e) {
                openModal("서버 연결에 실패했습니다.");
            }
        }
    </script>
    <script src="<c:url value='/resources/js/common.js'/>"></script>
    <%@ include file="/WEB-INF/views/common/modal.jsp" %>
</body>
</html>