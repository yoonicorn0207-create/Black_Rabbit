// ======================== 전역 변수 선언 ==============================
let allStocks = [];
let currentStockCode = "005930"; // 기본값 삼성전자
let currentPage = 0;
const PAGE_SIZE = 30;
let currentKeyword = "";
let totalCount = 0;
let isLoading = false;
let hasMore = true;

// ============================== apexChart config ==============================
const chart = new ApexCharts(document.querySelector("#main-chart"), {
  series: [
    {name: '주가', type: 'candlestick', data: []},
    {name: '5', type: 'line', data: []},
    {name: '20', type: 'line', data: []},
    {name: '60', type: 'line', data: []},
    {name: '120', type: 'line', data: []}
  ],
  colors: ['#FFFFFF', '#FFD700', '#FF4500', '#00FF00', '#00BFFF'],
  chart: {
    type: 'candlestick',
    height: '100%',
    zoom: {
      enabled: true,
      type: 'x',
      autoScaleYaxis: true
    },
    pan: {enabled: true},
    animations: {enabled: false},
    toolbar: {
      show: false
    }
  },
  legend: {
    show: true,
    position: 'top',
    horizontalAlign: 'right',
    fontSize: '12px',
    labels: {
      colors: '#d1d4dc'
    },
    markers: {
      width: 12,
      height: 12,
      radius: 0
    }
  },
  stroke: {
    width: [1, 2, 2, 2, 2], // 캔들 테두리 두께를 1로 주어 굵기 및 겹침 현상 개선
    curve: 'smooth',
    colors: ['#ef4444', '#FFD700', '#FF4500', '#00FF00', '#00BFFF']
  },
  tooltip: {
    shared: true,
    intersect: false
  },
  plotOptions: {
    candlestick: {
      colors: {
        upward: '#ef4444',
        downward: '#3b82f6'
      },
      wick: {
        useFillColor: true
      }
    }
  },
  xaxis: {
    type: 'category',
    labels: {
      style: {colors: '#9CA3AF'},
      offsetY: 2,
      hideOverlappingLabels: true
    },
    range: 50,
    scrollbar: {
      enabled: true,
      show: true,
      height: 20,
      offsetX: 0,
      offsetY: 0
    }
  },
  grid: {
    borderColor: '#374151',
    padding: {
      bottom: 25,
      left: 10,
      right: 10
    }
  },
  yaxis: {
    labels: {
      style: {colors: '#9CA3AF'},
      formatter: function (val) {
        return val ? val.toLocaleString() : '';
      }
    },
    forceNiceScale: true,
    decimalsInFloat: 0
  }
});

const donutChart = new ApexCharts(document.querySelector("#donut-chart"), {
  series: [],
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
async function fetchAndRender(opts = {}) {
  if (isLoading || !hasMore) return;
  isLoading = true;

  try {
    const params = new URLSearchParams({
      page: currentPage,
      size: PAGE_SIZE,
      keyword: currentKeyword
    });

    const response = await fetch(`/api/stockList?${params}`, { silent: opts.silent });
    const data = await response.json();

    const newStocks = Array.isArray(data.list) ? data.list : [];
    totalCount = data.total || 0;

    allStocks = currentPage === 0 ? newStocks : [...allStocks, ...newStocks];

    renderWatchlist(newStocks, currentPage === 0);
    updateCountDisplay();

    hasMore = allStocks.length < totalCount;
    currentPage++;
  } catch (error) {
    console.error('에러:', error);
  } finally {
    isLoading = false;
  }
}

// ============================== 실시간 시세 갱신 ==============================
async function refreshWatchlist(opts = {}) {
  const loadedCount = allStocks.length || PAGE_SIZE;

  try {
    const params = new URLSearchParams({
      page: 0,
      size: loadedCount,
      keyword: currentKeyword
    });

    const response = await fetch(`/api/stockList?${params}`, { silent: true });
    const data = await response.json();

    const refreshedStocks = Array.isArray(data.list) ? data.list : [];
    totalCount = data.total || 0;

    allStocks = refreshedStocks;
    renderWatchlist(refreshedStocks, true);
    updateCountDisplay();

    hasMore = allStocks.length < totalCount;
  } catch (error) {
    console.error('실시간 갱신 에러:', error);
  }
}

// ============================== watchList 화면 그리기 ==============================
function renderWatchlist(stockList, reset = false) {
  const wl = document.getElementById('watchlist');
  if (reset) wl.innerHTML = '';

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

    div.onclick = async () => {
      currentStockCode = code;
      document.getElementById('stock-title').innerText = name;
      document.getElementById('order-stock-name').innerText = name;
      document.getElementById('order-stock-price').innerText = `₩ ${price}`;

      const activeBtn = document.querySelector('.period-btn.active');
      const period = activeBtn ? activeBtn.innerText : 'day';
      await fetchChartData(code, period);
    };

    wl.appendChild(div);
  });
}

