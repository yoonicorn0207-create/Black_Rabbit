// /resources/js/common.js
window.fetch = ((originalFetch) => {
  return (url, options = {}) => {
    // 헤더 설정이 없으면 객체 생성
    options.headers = options.headers || {};

    // 로컬스토리지에서 accessToken을 가져와 헤더에 추가
    const token = localStorage.getItem("accessToken");
    if (token) {
      options.headers['Authorization'] = 'Bearer ' + token;
    }

    return originalFetch(url, options);
  };
})(window.fetch);