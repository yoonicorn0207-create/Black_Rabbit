<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8" %>
<div id="editUserModal" class="hidden fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-70">
    <div class="bg-[#1a1f2e] border border-white/10 p-8 rounded-2xl w-full max-w-lg shadow-2xl relative">
        <button onclick="closeEditModal()" class="absolute top-4 right-4 text-gray-400 hover:text-white text-2xl">&times;</button>
        <h2 class="text-white text-xl font-bold mb-6" id="modalTitle">본인 확인</h2>

        <div id="authSection" class="flex flex-col items-center space-y-4" style="gap: 1.5rem">
            <p class="text-gray-400 text-sm">정보 수정을 위해 현재 비밀번호를 입력해주세요.</p>
            <input type="password" id="checkPwd" class="input" style="margin:0;" placeholder="현재 비밀번호" autocomplete="new-password" />
            <button onclick="verifyPassword()" class="modal-btn" style="width:200px; padding:12px 0; margin:10px auto 0;">확인</button>
        </div>

        <div id="editSection" class="hidden space-y-4 text-left">
            <div>
                <label class="block text-xs text-gray-400 mb-1">아이디 / 잔여 예수금</label>
                <div class="flex gap-2">
                    <input type="text" id="editUsername" class="input flex-1" readonly />
                    <input type="text" id="editBalance" class="input flex-1" readonly />
                </div>
            </div>

            <div>
                <label class="block text-xs text-gray-400 mb-1">이메일</label>
                <div class="flex gap-2">
                    <input type="email" id="editEmail" class="input flex-1" oninput="resetEmailCheck()" />
                    <button type="button" class="btn-check" onclick="checkDuplicate('email', event)">중복확인</button>
                </div>
                <p id="editEmailVal" class="val_check"></p>
            </div>

            <div>
                <label class="block text-xs text-gray-400 mb-1">새 비밀번호 (변경 시 입력)</label>
                <input type="password" id="editPwd" class="input" placeholder="영문/숫자 포함 8~20자" oninput="validateEditForm()" />
                <p id="editPwdVal" class="val_check"></p>
                <input type="password" id="editRepwd" class="input mt-2" placeholder="비밀번호 확인" oninput="validateEditForm()" />
                <p id="editRepwdVal" class="val_check"></p>
            </div>

            <div class="space-y-2">
                <label class="block text-xs text-gray-400 mb-1">한투 모의투자 정보</label>
                <input type="text" id="editKisAccount" class="input mb-1" placeholder="계좌번호" />
                <input type="text" id="editAppKey" class="input mb-1" placeholder="새로운 App Key" />
                <input type="text" id="editSecretKey" class="input" placeholder="새로운 Secret Key" />
            </div>

            <div class="flex flex-col items-center justify-center gap-4 mx-auto w-full">
                <div class="flex items-center gap-2 mt-2">
                    <input type="checkbox" id="deleteKisCheck" class="w-4 h-4 cursor-pointer" />
                    <label for="deleteKisCheck" class="text-[12px] text-red-400 cursor-pointer hover:underline">
                        기존 한국투자증권 정보 삭제하기
                    </label>
                </div>
                <button onclick="submitEditUser(event)" class="modal-btn w-[200px] py-3 mt-2">수정하기</button>
            </div>
        </div>
    </div>
</div>

