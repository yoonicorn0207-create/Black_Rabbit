// ======================== 전역 변수 선언 ==============================
let allStocks = []; // 전역 변수 추가
let currentStockCode = "005930"; // 기본값 삼성전자
let currentPage = 0;
const PAGE_SIZE = 30;
let currentKeyword = "";
let totalCount = 0;
let isLoading = false;
let hasMore = true;



// ============================== apexChart config ==============================
/* * [초기화 및 차트 설정]
     * 페이지 로드 시 차트 객체를 선언하고 렌더링합니다.
     */
const chart = new ApexCharts(document.querySelector("#main-chart"), {
  series: [
    {name: '주가', type: 'candlestick', data: []},
    {name: '5', type: 'line', data: []},
    {name: '20', type: 'line', data: []},
    {name: '60', type: 'line', data: []},
    {name: '120', type: 'line', data: []}
  ],
  chart: {
    type: 'candlestick',
    height: '100%',
    zoom: {enabled: true},
    pan: {enabled: true}, // 마우스 드래그로 과거 데이터 탐색 가능
    // [추가된 부분] 범례를 위해 상단에 여백 확보
    animations: {enabled: false},
    toolbar: {show: false}
  },
  // [추가된 부분] 범례(Legend) 설정 시작
  legend: {
    show: true,
    position: 'top',      // 상단 배치
    horizontalAlign: 'right', // 우측 정렬 (요청하신 빨간 영역 쪽)
    fontSize: '12px',
    labels: {
      colors: '#d1d4dc' // 전체적인 테마 색상에 맞춤
    },
    markers: {
      width: 12,
      height: 12,
      radius: 0
    }
  },
  // [추가된 부분] 범례 설정 끝
  stroke: {
    width: [0, 2, 2, 2, 2],
    curve: 'smooth',
    colors: ['#FFFFFF', '#FFD700', '#FF4500', '#00FF00', '#00BFFF']
  },
  tooltip: {
    shared: true,
    intersect: false
  },
  plotOptions: {candlestick: {colors: {upward: '#ef4444', downward: '#3b82f6'}}},
  xaxis: {labels: {style: {colors: '#9CA3AF'}}},
  yaxis: {
    labels: {
      style: {colors: '#9CA3AF'},
      formatter: function (val) {
        return val.toLocaleString(); // 가격을 1,000 단위로 표시
      }
    },
    forceNiceScale: true, // [추가] 가격 범위에 맞게 눈금 자동 조정
    decimalsInFloat: 0    // [추가] 정수 가격이면 소수점 제거
  }
});

//보유종목 도넛형 차트(2026_0630)
const donutChart = new ApexCharts(document.querySelector("#donut-chart"), {
  series: [], // 빈 배열로 시작
  labels: [],
  chart: {type: 'donut', height: 160},
  legend: {show: false},
  noData: {
    text: '보유 종목이 없습니다.',
    align: 'center',
    verticalAlign: 'middle',
    style: {
      color: '#6b7280',
      fontSize: '14px'
    }
  },
});





// ============================== getStockList ==============================
/* * [API 통신] (2026_0626에 추가)
     * fetchAndRender: 서버의 /api/stockList 경로에서 종목 데이터를 가져와
     * 렌더링 함수인 renderWatchlist로 데이터를 전달.
     *
     * 기능 추가 260713
     * - 페이지네이션
     * - 현재 출력중인 데이터 수/ 총 데이터 수
     */
async function fetchAndRender(opts = {}) {
  if (isLoading || !hasMore) return; // 중복 요청/더 없을 때 방지
  isLoading = true;

  try {
    const params = new URLSearchParams({
      page: currentPage,
      size: PAGE_SIZE,
      keyword: currentKeyword
    });

    const response = await fetch(
      `/api/stockList?${params}`,
      { silent: opts.silent }
    );
    const data = await response.json();

    const newStocks = Array.isArray(data.list) ? data.list : [];
    totalCount = data.total || 0;

    // 1. 전체 데이터를 전역 변수에 담기
    // 누적: 검색/첫 로딩이면 새로 시작, 스크롤이면 이어붙이기
    allStocks = currentPage === 0 ? newStocks : [...allStocks, ...newStocks];

    // 2. 초기 리스트 렌더링
    renderWatchlist(newStocks, currentPage === 0);
    updateCountDisplay();

    hasMore = allStocks.length < totalCount;
    currentPage++;
  } catch (error) {
    console.error('에러:', error);
  }finally {
    isLoading = false;
  }
}//