function updateCountDisplay() {
  document.getElementById('watchlist-count').innerText =
      `${allStocks.length.toLocaleString()} / ${totalCount.toLocaleString()}`;
}

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
  searchDebounceTimer = setTimeout(searchStock, 300);
});

document.getElementById('watchlist').addEventListener('scroll', function () {
  const { scrollTop, scrollHeight, clientHeight } = this;
  if (scrollHeight - scrollTop - clientHeight < 50) {
    fetchAndRender({ silent: true });
  }
});

// ============================== 분봉/ 시간봉 차트 ==============================
async function fetchChartData(stockCode, period, opts = {}) {
  try {
    const url = period === 'minute' || period === 'hour' ? "minHourChartData" : "chartData";
    const response = await fetch(`/api/${url}?code=${stockCode}&period=${period}`, { silent: opts.silent });

    if (!response.ok) throw new Error('서버 데이터 응답 실패');

    const data = await response.json();

    const formattedData = data.map(item => ({
      x: item.x,
      y: [
        parseFloat(item.y[0]),
        parseFloat(item.y[1]),
        parseFloat(item.y[2]),
        parseFloat(item.y[3])
      ]
    }));

    const ma5 = calculateMA(5, formattedData);
    const ma20 = calculateMA(20, formattedData);
    const ma60 = calculateMA(60, formattedData);
    const ma120 = calculateMA(120, formattedData);

    chart.updateSeries([
      {name: '주가', type: 'candlestick', data: formattedData},
      {name: '5', type: 'line', data: ma5},
      {name: '20', type: 'line', data: ma20},
      {name: '60', type: 'line', data: ma60},
      {name: '120', type: 'line', data: ma120}
    ]);

    chart.updateOptions({
      yaxis: {
        labels: {
          style: {colors: '#9CA3AF'},
          formatter: (val) => val ? val.toLocaleString() : ''
        },
        forceNiceScale: true,
        decimalsInFloat: 0
      }
    }, true, true, true);

  } catch (error) {
    console.error("차트 데이터를 불러오는 중 에러 발생:", error);
  }
}

// ============================== 로그인 사용자의 보유종목 출력 ==============================
async function renderHoldings(opts = {}) {
  try {
    const response = await fetch('/api/myHoldings', { silent: opts.silent });
    if (!response.ok) throw new Error('데이터 로드 실패');

    const res = await response.json();
    if(!res.state){
      openModal(res.failMsg || "보유종목 리스트를 가져오지 못했습니다");
      return;
    }

    const balance = Number(res?.data?.balance);
    document.getElementById('available-balance').innerText =
        `₩ ${Number.isFinite(balance) ? balance.toLocaleString() : '0'}`;

    const holdings = res?.data?.holdings;
    const list = document.getElementById('holding-list');

    if (!holdings || holdings.length === 0) {
      list.innerHTML = `<div class="text-center text-gray-500 py-10">보유 종목이 없습니다.</div>`;
      donutChart.updateSeries([]);
      return;
    }

    list.innerHTML = `<div class="grid grid-cols-5 gap-1 text-gray-500 border-b border-gray-800 pb-1 mb-1 text-[10px]">
      <span class="text-center">종목</span>
      <span class="text-center">수량</span>
      <span class="text-center">평단</span>
      <span class="text-center">현재</span>
      <span class="text-center">수익</span>
    </div>`;

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

      list.innerHTML += `
        <div class="grid grid-cols-5 gap-1 items-center text-[11px] py-1 border-b border-gray-900 cursor-pointer hover:bg-gray-800"
        onclick="prepareSell('${name}', ${qty}, '${iscd}', ${avgPrice})">
          <span class="font-bold text-white truncate text-center">${name}</span>
          <span class="font-mono text-gray-300 text-center">${qty.toLocaleString()}</span>
          <span class="font-mono text-center">₩ ${avgPrice.toLocaleString()}</span>
          <span class="font-mono text-center">₩ ${currentPrice.toLocaleString()}</span>
          <span class="${color} font-bold text-center">${profit.toFixed(2)}%</span>
        </div>`;

      chartSeries.push(currentPrice * qty);
      chartLabels.push(name);
    });

    donutChart.updateOptions({
      series: chartSeries,
      labels: chartLabels
    });

  } catch (error) {
    console.error("보유 종목 로딩 실패:", error);
  }
}

