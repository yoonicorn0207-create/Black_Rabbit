<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8" %>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BlackRabbit Login</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="<c:url value='/resources/css/login.css'/>">
</head>
<body>
    <video id="bg-video" autoplay muted loop playsinline>
        <source src="<c:url value='/resources/video/login_vedio.mp4'/>" type="video/mp4">
    </video>

    <div class="container" id="container">

        <%-- 회원가입 컴포넌트 --%>
        <jsp:include page="/WEB-INF/views/login/signup-form.jsp" />

        <%-- 로그인 컴포넌트 --%>
        <jsp:include page="/WEB-INF/views/login/login-form.jsp" />

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

    <script src="<c:url value='/resources/js/login.js'/>"></script>
    <%@ include file="/WEB-INF/views/common/modal.jsp" %>
</body>
</html>