// ============================== watchList 화면 그리기 ==============================
/* * [Watchlist UI 렌더링] (2026_0626에 추가)
 * renderWatchlist: API로 받은 stockList 배열을 순회하며 HTML 요소를 생성하여 #watchlist 영역에 삽입.
 * 클릭 시 상단 종목 타이틀을 변경하는 기능을 포함.
 *
 * 기능 추가 260713
 * - 페이지네이션
 * - 현재 출력중인 데이터 수/ 총 데이터 수
 */
function renderWatchlist(stockList, reset = false) {
  const wl = document.getElementById('watchlist');
  if (reset) wl.innerHTML = '';

  // stockList가 배열인지 확인 후 처리
  if (!Array.isArray(stockList)) return;

  stockList.forEach(s => {
    const code = s.stck_shrn_iscd || "000000";
    const name = s.hts_kor_isnm || "종목명";
    const price = s.stck_prpr ? parseInt(s.stck_prpr).toLocaleString() : '0';

    const div = document.createElement('div');

    div.className = "px-3 py-2 bg-black rounded border border-gray-800 hover:border-gray-600 transition cursor-pointer flex justify-between items-center";
    div.innerHTML = `
                <div class="text-sm font-bold text-white truncate">[${code}] ${name}</div>
                <div class="text-sm font-mono text-gray-300">₩ ${price}</div>
            `;

    // 리스트 클릭 시 차트 타이틀 변경 예시 (필요 시)
    div.onclick = async () => {
      currentStockCode = code; // 전역 변수 업데이트
      document.getElementById('stock-title').innerText = name;

      // 2. [추가] ORDER 영역에 종목명 및 현재가 표시(2026_0701)
      document.getElementById('order-stock-name').innerText = name;
      document.getElementById('order-stock-price').innerText = `₩ ${price}`;

      // 3. 차트 데이터 로드
      const activeBtn = document.querySelector('.period-btn.active');
      const period = activeBtn ? activeBtn.innerText : 'day';
      await fetchChartData(code, period);
    };

    wl.appendChild(div);
  });
}


// ============================== 노출 개수 표시 ==============================
function updateCountDisplay() {
  document.getElementById('watchlist-count').innerText =
    `${allStocks.length.toLocaleString()} / ${totalCount.toLocaleString()}`;
}

// ============================== 검색 (버튼 + 디바운스 둘 다 지원) ==============================
function searchStock() {
  const keyword = document.getElementById('stockInput').value.trim();
  currentKeyword = keyword;
  currentPage = 0;
  hasMore = true;
  fetchAndRender({ silent: true });
}

let searchDebounceTimer = null;
document.getElementById('stockInput').addEventListener('input', () => {
  clearTimeout(searchDebounceTimer);
  searchDebounceTimer = setTimeout(searchStock, 300); // 타이핑 멈추고 0.3초 후 자동 검색
});

// ============================== 무한 스크롤 ==============================
document.getElementById('watchlist').addEventListener('scroll', function () {
  const { scrollTop, scrollHeight, clientHeight } = this;
  // 스크롤이 하단 50px 이내로 오면 다음 페이지 로드
  if (scrollHeight - scrollTop - clientHeight < 50) {
    fetchAndRender({ silent: true }); // 스크롤 로딩은 조용히 (전체 화면 로딩창 X)
  }
});



