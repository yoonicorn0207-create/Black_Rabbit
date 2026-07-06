// ============================ 패널 전환 (로그인 <-> 회원가입) ============================
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
const regexAccount = /^\d{8}-\d{2}$/; // 예: 12345678-01

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

  // KIS 검사
  const kisAccount = document.getElementById('kisAccount').value.trim();
  const kisAppKey = document.getElementById('kisAppKey').value.trim();
  const kisSecretKey = document.getElementById('kisSecretKey').value.trim();
  const hasAnyKis = kisAccount !== "" || kisAppKey !== "" || kisSecretKey !== "";
  const hasAllKis = kisAccount !== "" && kisAppKey !== "" && kisSecretKey !== "";



  // 1. 전체 빈 값 체크
  if (!userId || !userEmail || !pwd || !repwd || !balance) {
    openModal("필수 항목을 모두 입력/선택해주세요.");
    return;
  }
  // kis 입력값 확인
  if (hasAnyKis && !hasAllKis) {
    openModal("KIS 정보 입력 시 모의 계좌번호, App Key, Secret Key를 모두 입력해야 합니다.");
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

  // kis 계좌번호 형식 검사
  if (hasAllKis && !regexAccount.test(kisAccount)) {
    openModal("계좌번호 형식이 올바르지 않습니다.<br>(예: 12345678-01)");
    return;
  }

  // 토큰 생성 api를 호출하여 입력받은 key들이 유효한지 확인한다
  if(!!hasAllKis){
    let successToken =  await getKISToken();
    if(!successToken){
      return;
    }
  }

  // 5. 최종 데이터 전송
  const signupData = {
    username: userId,
    email: userEmail,
    password: pwd,
    balance,
    kisAccount,
    kisAppKey,
    kisSecretKey
  };

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

    openModal(result.failMsg);

  } catch (e) {
    openModal("서버 연결에 실패했습니다.");
  }
}

// kis token 발행 함수
async function getKISToken(){
  try {

    const response = await fetch("/api/getKisToken", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        appKey: kisAppKey,
        secretKey: kisSecretKey
      })
    });

    const result = await response.json();

    if (!result.state) {
      openModal(result.failMsg || "KIS 인증에 실패했습니다.");
      return false;
    }

    return true;

  } catch (e) {
    openModal("KIS 인증 서버와 통신하지 못했습니다.");
    returnfalse;
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

  document.getElementById('kisAccount').value = "";
  document.getElementById('kisAppKey').value = "";
  document.getElementById('kisSecretKey').value = "";

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
    username: document.getElementById('loginId').value,
    password: document.getElementById('loginPwd').value,
    isUseKisApi : document.getElementById('useKisApi').checked
  };

  try {
    const response = await fetch('/api/userLogin', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(loginData)
    });

    const result = await response.json();

    if (result.state) {
      localStorage.setItem("accessToken", result.data.accessToken);
      localStorage.setItem("refreshToken", result.data.refreshToken);
      window.location.href = "/stockMain";
    } else {
      openModal(result.failMsg || "로그인에 실패하였습니다.");
    }
  } catch (e) {
    openModal(`로그인에 실패했습니다. ${e}`);
  }
}

// ============================ 자동완성(자동 채움) 겹침 방지 ============================
// 크롬 등 브라우저는 페이지 내 password input 근처의 text input을 기준으로
// 저장된 로그인 정보를 자동으로 채워 넣는데, 로그인 폼과 회원가입 폼이 같은 페이지(DOM) 안에
// 같이 있다 보니 회원가입 폼에도 로그인 아이디/비번이 그대로 채워지는 문제가 있었음.
//
// 1차 방어: signup-form.jsp 쪽에서 name/autocomplete 속성을 로그인 폼과 완전히
//          다르게 지정 (name="new-userid" 등, autocomplete="off"/"new-password")
// 2차 방어(가장 확실함): 아래처럼 readonly 상태로 두었다가 focus 시점에만 해제.
//          브라우저는 readonly input에는 자동완성을 채우지 않음.
window.addEventListener('DOMContentLoaded', () => {
  const autofillGuardIds = ['userId', 'signupPwd', 'signupRepwd'];
  autofillGuardIds.forEach((id) => {
    const el = document.getElementById(id);
    if (!el) return;
    el.setAttribute('readonly', 'readonly');
    el.addEventListener('focus', function onFocus() {
      el.removeAttribute('readonly');
    }, { once: true });
  });
});