// ============================== 분봉 선택 ==============================
function updatePeriod(period, button) {
  document.querySelectorAll('.period-btn').forEach(btn => btn.classList.remove('active'));
  button.classList.add('active');
  fetchChartData(currentStockCode, period);
}

// ============================== watchList 검색 ==============================
function filterWatchlist(keyword) {
  const searchKeyword = keyword.toLowerCase().trim();
  const filtered = allStocks.filter(s =>
      (s.stck_shrn_iscd && s.stck_shrn_iscd.includes(searchKeyword)) ||
      (s.hts_kor_isnm && s.hts_kor_isnm.toLowerCase().includes(searchKeyword))
  );
  renderWatchlist(filtered);
}

// ============================== 매수/ 매도 ==============================
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
      setTimeout(async() => {
        await renderHoldings({ silent: true });
      }, 2500);
      document.getElementById('order-quantity').value = '';
    }
    await openModal(result.failMsg);
  }catch(error){
    console.error(error);
  }
}

// ============================== 매도 시 평단가 추가 출력 ==============================
async function prepareSell(name, quantity, code, avgPrice) {
  document.getElementById('order-stock-name').innerText = name;
  document.getElementById('order-stock-price').innerText = `(평단: ₩ ${avgPrice.toLocaleString()})`;
  document.getElementById('order-quantity').value = quantity;
  currentStockCode = code;
  document.getElementById('stock-title').innerText = name;

  const activeBtn = document.querySelector('.period-btn.active');
  const period = activeBtn ? activeBtn.innerText : 'day';
  await fetchChartData(code, period);
}

// ============================== 예수금 잔액 출력 ==============================
async function loadUserBalance() {
  try {
    const response = await fetch('/api/userBalance');
    const data = await response.json();
    if (data.balance !== undefined) {
      document.getElementById('available-balance').innerText = `₩ ${data.balance.toLocaleString()}`;
    }
  } catch (error) {
    console.error("예수금 로드 실패:", error);
  }
}

// ============================== kospi& kosdaq ==============================
async function updateMarketIndices(opts = {}) {
  try {
    const response = await fetch('/api/market-indices', { silent: opts.silent });
    if (!response.ok) throw new Error('네트워크 응답 오류');

    const data = await response.json();
    const latest = Array.isArray(data) ? data[0] : data;

    if (latest) {
      const indexContainer = document.getElementById('market-index-container');
      indexContainer.innerHTML = `
        <p>KOSPI <span class="text-green-400 font-mono">${latest.kospi.toLocaleString()}</span></p>
        <p>KOSDAQ <span class="text-red-500 font-mono">${latest.kosdaq.toLocaleString()}</span></p>
      `;
    }
  } catch (error) {
    console.error("지수 업데이트 실패:", error);
  }
}

// ============================== 이동평균선 계산 ==============================
function calculateMA(dayCount, data) {
  let result = [];
  for (let i = 0; i < data.length; i++) {
    if (i < dayCount - 1) {
      result.push({x: data[i].x, y: null});
    } else {
      let sum = 0;
      for (let j = 0; j < dayCount; j++) {
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
    await fetch('/api/logout', { method: 'POST' });
  } catch (e) {
    console.error("로그아웃 서버 처리 실패");
  } finally {
    localStorage.removeItem("accessToken");
    localStorage.removeItem("refreshToken");
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
document.addEventListener('DOMContentLoaded', async () => {
  try {
    showLoading();
    await Promise.all([
      fetchAndRender(),
      loadUserInfo(),
    ]);

    chart.updateSeries([{data: []}]);
    chart.render();
    donutChart.render();

    await Promise.all([
      fetchChartData("005930", "1D"),
      renderHoldings()
    ]);
  } finally {
    hideLoading();
  }

  setInterval(() => refreshWatchlist({ silent: true }), 50000);
  await updateMarketIndices({ silent: true });
  setInterval(() => updateMarketIndices({ silent: true }), 180000);
});