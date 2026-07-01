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
        /* 공통 모달 스타일 */
        #commonModal > div {
            background-color: #1a1f2e; /* 다크 모드 배경색 */
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: white; /* 텍스트 흰색 */
            padding: 2rem;
            border-radius: 1rem;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
        }

        /* 확인 버튼 스타일 */
        .modal-btn {
            background-color: #f7df1e; /* 포인트 컬러 */
            color: black;
            font-weight: bold;
            padding: 0.5rem 2rem;
            border-radius: 50px;
            cursor: pointer;
            border: none;
            margin-top: 1rem;
        }
    </style>
</head>
<body>
    <div id="commonModal" class="hidden fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
        <div class="bg-white p-6 rounded-lg shadow-xl min-w-80 max-w-md text-center">
            <p id="modalMessage" class="text-black-800 mb-4"></p>
            <button onclick="closeModal()" class="bg-yellow-400 px-4 py-2 rounded text-black">확인</button>
        </div>
    </div>
    <script>
        function openModal(msg) {
            const msgElement = document.getElementById('modalMessage');
            msgElement.innerHTML = msg; // innerText 대신 innerHTML 사용
            document.getElementById('commonModal').classList.remove('hidden');
        }
        function closeModal() {
            document.getElementById('commonModal').classList.add('hidden');
        }
    </script>
</body>
</html>