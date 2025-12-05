// Crypto Sentiment Analytics Dashboard - Main JavaScript

// Global variables
let cryptoData = {};
let sentimentData = {};
let correlationData = {};
let currentCrypto = "BTC";
let currentTimeframe = "1h";
let priceChart = null;
let sentimentGauge = null;

// Initialize dashboard
document.addEventListener("DOMContentLoaded", function () {
  loadData();
  initializeCharts();
  setupEventListeners();
  startRealTimeUpdates();
});

// Load data from JSON files
async function loadData() {
  try {
    const [cryptoResponse, sentimentResponse, correlationResponse] =
      await Promise.all([
        fetch("resources/data/crypto-prices.json"),
        fetch("resources/data/sentiment-data.json"),
        fetch("resources/data/correlation-data.json"),
      ]);

    cryptoData = await cryptoResponse.json();
    sentimentData = await sentimentResponse.json();
    correlationData = await correlationResponse.json();

    populateCryptoCards();
    updateMarketOverview();
    console.log("✅ Data loaded successfully");
  } catch (error) {
    console.error("❌ Error loading data:", error);
    // Use fallback data
    loadFallbackData();
  }
}

// Fallback data in case files can't be loaded
function loadFallbackData() {
  cryptoData = {
    cryptocurrencies: [
      {
        symbol: "BTC",
        name: "Bitcoin",
        price: 98750.32,
        change24h: 2.34,
        volume24h: 28500000000,
        marketCap: 1950000000000,
        volatility: 0.0234,
        sparkline: [
          98123, 98345, 98750, 98567, 98923, 98750, 99123, 98750, 98543, 98750,
        ],
        socialSentiment: 0.67,
        buzzVolume: 89432,
      },
      {
        symbol: "ETH",
        name: "Ethereum",
        price: 3456.78,
        change24h: -1.23,
        volume24h: 15600000000,
        marketCap: 415000000000,
        volatility: 0.0312,
        sparkline: [3456, 3423, 3456, 3489, 3456, 3434, 3456, 3478, 3456, 3456],
        socialSentiment: 0.45,
        buzzVolume: 56789,
      },
    ],
    marketOverview: {
      totalMarketCap: 2850000000000,
      totalVolume: 52300000000,
      btcDominance: 68.4,
      fearGreedIndex: 72,
      socialSentiment: 0.56,
    },
  };

  populateCryptoCards();
  updateMarketOverview();
}

// Initialize charts
function initializeCharts() {
  initializeSentimentGauge();
  initializePriceChart();
}

// Initialize sentiment gauge
function initializeSentimentGauge() {
  const gaugeElement = document.getElementById("sentiment-gauge");
  if (!gaugeElement) return;

  sentimentGauge = echarts.init(gaugeElement);

  const option = {
    backgroundColor: "transparent",
    series: [
      {
        name: "Sentiment",
        type: "gauge",
        min: -1,
        max: 1,
        splitNumber: 10,
        radius: "80%",
        center: ["50%", "60%"],
        axisLine: {
          lineStyle: {
            width: 30,
            color: [
              [0.3, "#ef4444"],
              [0.7, "#f59e0b"],
              [1, "#10b981"],
            ],
          },
        },
        pointer: {
          itemStyle: {
            color: "#00d4ff",
          },
        },
        axisTick: {
          distance: -30,
          length: 8,
          lineStyle: {
            color: "#fff",
            width: 2,
          },
        },
        splitLine: {
          distance: -30,
          length: 30,
          lineStyle: {
            color: "#fff",
            width: 4,
          },
        },
        axisLabel: {
          color: "#e5e7eb",
          distance: 40,
          fontSize: 12,
          formatter: function (value) {
            if (value === -1) return "Very Negative";
            if (value === -0.5) return "Negative";
            if (value === 0) return "Neutral";
            if (value === 0.5) return "Positive";
            if (value === 1) return "Very Positive";
            return "";
          },
        },
        detail: {
          valueAnimation: true,
          formatter: "{value}",
          color: "#00d4ff",
          fontSize: 24,
          offsetCenter: [0, "70%"],
        },
        data: [
          {
            value: sentimentData.sentimentOverview
              ? sentimentData.sentimentOverview.overallSentiment
              : 0.67,
            name: "Market Sentiment",
          },
        ],
      },
    ],
  };

  sentimentGauge.setOption(option);
}

// Initialize price chart
function initializePriceChart() {
  const chartElement = document.getElementById("price-chart");
  if (!chartElement) return;

  priceChart = echarts.init(chartElement);
  updatePriceChart();
}