// ============================== 분봉/ 시간봉 차트 ==============================
// [추가] fetch를 사용하는 새로운 차트 데이터 로드 함수 (2026_0629 생성)
async function fetchChartData(stockCode, period, opts = {}) {
  try {
    // 서버의 컨트롤러로 요청 전송
    const url = period === 'minute' || period === 'hour' ? "minHourChartData" : "chartData";
    const response = await fetch(`/api/${url}?code=${stockCode}&period=${period}`, { silent: opts.silent });

    if (!response.ok) throw new Error('서버 데이터 응답 실패');

    const data = await response.json(); // DB에서 변환된 JSON 데이터 수신
    console.log("받아온 데이터:", data); // F12 콘솔에서 확인용

    // ApexCharts 차트 객체(chart)의 시리즈 데이터 업데이트
    // 가격 등을 차드에 반영하기 위해 가격 등을 숫자로 명시적 변환 진행
    const formattedData = data.map(item => {
      return {
        x: item.x, // 날짜
        y: [
          parseFloat(item.y[0]), // 시가
          parseFloat(item.y[1]), // 고가
          parseFloat(item.y[2]), // 저가
          parseFloat(item.y[3])  // 종가(또는 현재가)
        ]
      }
    });

    // 이동평균선 계산
    const ma5 = calculateMA(5, formattedData);
    const ma20 = calculateMA(20, formattedData);
    const ma60 = calculateMA(60, formattedData);
    const ma120 = calculateMA(120, formattedData);


    // [중요] 모든 데이터를 한 번에 업데이트
    chart.updateSeries([
      {name: '주가', type: 'candlestick', data: formattedData},
      {name: '5', type: 'line', data: ma5},
      {name: '20', type: 'line', data: ma20},
      {name: '60', type: 'line', data: ma60},
      {name: '120', type: 'line', data: ma120}
    ]);


    // 종목마다 차트 금액 표시선 변경되도록 updateOption 추가
    chart.updateOptions({
      series: [{data: formattedData}],
      yaxis: {
        // 기존 스타일 유지
        labels: {
          style: {colors: '#9CA3AF'},
          formatter: (val) => val.toLocaleString()
        },
        forceNiceScale: true,
        decimalsInFloat: 0
      }
    }, true, true, true);

    // 종목명 업데이트 (선택 사항)
    // document.getElementById('stock-title').innerText = stockCode;

  } catch (error) {
    console.error("차트 데이터를 불러오는 중 에러 발생:", error);
  }
}


// ============================== 로그인 사용자의 보유종목 출력 ==============================
/* * [수정된 보유 종목 UI 렌더링] (2026_0630)
   * 서버에서 API(/api/myHoldings)를 호출해 실제 데이터를 가져와 그립니다.
   */
async function renderHoldings(opts = {}) {
  try {
    const response = await fetch('/api/myHoldings', { silent: opts.silent });
    if (!response.ok) throw new Error('데이터 로드 실패');

    const res = await response.json();

    if(!res.state){
      openModal(res.failMsg || "보유종목 리스트를 가져오지 못했습니다");
      return;
    }

    // 예수금 화면에 그리기
    const balance = Number(res?.data?.balance);
    document.getElementById('available-balance').innerText = `₩ ${balance.toLocaleString()}`;

    const holdings = res?.data?.holdings;
    // 보유종목 화면에 그리기
    const list = document.getElementById('holding-list');


    // 보유 종목이 없을 경우
    if (!holdings || holdings.length === 0) {
      // 차트 비우기
      list.innerHTML += `<div class="text-center text-gray-500 py-10">보유 종목이 없습니다.</div>`;
      donutChart.updateSeries([]);
      return; // 함수 종료
    }


    // 1. 헤더 수정: 4개 -> 5개 컬럼으로 (종목, 수량, 평단, 현재, 수익) (2026_0701 수정)
    list.innerHTML = `<div class="grid grid-cols-5 gap-1 text-gray-500 border-b border-gray-800 pb-1 mb-1 text-[10px]">
                        <span class="text-center">종목</span>
                        <span class="text-center">수량</span>
                        <span class="text-center">평단</span>
                        <span class="text-center">현재</span>
                        <span class="text-center">수익</span>
                      </div>`;

    // 1. 도넛 차트 데이터 준비
    const chartSeries = [];
    const chartLabels = [];


    holdings.forEach(s => {
      const name = s.stock_name || s.prdt_name || "알수없음";
      const qty = Number(s.total_quantity || s.hldg_qty || 0);
      const avgPrice = Number(s.avg_buy_price || s.pchs_avg_pric || 0);
      const currentPrice = Number(s.current_price || s.prpr || 0);
      const profit = Number(s.profit_rate || s.evlu_pfls_rt || 0);
      const iscd = s.stck_shrn_iscd || s.pdno || "";

      const color = profit >= 0 ? 'text-up' : 'text-down';


      // 2. 행 클릭 시 매도 정보 자동 입력 (onclick 이벤트 추가) (2026_0701)
      list.innerHTML += `
    <div class="grid grid-cols-5 gap-1 items-center text-[11px] py-1 border-b border-gray-900 cursor-pointer hover:bg-gray-800"
         onclick="prepareSell('${name}', ${qty}, '${iscd}', ${avgPrice})">
        <span class="font-bold text-white truncate text-center">${name}</span>
        <span class="font-mono text-gray-300 text-center">${qty.toLocaleString()}</span>
        <span class="font-mono text-center">₩ ${avgPrice.toLocaleString()}</span>
        <span class="font-mono text-center">₩ ${currentPrice.toLocaleString()}</span>
        <span class="${color} font-bold text-center">${profit.toFixed(2)}%</span>
    </div>`;

      // 2. 도넛 차트용 데이터 배열 채우기
      // 예: (현재가 * 수량)으로 비중 계산
      chartSeries.push(currentPrice * qty);
      chartLabels.push(name);
    });

    console.log("chartSeries : ", chartSeries)
    console.log("chartLabels : ", chartLabels)

    // 3. 도넛 차트 업데이트 (ApexCharts 제공 메서드)
    donutChart.updateOptions({
      series: chartSeries,
      labels: chartLabels
    });

  } catch (error) {
    console.error("보유 종목 로딩 실패:", error);
  }
}//renderHoldings(보유종목 리스트)