<script>
    let initialEmail = "";
    let isEmailChecked = true;
    let isPwdValid = true;
    let isPwdMatch = true;

    const regexPwd = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d!\"\#\$%&'()*+,\-./:;<=>?@\[\\\]^_`{|}~]{8,20}$/;
    const regexEmail = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

    function openEditModal() {
        document.getElementById('authSection').classList.remove('hidden');
        document.getElementById('editSection').classList.add('hidden');
        document.getElementById('modalTitle').innerText = "본인 확인";
        document.getElementById('editUserModal').classList.remove('hidden');
    }

    function closeEditModal() {
        document.getElementById('checkPwd').value = "";
        document.getElementById('editUserModal').classList.add('hidden');
    }

    function resetEmailCheck() {
        const currentEmail = document.getElementById('editEmail').value;
        isEmailChecked = (currentEmail === initialEmail);
    }

    // 실시간 유효성 검사 로직 (비밀번호)
    function validateEditForm() {
        const pwd = document.getElementById('editPwd').value;
        const repwd = document.getElementById('editRepwd').value;

        if (pwd.length > 0 && !regexPwd.test(pwd)) {
            showValidation('editPwdVal', true, "영문/숫자 포함 8~20자 입력하세요.", true);
            isPwdValid = false;
        } else {
            showValidation('editPwdVal', pwd.length > 0, pwd.length > 0 ? "사용 가능한 비밀번호입니다." : "", false);
            isPwdValid = true;
        }

        if (pwd.length > 0 || repwd.length > 0) {
            if (pwd !== repwd) {
                showValidation('editRepwdVal', true, "비밀번호가 일치하지 않습니다.", true);
                isPwdMatch = false;
            } else {
                showValidation('editRepwdVal', true, "비밀번호가 일치합니다.", false);
                isPwdMatch = true;
            }
        } else {
            showValidation('editRepwdVal', false);
            isPwdMatch = true;
        }
    }

    async function verifyPassword() {
        const pwd = document.getElementById('checkPwd').value;
        const userId = document.getElementById('loginUserId').innerText.replace('님', '');

        try {
            const response = await fetch('/api/verifyPassword', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ password: pwd, username: userId })
            });
            const result = await response.json();

            if (result.state) {
                initialEmail = result.data.email;
                isEmailChecked = true;
                document.getElementById('authSection').classList.add('hidden');
                document.getElementById('editSection').classList.remove('hidden');
                document.getElementById('modalTitle').innerText = "회원 정보 수정";
                document.getElementById('editUsername').value = result.data.username;
                document.getElementById('editBalance').value = result.data.balance.toLocaleString();
                document.getElementById('editEmail').value = result.data.email;
            } else {
                openModal("비밀번호가 일치하지 않습니다.");
            }
        } catch(e) {
            openModal("인증 서버 통신 오류");
        }
    }

    async function checkDuplicate(type, event) {
        const email = document.getElementById('editEmail').value;
        if (email === initialEmail) {
            openModal("현재 사용 중인 이메일과 동일합니다.");
            isEmailChecked = true;
            return;
        }
        if (!regexEmail.test(email)) {
            openModal("올바른 이메일 형식이 아닙니다.");
            return;
        }

        const response = await fetch('/api/signinDup', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ type: type, value: email })
        });
        const data = await response.json();

        if (data.state) {
            isEmailChecked = true;
            openModal("사용 가능한 이메일입니다.");
        } else {
            openModal(data.failMsg);
        }
    }

    async function submitEditUser(event) {
    const btnEl = event.target;

        const email = document.getElementById('editEmail').value;
        const pwd = document.getElementById('editPwd').value;
        const repwd = document.getElementById('editRepwd').value;

        // 모의투자 관련 데이터
        const kisAccount = document.getElementById('editKisAccount').value.trim();
        const appKey = document.getElementById('editAppKey').value.trim();
        const appSecret = document.getElementById('editSecretKey').value.trim();
        const deleteKis = document.getElementById('deleteKisCheck').checked;

        if (email !== initialEmail && !isEmailChecked) {
            openModal("이메일 중복 확인이 필요합니다.");
            return;
        }
        if (pwd.length > 0 && (!isPwdValid || !isPwdMatch)) {
            openModal("비밀번호 형식을 확인하거나 일치시켜주세요.");
            return;
        }

        // 3. 모의투자 계좌 유효성 검사 (삭제 체크 안 했을 때만)
        if (!deleteKis) {
            // 계좌번호 8자리 정규식 (필요 시 수정)
            const regexAccount = /^\d{8}$/;

            // 하나라도 입력되어 있다면 셋 다 입력되어야 함
            const hasAny = kisAccount || appKey || appSecret;
            if (hasAny) {
                if (!regexAccount.test(kisAccount)) {
                    openModal("계좌번호는 8자리 숫자여야 합니다.");
                    return;
                }
                if (!kisAccount || !appKey || !appSecret) {
                    openModal("모의투자 정보(계좌, App Key, Secret)를 모두 입력해주세요.");
                    return;
                }
            }
        }

     try {
        // api 호출로 버튼 로딩 시작
        toggleBtnLoading(btnEl, true);

        const data = {
            email: email,
            password: pwd,
            mockAccount: kisAccount,
            appKey,
            appSecret,
            deleteKis
        };

        const response = await fetch('/api/editUserData', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const result = await response.json();

        if (result.state) {
            closeEditModal();
            openModal("정보가 수정되었습니다. 다시 로그인해주세요.");
        } else {
            openModal(result.failMsg || "수정 실패");
        }
    } catch (e) {
        openModal(`로그인에 실패했습니다. ${e}`);
      }finally{
        toggleBtnLoading(btnEl, false);
      }
    }
    function showValidation(id, isShow, message = "", isError = true) {
      const el = document.getElementById(id);
      el.innerText = message;
      el.style.color = isError ? "#ff3e3e" : "#ffffff"; // 실패:빨강, 성공:흰색
      el.classList.toggle('show', isShow);
    }
</script>