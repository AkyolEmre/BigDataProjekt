// CryptoSentiment Analytics Dashboard - Enhanced Main.js
// Big Data Analytics Final Project

let cryptoData = {};
let currentCrypto = "BTC";
let currentTimeframe = "24h";
let priceChart = null;
let sentimentGauge = null;
let lastUpdateTime = null;

const CRYPTO_COLORS = { BTC: '#f7931a', ETH: '#627eea', XRP: '#23292f', SOL: '#00ffa3', DOGE: '#c2a633', ADA: '#0033ad' };

document.addEventListener("DOMContentLoaded", function () {
  showLoadingIndicator();
  loadData();
  initializeCharts();
  setupEventListeners();
  startRealTimeUpdates();
});

function showLoadingIndicator() {
  const indicator = document.createElement('div');
  indicator.id = 'update-indicator';
  indicator.className = 'fixed top-20 right-4 bg-blue-600 text-white px-4 py-2 rounded-lg shadow-lg z-50 flex items-center space-x-2';
  indicator.innerHTML = '<div class="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div><span>Loading live data...</span>';
  document.body.appendChild(indicator);
}

function updateIndicator(status, message) {
  const indicator = document.getElementById('update-indicator');
  if (!indicator) return;
  const configs = {
    success: { bg: 'bg-emerald-600', icon: '<svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/></svg>' },
    loading: { bg: 'bg-blue-600', icon: '<div class="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>' },
    error: { bg: 'bg-red-600', icon: '<svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/></svg>' }
  };
  const config = configs[status] || configs.loading;
  indicator.className = `fixed top-20 right-4 ${config.bg} text-white px-4 py-2 rounded-lg shadow-lg z-50 flex items-center space-x-2`;
  indicator.innerHTML = `${config.icon}<span>${message}</span>`;
  if (status === 'success') setTimeout(() => { indicator.style.opacity = '0.7'; }, 3000);
  else indicator.style.opacity = '1';
}