// Update price chart based on selected crypto
function updatePriceChart() {
  if (!priceChart || !cryptoData.cryptocurrencies) return;

  const crypto = cryptoData.cryptocurrencies.find(
    (c) => c.symbol === currentCrypto
  );
  if (!crypto) return;

  // Generate sample price data
  const basePrice = crypto.price;
  const data = [];
  const now = new Date();

  for (let i = 99; i >= 0; i--) {
    const time = new Date(now.getTime() - i * 60000); // 1 minute intervals
    const variation = (Math.random() - 0.5) * crypto.volatility * basePrice;
    const price = basePrice + variation;
    data.push([time.toISOString(), price.toFixed(2)]);
  }

  const option = {
    backgroundColor: "transparent",
    title: {
      text: `${crypto.name} Price Chart`,
      textStyle: {
        color: "#e5e7eb",
        fontSize: 18,
      },
    },
    tooltip: {
      trigger: "axis",
      backgroundColor: "#1f2937",
      borderColor: "#374151",
      textStyle: {
        color: "#e5e7eb",
      },
      formatter: function (params) {
        const date = new Date(params[0].value[0]);
        const price = parseFloat(params[0].value[1]);
        return `${date.toLocaleString()}<br/>Price: $${price.toLocaleString()}`;
      },
    },
    grid: {
      left: "3%",
      right: "4%",
      bottom: "3%",
      containLabel: true,
    },
    xAxis: {
      type: "time",
      axisLine: {
        lineStyle: {
          color: "#374151",
        },
      },
      axisLabel: {
        color: "#9ca3af",
      },
    },
    yAxis: {
      type: "value",
      axisLine: {
        lineStyle: {
          color: "#374151",
        },
      },
      axisLabel: {
        color: "#9ca3af",
        formatter: "${value}",
      },
      splitLine: {
        lineStyle: {
          color: "#374151",
        },
      },
    },
    series: [
      {
        name: "Price",
        type: "line",
        data: data,
        smooth: true,
        lineStyle: {
          color: "#00d4ff",
          width: 2,
        },
        areaStyle: {
          color: {
            type: "linear",
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              {
                offset: 0,
                color: "rgba(0, 212, 255, 0.3)",
              },
              {
                offset: 1,
                color: "rgba(0, 212, 255, 0.05)",
              },
            ],
          },
        },
        symbol: "none",
      },
    ],
  };

  priceChart.setOption(option);
}

// Populate cryptocurrency cards
function populateCryptoCards() {
  const container = document.getElementById("crypto-cards");
  if (!container || !cryptoData.cryptocurrencies) return;

  container.innerHTML = "";

  cryptoData.cryptocurrencies.forEach((crypto) => {
    const changeColor =
      crypto.change24h >= 0 ? "text-emerald-400" : "text-red-400";
    const changeIcon = crypto.change24h >= 0 ? "↗" : "↘";

    const card = document.createElement("div");
    card.className =
      "bg-gray-900 rounded-xl p-6 card-hover border border-gray-700 cursor-pointer";
    card.onclick = () => selectCrypto(crypto.symbol);

    card.innerHTML = `
            <div class="flex items-center justify-between mb-4">
                <div class="flex items-center space-x-3">
                    <div class="w-10 h-10 bg-gradient-to-r from-blue-500 to-emerald-500 rounded-full flex items-center justify-center">
                        <span class="text-white font-bold text-sm">${
                          crypto.symbol
                        }</span>
                    </div>
                    <div>
                        <h3 class="font-bold text-lg">${crypto.name}</h3>
                        <p class="text-gray-400 text-sm">${crypto.symbol}</p>
                    </div>
                </div>
                <div class="text-right">
                    <p class="text-2xl font-bold">$${crypto.price.toLocaleString()}</p>
                    <p class="${changeColor} text-sm">${changeIcon} ${Math.abs(
      crypto.change24h
    )}%</p>
                </div>
            </div>
            
            <div class="grid grid-cols-2 gap-4 mb-4">
                <div>
                    <p class="text-gray-400 text-sm">Market Cap</p>
                    <p class="font-semibold">$${(
                      crypto.marketCap / 1000000000
                    ).toFixed(2)}B</p>
                </div>
                <div>
                    <p class="text-gray-400 text-sm">24h Volume</p>
                    <p class="font-semibold">$${(
                      crypto.volume24h / 1000000000
                    ).toFixed(2)}B</p>
                </div>
            </div>
            
            <div class="mb-4">
                <div class="flex justify-between items-center mb-2">
                    <span class="text-gray-400 text-sm">Volatility</span>
                    <span class="text-sm">${(crypto.volatility * 100).toFixed(
                      2
                    )}%</span>
                </div>
                <div class="w-full bg-gray-700 rounded-full h-2">
                    <div class="bg-gradient-to-r from-blue-400 to-emerald-400 h-2 rounded-full" style="width: ${Math.min(
                      crypto.volatility * 1000,
                      100
                    )}%"></div>
                </div>
            </div>
            
            <div class="flex justify-between items-center">
                <div>
                    <p class="text-gray-400 text-sm">Social Sentiment</p>
                    <p class="font-semibold ${
                      crypto.socialSentiment >= 0
                        ? "text-emerald-400"
                        : "text-red-400"
                    }">
                        ${
                          crypto.socialSentiment >= 0 ? "+" : ""
                        }${crypto.socialSentiment.toFixed(2)}
                    </p>
                </div>
                <div>
                    <p class="text-gray-400 text-sm">Buzz Volume</p>
                    <p class="font-semibold text-blue-400">${crypto.buzzVolume.toLocaleString()}</p>
                </div>
            </div>
        `;

    container.appendChild(card);
  });
}

