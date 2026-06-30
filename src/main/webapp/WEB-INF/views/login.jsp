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
                <p id="idValidationText" class="val_check">중복된 아이디입니다.</p>

                <div class="flex w-full gap-2">
                    <input type="email" placeholder="이메일" class="input" id="userEmail" />
                    <button type="button" class="btn-check" onclick="checkDuplicate('email')">중복확인</button>
                </div>
                <p id="emailValidationText" class="val_check">유효하지 않은 이메일입니다.</p>

                <input type="password" placeholder="비밀번호" class="input" />
                <p id="pwdValidationText" class="val_check">비밀번호가 일치하지 않습니다.</p>

                <input type="password" placeholder="비밀번호 확인" class="input" />
                <p id="repwdValidationText" class="val_check">비밀번호가 일치하지 않습니다.</p>

                <select class="input mb-2" name="balance">
                    <option value="" disabled selected hidden>초기 예수금 선택</option>
                    <option class="text-black" value="10000000">1,000만 원</option>
                    <option class="text-black" value="50000000">5,000만 원</option>
                    <option class="text-black" value="100000000">10,000만 원</option>
                    <option class="text-black" value="500000000">50,000만 원</option>
                </select>

                <button class="btn mx-auto">회원가입 하기</button>
            </form>
        </div>

        <div class="container__form container--signin">
            <form class="form" onsubmit="return false;">
                <div class="logo-text"><span class="text-white">BLACK</span><span class="text-rabbit">RABBIT</span></div>
                <input type="text" placeholder="아이디" class="input mb-4" />
                <input type="password" placeholder="비밀번호" class="input mb-4" />
                <button class="btn">로그인</button>
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

        async function checkDuplicate(type) {
            const inputEl = document.getElementById(type === 'id' ? 'userId' : 'userEmail');
            const msgId = type === 'id' ? 'idValidationText' : 'emailValidationText';
            const val = inputEl.value;

            if (!val) {
                showValidation(msgId, true, "값을 입력하세요.", true);
                return;
            }

            try {
                const response = await fetch(`/api/checkDuplicate?type=${type}&value=${val}`);
                const data = await response.json();

                // data.isDuplicate 가 true면 실패(빨강), false면 성공(흰색)
                const isFailed = data.isDuplicate;
                const message = isFailed ? "이미 사용 중입니다." : "사용 가능한 아이디입니다.";

                showValidation(msgId, true, message, isFailed);
            } catch (e) {
                showValidation(msgId, true, "서버 연결에 실패했습니다.", true);
            }
        }
    </script>
</body>
</html>