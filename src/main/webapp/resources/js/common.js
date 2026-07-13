// /resources/js/common.js

// 로딩창 로직
let loadingCount = 0;
const MIN_DISPLAY_TIME = 500; // ms
let loadingShownAt = 0;

function showLoading() {
  loadingCount++;
  if (loadingCount === 1) {
    loadingShownAt = Date.now();
    document.getElementById('global-loading')?.classList.remove('hidden');
  }
}

function hideLoading() {
  loadingCount = Math.max(0, loadingCount - 1);
  if (loadingCount === 0) {
    const elapsed = Date.now() - loadingShownAt;
    const remaining = MIN_DISPLAY_TIME - elapsed;

    if (remaining > 0) {
      setTimeout(() => {
        // 대기하는 동안 다시 로딩이 시작됐을 수 있으니 재확인
        if (loadingCount === 0) {
          document.getElementById('global-loading')?.classList.add('hidden');
        }
      }, remaining);
    } else {
      document.getElementById('global-loading')?.classList.add('hidden');
    }
  }
}


// 토큰+ 로딩창 추가
/* 만약 로딩창을 사용하고 싶지 않다면 아래와 같이 silent true 옵션을 준다
* fetch('/api/stock/price/live', { silent: true })
*   .then(res => res.json())
*   .then(updatePrice);
* */
window.fetch = ((originalFetch) => {
  return (url, options = {}) => {
    // 헤더 설정이 없으면 객체 생성
    const opts = { ...options, headers: { ...(options.headers || {}) } };

    // 로컬스토리지에서 accessToken을 가져와 헤더에 추가
    const token = localStorage.getItem("accessToken");
    if (token) {
      opts.headers['Authorization'] = 'Bearer ' + token;
    }

    const silent = options.silent === true;
    delete opts.silent; // 원본 fetch에 전달되지 않도록 제거

    if (!silent)  showLoading();

    try {
      const promise = originalFetch(url, opts);
      return silent ? promise : promise.finally(() => hideLoading());
    } catch (err) {
      if (!silent) hideLoading();
      throw err;
    }
  };
})(window.fetch);