// Update market overview
function updateMarketOverview() {
  if (!cryptoData.marketOverview) return;

  const overview = cryptoData.marketOverview;

  document.getElementById("total-market-cap").textContent = `$${(
    overview.totalMarketCap / 1000000000000
  ).toFixed(2)}T`;
  document.getElementById("total-volume").textContent = `$${(
    overview.totalVolume / 1000000000
  ).toFixed(1)}B`;
  document.getElementById(
    "btc-dominance"
  ).textContent = `${overview.btcDominance}%`;
  document.getElementById("fear-greed").textContent = overview.fearGreedIndex;
}

// Setup event listeners
function setupEventListeners() {
  // Crypto selector buttons
  document.querySelectorAll(".crypto-btn").forEach((btn) => {
    btn.addEventListener("click", function () {
      document.querySelectorAll(".crypto-btn").forEach((b) => {
        b.classList.remove("active", "bg-blue-500", "text-white");
        b.classList.add("bg-gray-700", "text-gray-300");
      });

      this.classList.add("active", "bg-blue-500", "text-white");
      this.classList.remove("bg-gray-700", "text-gray-300");

      currentCrypto = this.dataset.crypto;
      updateSelectedCrypto();
      updatePriceChart();
    });
  });

  // Timeframe buttons
  document.querySelectorAll(".time-btn").forEach((btn) => {
    btn.addEventListener("click", function () {
      document.querySelectorAll(".time-btn").forEach((b) => {
        b.classList.remove("active", "bg-blue-500", "text-white");
        b.classList.add("bg-gray-700", "text-gray-300");
      });

      this.classList.add("active", "bg-blue-500", "text-white");
      this.classList.remove("bg-gray-700", "text-gray-300");

      currentTimeframe = this.dataset.time;
      updatePriceChart();
    });
  });

  // Mobile menu
  const mobileMenuBtn = document.getElementById("mobile-menu-btn");
  if (mobileMenuBtn) {
    mobileMenuBtn.addEventListener("click", function () {
      // Toggle mobile menu (implement if needed)
      console.log("Mobile menu clicked");
    });
  }
}

// Select cryptocurrency
function selectCrypto(symbol) {
  currentCrypto = symbol;

  // Update active button
  document.querySelectorAll(".crypto-btn").forEach((btn) => {
    btn.classList.remove("active", "bg-blue-500", "text-white");
    btn.classList.add("bg-gray-700", "text-gray-300");
    if (btn.dataset.crypto === symbol) {
      btn.classList.add("active", "bg-blue-500", "text-white");
      btn.classList.remove("bg-gray-700", "text-gray-300");
    }
  });

  updateSelectedCrypto();
  updatePriceChart();
}

// Update selected crypto display
function updateSelectedCrypto() {
  if (!cryptoData.cryptocurrencies) return;

  const crypto = cryptoData.cryptocurrencies.find(
    (c) => c.symbol === currentCrypto
  );
  if (!crypto) return;

  document.getElementById("selected-crypto-name").textContent = crypto.name;
  document.getElementById("selected-crypto-symbol").textContent = crypto.symbol;
}

// Start real-time updates
function startRealTimeUpdates() {
  // Update all data every 10 seconds to match backend update frequency
  setInterval(() => {
    console.log("🔄 Auto-updating with real data...");
    loadData(); // Reload all JSON data files for real updates
    updatePrices(); // Update price displays
    updateSentiment(); // Update sentiment gauge
  }, 10000); // Changed from 120000ms (120s) to 10000ms (10s)
}

// Update prices with real data changes
function updatePrices() {
  if (!cryptoData.cryptocurrencies) return;

  // Real data is already updated by loadData()
  populateCryptoCards();
  updatePriceChart();
}

// Update sentiment with real data changes
function updateSentiment() {
  if (!sentimentData.sentimentOverview) return;

  // Real sentiment data is already updated by loadData()
  // Update gauge with current sentiment
  if (sentimentGauge) {
    sentimentGauge.setOption({
      series: [
        {
          data: [
            {
              value: sentimentData.sentimentOverview.overallSentiment,
              name: "Market Sentiment",
            },
          ],
        },
      ],
    });
  }
}

// Utility functions
function scrollToSection(sectionId) {
  const element = document.getElementById(sectionId);
  if (element) {
    element.scrollIntoView({ behavior: "smooth" });
  }
}

// Handle window resize
window.addEventListener("resize", function () {
  if (priceChart) {
    priceChart.resize();
  }
  if (sentimentGauge) {
    sentimentGauge.resize();
  }
});

// Animation utilities
function animateValue(element, start, end, duration) {
  const startTime = performance.now();

  function update(currentTime) {
    const elapsed = currentTime - startTime;
    const progress = Math.min(elapsed / duration, 1);

    const current = start + (end - start) * progress;
    element.textContent = Math.round(current).toLocaleString();

    if (progress < 1) {
      requestAnimationFrame(update);
    }
  }

  requestAnimationFrame(update);
}

// Export functions for other pages
window.CryptoDashboard = {
  loadData,
  updatePrices,
  updateSentiment,
  cryptoData,
  sentimentData,
  correlationData,
};