async function loadData() {
  try {
    updateIndicator('loading', 'Fetching live data...');
    const response = await fetch(`resources/data/crypto-prices.json?t=${Date.now()}`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    cryptoData = await response.json();
    lastUpdateTime = new Date(cryptoData.metadata?.lastUpdate || Date.now());
    populateCryptoCards();
    updateMarketOverview();
    updateCharts();
    updateDataStatus();
    updateIndicator('success', `Updated ${getTimeAgo(lastUpdateTime)}`);
  } catch (error) {
    console.error("Error loading data:", error);
    updateIndicator('error', 'Failed to load data');
  }
}

function getTimeAgo(date) {
  const seconds = Math.floor((new Date() - date) / 1000);
  if (seconds < 10) return "just now";
  if (seconds < 60) return `${seconds}s ago`;
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  return date.toLocaleDateString();
}

function formatPrice(price) {
  if (!price) return '$0.00';
  if (price >= 1000) return `$${price.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
  if (price >= 1) return `$${price.toFixed(2)}`;
  if (price >= 0.01) return `$${price.toFixed(4)}`;
  return `$${price.toFixed(6)}`;
}

function updateDataStatus() {
  const statusEl = document.getElementById('data-status');
  if (statusEl && lastUpdateTime) statusEl.textContent = `Last updated: ${getTimeAgo(lastUpdateTime)}`;
}

function initializeCharts() {
  const gaugeEl = document.getElementById("sentiment-gauge");
  if (gaugeEl) { sentimentGauge = echarts.init(gaugeEl); window.addEventListener("resize", () => sentimentGauge?.resize()); }
  const chartEl = document.getElementById("price-chart");
  if (chartEl) { priceChart = echarts.init(chartEl); window.addEventListener("resize", () => priceChart?.resize()); }
}

function updateCharts() { updateSentimentGauge(); updatePriceChart(); }

function updateSentimentGauge() {
  if (!sentimentGauge || !cryptoData.marketOverview) return;
  const value = cryptoData.marketOverview.socialSentiment || 0;
  sentimentGauge.setOption({
    backgroundColor: 'transparent',
    series: [{
      type: "gauge", min: -1, max: 1, splitNumber: 4, radius: "85%",
      axisLine: { lineStyle: { width: 20, color: [[0.2, "#ef4444"], [0.4, "#f97316"], [0.6, "#fbbf24"], [0.8, "#84cc16"], [1, "#10b981"]] } },
      pointer: { width: 6, length: '60%', itemStyle: { color: '#fff' } },
      axisTick: { show: false },
      splitLine: { length: 15, lineStyle: { color: '#374151', width: 2 } },
      axisLabel: { distance: 25, color: "#9ca3af", fontSize: 11, formatter: (v) => ({ '-1': 'Fear', '0': 'Neutral', '1': 'Greed' }[v.toString()] || '') },
      detail: { valueAnimation: true, formatter: (v) => v.toFixed(2), color: "#fff", fontSize: 28, fontWeight: 'bold', offsetCenter: [0, '75%'] },
      data: [{ value }]
    }]
  });
}

function updatePriceChart() {
  if (!priceChart || !cryptoData.cryptocurrencies) return;
  const crypto = cryptoData.cryptocurrencies.find(c => c.symbol === currentCrypto);
  if (!crypto || !crypto.sparkline?.length) return;
  
  const hours = { '1h': 12, '4h': 4, '24h': 24, '7d': 168, '30d': 720 };
  let hoursToShow = Math.min(hours[currentTimeframe] || 24, crypto.sparkline.length);
  const prices = crypto.sparkline.slice(-hoursToShow);
  const times = (crypto.sparkline_timestamps || []).slice(-hoursToShow);
  const data = prices.map((p, i) => [times[i] || new Date(Date.now() - (hoursToShow - i) * 3600000).toISOString(), p]);
  
  const min = Math.min(...prices), max = Math.max(...prices);
  const pad = (max - min) === 0 ? max * 0.01 : (max - min) * 0.1;
  const color = CRYPTO_COLORS[currentCrypto] || '#00d4ff';
  
  priceChart.setOption({
    backgroundColor: "transparent",
    tooltip: { trigger: "axis", backgroundColor: "#1f2937", borderColor: "#374151", textStyle: { color: "#fff" }, formatter: (p) => `<b>${new Date(p[0].value[0]).toLocaleString()}</b><br/>Price: ${formatPrice(p[0].value[1])}` },
    grid: { left: "12%", right: "5%", top: "10%", bottom: "15%" },
    xAxis: { type: "time", axisLabel: { color: "#9ca3af", fontSize: 11 }, splitLine: { show: false }, axisLine: { lineStyle: { color: '#374151' } } },
    yAxis: { type: "value", min: min - pad, max: max + pad, axisLabel: { color: "#9ca3af", fontSize: 11, formatter: (v) => formatPrice(v).replace('$', '') }, splitLine: { lineStyle: { color: "#374151", type: 'dashed' } }, axisLine: { show: false } },
    series: [{ data, type: "line", smooth: true, showSymbol: hoursToShow <= 24, symbolSize: 6, lineStyle: { width: 3, color }, itemStyle: { color }, areaStyle: { color: { type: "linear", x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: color + '40' }, { offset: 1, color: color + '05' }] } } }]
  }, { notMerge: true });
}

function populateCryptoCards() {
  const container = document.getElementById("crypto-cards");
  if (!container || !cryptoData.cryptocurrencies) return;
  container.innerHTML = "";
  
  cryptoData.cryptocurrencies.forEach((crypto) => {
    const card = document.createElement("div");
    const isSelected = crypto.symbol === currentCrypto;
    const color = CRYPTO_COLORS[crypto.symbol] || '#6b7280';
    const changeColor = crypto.change24h >= 0 ? "text-emerald-400" : "text-red-400";
    
    card.className = `bg-gray-900 rounded-xl p-6 card-hover border cursor-pointer transition-all ${isSelected ? 'border-blue-500 ring-2 ring-blue-500/30' : 'border-gray-700 hover:border-gray-600'}`;
    card.onclick = () => selectCrypto(crypto.symbol);
    
    card.innerHTML = `
      <div class="flex items-center justify-between mb-4">
        <div class="flex items-center space-x-3">
          <div class="w-10 h-10 rounded-full flex items-center justify-center" style="background: ${color}20; border: 2px solid ${color}">
            <span class="font-bold text-sm" style="color: ${color}">${crypto.symbol.charAt(0)}</span>
          </div>
          <div><h3 class="font-bold text-lg text-white">${crypto.name}</h3><span class="text-gray-400 text-sm">${crypto.symbol}</span></div>
        </div>
      </div>
      <div class="flex justify-between items-end">
        <div>
          <p class="text-2xl font-bold text-white">${formatPrice(crypto.price)}</p>
          <p class="${changeColor} text-sm font-medium mt-1">${crypto.change24h >= 0 ? '↑' : '↓'} ${crypto.change24h >= 0 ? '+' : ''}${crypto.change24h.toFixed(2)}%</p>
        </div>
        <div class="text-right"><p class="text-xs text-gray-500">Volatility</p><p class="text-sm font-medium text-yellow-400">${(crypto.volatility * 100).toFixed(2)}%</p></div>
      </div>
      <div class="mt-4">
        <div class="flex justify-between text-xs text-gray-500 mb-1"><span>Sentiment</span><span>${(crypto.socialSentiment * 100).toFixed(0)}%</span></div>
        <div class="w-full bg-gray-700 rounded-full h-2"><div class="h-2 rounded-full" style="width: ${Math.min(Math.abs(crypto.socialSentiment * 100), 100)}%; background: ${crypto.socialSentiment >= 0 ? '#10b981' : '#ef4444'}"></div></div>
      </div>`;
    container.appendChild(card);
  });
}

function selectCrypto(symbol) {
  currentCrypto = symbol;
  const crypto = cryptoData.cryptocurrencies?.find(c => c.symbol === symbol);
  if (crypto) {
    const nameEl = document.getElementById("selected-crypto-name");
    const symbolEl = document.getElementById("selected-crypto-symbol");
    if (nameEl) nameEl.textContent = crypto.name;
    if (symbolEl) symbolEl.textContent = crypto.symbol;
  }
  document.querySelectorAll(".crypto-btn").forEach(btn => {
    const isActive = btn.dataset.crypto === symbol;
    btn.className = `crypto-btn ${isActive ? 'active bg-blue-500 text-white' : 'bg-gray-700 text-gray-300 hover:bg-gray-600'} px-4 py-2 rounded-lg font-medium`;
  });
  updatePriceChart();
  populateCryptoCards();
}

function updateMarketOverview() {
  if (!cryptoData.marketOverview) return;
  const mo = cryptoData.marketOverview;
  const els = { 'total-market-cap': `$${(mo.totalMarketCap / 1e12).toFixed(2)}T`, 'total-volume': `$${(mo.totalVolume / 1e9).toFixed(1)}B`, 'btc-dominance': `${mo.btcDominance}%`, 'fear-greed': mo.fearGreedIndex };
  Object.entries(els).forEach(([id, val]) => { const el = document.getElementById(id); if (el) el.textContent = val; });
  const fgLabel = document.getElementById("fear-greed-label");
  if (fgLabel) {
    const fg = mo.fearGreedIndex;
    fgLabel.textContent = fg <= 25 ? "Extreme Fear" : fg <= 45 ? "Fear" : fg <= 55 ? "Neutral" : fg <= 75 ? "Greed" : "Extreme Greed";
  }
}

function setupEventListeners() {
  document.querySelectorAll(".crypto-btn").forEach(btn => btn.addEventListener("click", (e) => selectCrypto(e.target.dataset.crypto)));
  document.querySelectorAll(".time-btn").forEach(btn => btn.addEventListener("click", (e) => {
    document.querySelectorAll(".time-btn").forEach(b => b.className = 'time-btn bg-gray-700 text-gray-300 px-3 py-1 rounded text-sm hover:bg-gray-600');
    e.target.className = 'time-btn active bg-blue-500 text-white px-3 py-1 rounded text-sm';
    currentTimeframe = e.target.dataset.time.toLowerCase();
    updatePriceChart();
  }));
}

function startRealTimeUpdates() {
  setInterval(() => loadData(), 120000);
  setInterval(() => {
    updateDataStatus();
    const indicator = document.getElementById('update-indicator');
    if (indicator && lastUpdateTime && indicator.classList.contains('bg-emerald-600')) {
      const span = indicator.querySelector('span');
      if (span) span.textContent = `Updated ${getTimeAgo(lastUpdateTime)}`;
    }
  }, 10000);
}

function scrollToSection(id) { document.getElementById(id)?.scrollIntoView({ behavior: "smooth" }); }

window.CryptoDashboard = { loadData, selectCrypto, cryptoData: () => cryptoData, formatPrice, getTimeAgo };