// ============================== 분봉 선택 ==============================
/* * [이벤트 핸들러]
 * updatePeriod: 차트 기간 버튼 클릭 시 호출됩니다.
 * 버튼 디자인을 변경하고 선택된 기간에 맞춰 차트 데이터를 업데이트합니다.
 */
function updatePeriod(period, button) {

  // 1. UI 활성화 상태 변경
  document.querySelectorAll('.period-btn').forEach(btn => btn.classList.remove('active'));
  button.classList.add('active');

  // 서버에 파라미터 전달 (예: 'day')
  fetchChartData(currentStockCode, period);
}


// ============================== watchList 검색 ==============================
// 검색창 입력 시 호출될 함수(2026_0629)
function filterWatchlist(keyword) {
  const searchKeyword = keyword.toLowerCase().trim();

  // 코드 혹은 이름이 포함된 항목만 필터링
  const filtered = allStocks.filter(s =>
    (s.stck_shrn_iscd && s.stck_shrn_iscd.includes(searchKeyword)) ||
    (s.hts_kor_isnm && s.hts_kor_isnm.toLowerCase().includes(searchKeyword))
  );

  renderWatchlist(filtered); // 필터링된 데이터만 다시 그리기
}//검색창 검색어 입력 시 호출


// ============================== 매수/ 매도 ==============================
// [수정] 매수/매도 공통 실행 함수(2026_0701)
async function executeOrder(type) {
  try{
    const quantity = document.getElementById('order-quantity').value;
    const stockName = document.getElementById('order-stock-name').innerText;

    if (!quantity || quantity <= 0) {
      openModal("수량을 확인하세요.");
      return;
    }

    const url = type === 'buy' ? '/api/buyStock' : '/api/sellStock';

    const response = await fetch(url, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        stockCode: currentStockCode,
        stockName,
        quantity: parseInt(quantity)
      })
    });

    const result = await response.json();


    if (result.state) {
      // kis 모의투자의 경우 매수/매도가 바로 kis 서버에 반영되지 않으므로 2.5초의 딜레이 부여
      setTimeout(async()=>{
        await renderHoldings({ silent: true }); // 리스트 갱신
      }, 2500)

      // await loadUserBalance(); // 2. [추가] 예수금 즉시 갱신 (2026_0706)
      document.getElementById('order-quantity').value = '';// 3. 입력창 초기화 (선택 사항) (2026_0706)
    }

    await openModal(result.failMsg);

  }catch(error){
    console.error(error)
  }
}


// ============================== 매도 시 평단가 추가 출력 ==============================
// [추가] 매도 시 입력창 자동 채우기(2026_0701)
function prepareSell(name, quantity, code, avgPrice) {
  document.getElementById('order-stock-name').innerText = name;
  // 평단가 표시를 위해 새로운 span 추가 또는 기존 영역 활용
  // 여기서는 종목명 옆에 평단가를 함께 표시하도록 구성
  document.getElementById('order-stock-price').innerText =`(평단: ₩ ${avgPrice.toLocaleString()})`
  document.getElementById('order-quantity').value = quantity;
  currentStockCode = code;
}



// ============================== 예수금 잔액 출력 ==============================
// [추가] 예수금 정보를 서버에서 가져와 화면에 출력 (2026_0706)
// 보유 종목 api와 통합 진행 260713
async function loadUserBalance() {
  try {
    const response = await fetch('/api/userBalance');
    const data = await response.json();
    if (data.balance !== undefined) {
      // 천 단위 콤마 처리
      document.getElementById('available-balance').innerText = `₩ ${data.balance.toLocaleString()}`;
    }
  } catch (error) {
    console.error("예수금 로드 실패:", error);
  }
}//loadUserBalance()



// ============================== kospi& kosdaq ==============================
// 3분(180,000ms)마다 KOSPI & KOSDAQ지수 업데이트(2026_0708)
async function updateMarketIndices() {
  try {
    const response = await fetch('/api/market-indices');
    if (!response.ok) throw new Error('네트워크 응답 오류');

    const data = await response.json();

    // 데이터가 배열인지 확인 후 처리 (안전장치)
    const latest = Array.isArray(data) ? data[0] : data;

    if (latest) {
      const indexContainer = document.querySelector('.flex.gap-4.text-sm.text-gray-400');
      indexContainer.innerHTML = `  
			<p>KOSPI <span class="text-green-400 font-mono">${latest.kospi.toLocaleString()}</span></p>  
			<p>KOSDAQ <span class="text-red-500 font-mono">${latest.kosdaq.toLocaleString()}</span></p>  
		`;
    }
  } catch (error) {
    console.error("지수 업데이트 실패:", error);
    // 에러 시 사용자에게 알림을 띄우거나, 기존 값을 유지하는 로직 추가 가능
  }
}


// ============================== 이동평균선 계산 ==============================
// 수정된 이동평균 계산 함수 (기간 파라미터 추가)
function calculateMA(dayCount, data) {
  let result = [];
  for (let i = 0; i < data.length; i++) {
    if (i < dayCount - 1) {
      result.push({x: data[i].x, y: null});
    } else {
      let sum = 0;
      for (let j = 0; j < dayCount; j++) {
        // 데이터 배열에서 종가(y[3])를 가져옴
        sum += parseFloat(data[i - j].y[3]);
      }
      result.push({x: data[i].x, y: (sum / dayCount).toFixed(0)});
    }
  }
  return result;
}



// =============================== 로그아웃 ===============================
async function logout() {
  try {
    // 서버 측 토큰 무효화 요청
    await fetch('/api/logout', { method: 'POST' });
  } catch (e) {
    console.error("로그아웃 서버 처리 실패");
  } finally {
    // 성공하든 실패하든 클라이언트 로컬 스토리지는 반드시 비움
    localStorage.removeItem("accessToken");
    localStorage.removeItem("refreshToken");

    // 로그인 페이지로 이동
    window.location.href = "/login";
  }
}

// ========================== 로그인된 사용자 id 출력을 위한 로직 ===========================
async function loadUserInfo(opts = {}) {
  const res = await fetch('/api/userInfo', { silent: opts.silent });
  const data = await res.json();
  if(data.userId) {
    document.getElementById('loginUserId').innerText = data.userId + "님";
  }
}



// =========================== 페이지 랜딩 시 바로 실행 ================================
/* * [페이지 라이프사이클 관리]
     * DOMContentLoaded: HTML 문서가 모두 로드된 직후 실행되는 초기화 블록입니다.
     */
// [중요] 페이지 로드 시 실행되는 부분 (2026_0626에 추가)
document.addEventListener('DOMContentLoaded', async () => {
  try {
    showLoading();
    // 서로 의존관계 없는 초기 데이터는 동시에 호출
    await Promise.all([
      fetchAndRender(),   // Watchlist 서버 데이터 호출
      loadUserInfo(),     // 사용자 아이디 출력 위해 호출
      // loadUserBalance(); // 예수금 불러오기 (2026_0706)
    ]);

    // 1. 차트 초기화 (초기 데이터는 빈 배열로 시작)
    chart.updateSeries([{data: []}]); //(2026_0629 추가)
    chart.render();
    donutChart.render();

    // render 완료 후에 실제 데이터 채워넣기
    await Promise.all([
      fetchChartData("005930", "1D"), // 삼성전자 기본값 세팅
      renderHoldings() // 보유 종목 호출
    ]);
  } finally {
    hideLoading();
  }


  // 5초마다 데이터 갱신
  setInterval(() => fetchAndRender({ silent: true }), 50000);
  //3분마다 (KOSPI & KOSDAQ)지수로드
  setInterval(() => updateMarketIndices({ silent: true }), 180000);
});