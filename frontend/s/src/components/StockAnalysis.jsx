import { useState, useEffect } from "react";
import Plot from "react-plotly.js";
import { API_BASE } from "../config";

const fetchStockData = async (symbol, period) => {
  try {
    const response = await fetch(`${API_BASE}/stock-data?symbol=${encodeURIComponent(symbol)}&period=${period}`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const contentType = response.headers.get("content-type") || "";
    if (!contentType.includes("application/json")) {
      throw new Error(
        `API returned HTML instead of JSON. Check VITE_API_BASE_URL (got ${API_BASE}).`
      );
    }
    
    const result = await response.json();

    if (!result.success) {
      const errorMsg = result.error || "Failed to fetch stock data";
      throw new Error(errorMsg);
    }

    if (result.success && Array.isArray(result.data) && result.data.length > 0) {
      return result.data;
    }
    throw new Error(`No data available for ${symbol}`);
  } catch (error) {
    console.error("❌ Stock API Error:", error.message);
    throw error;
  }
};

function StockAnalysis({ symbol1, symbol2, period, trigger }) {
  const [data1, setData1] = useState(null);
  const [data2, setData2] = useState(null);
  const [loading1, setLoading1] = useState(false);
  const [loading2, setLoading2] = useState(false);
  const [error1, setError1] = useState(null);
  const [error2, setError2] = useState(null);

  useEffect(() => {
    async function loadData() {
      if (!symbol1) return;

      // ✅ OPTIMIZED: Load both stocks in parallel for faster loading
      const loadPromises = [];

      // Load stock 1
      const loadStock1 = async () => {
        try {
          setLoading1(true);
          setError1(null);
          const d1 = await fetchStockData(symbol1, period);
          setData1(d1);
        } catch (err) {
          console.error("Error loading stock1:", err.message);
          setError1(err.message || `Failed to fetch data for ${symbol1}`);
          setData1(null);
        } finally {
          setLoading1(false);
        }
      };

      // Load stock 2 (if provided)
      const loadStock2 = async () => {
        if (symbol2 && symbol2.trim() && symbol2 !== symbol1) {
          try {
            setLoading2(true);
            setError2(null);
            const d2 = await fetchStockData(symbol2, period);
            setData2(d2);
          } catch (err) {
            console.error("Error loading stock2:", err.message);
            setError2(err.message || `Failed to fetch data for ${symbol2}`);
            setData2(null);
          } finally {
            setLoading2(false);
          }
        } else {
          setData2(null);
          setError2(null);
        }
      };

      // Load both in parallel
      loadPromises.push(loadStock1());
      if (symbol2 && symbol2.trim() && symbol2 !== symbol1) {
        loadPromises.push(loadStock2());
      }

      // Wait for all to complete
      await Promise.all(loadPromises);
    }

    loadData();
  }, [symbol1, symbol2, period, trigger]);

  const renderStockSection = (data, error, loading, symbol) => {
    if (loading) {
      return (
        <div className="flex items-center justify-center h-64 text-gray-400">
          Loading {symbol}...
        </div>
      );
    }
    if (error) {
      return (
        <div className="bg-red-500/10 border border-red-500/30 text-red-400 p-4 rounded-lg">
          {error}
        </div>
      );
    }
    if (!data || data.length === 0) {
      return (
        <div className="bg-blue-500/10 border border-blue-500/20 text-blue-300 p-4 rounded-xl">
          No data available
        </div>
      );
    }

    const latest = data[data.length - 1];
    const previous = data[data.length - 2];
    const priceChange = previous ? latest.Close - previous.Close : 0;
    const priceChangePct = previous
      ? ((priceChange / previous.Close) * 100).toFixed(2)
      : 0;
    const latestRSI = latest.RSI ? latest.RSI.toFixed(2) : "N/A";

    return (
      <div className="space-y-6">
        <h3 className="text-2xl font-bold text-white mb-4">{symbol}</h3>

        {/* Metrics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-[#0a0a0f] border border-gray-800 rounded-3xl p-4 hover:border-blue-500/30 transition">
            <div className="text-xs text-gray-400 mb-2 uppercase tracking-wider">
              Latest Price
            </div>
            <div className="text-2xl font-bold text-white mb-1">
              ₹{latest.Close.toFixed(2)}
            </div>
            <div
              className={`text-sm font-semibold ${
                priceChange >= 0 ? "text-green-400" : "text-red-400"
              }`}
            >
              {priceChange >= 0 ? "↑" : "↓"} {Math.abs(priceChangePct)}%
            </div>
          </div>

          <div className="bg-[#0a0a0f] border border-gray-800 rounded-3xl p-4 hover:border-blue-500/30 transition">
            <div className="text-xs text-gray-400 mb-2 uppercase tracking-wider">
              Data Points
            </div>
            <div className="text-2xl font-bold text-white">{data.length}</div>
          </div>

          <div className="bg-[#0a0a0f] border border-gray-800 rounded-3xl p-4 hover:border-blue-500/30 transition">
            <div className="text-xs text-gray-400 mb-2 uppercase tracking-wider">
              Latest RSI
            </div>
            <div className="text-2xl font-bold text-white">{latestRSI}</div>
          </div>
        </div>

        {/* Price Chart */}
        <div className="bg-[#0a0a0f] border border-gray-800 rounded-3xl p-4">
          <Plot
            data={[
              {
                x: data.map((d) => d.Date),
                y: data.map((d) => d.Close),
                type: "scatter",
                mode: "lines",
                name: `${symbol} Close`,
                line: { color: "#60a5fa", width: 2.5 },
              },
              {
                x: data.map((d) => d.Date),
                y: data.map((d) => d.MA20),
                type: "scatter",
                mode: "lines",
                name: "20-Day MA",
                line: { color: "#a78bfa", width: 2, dash: "dash" },
              },
            ]}
            layout={{
              title: {
                text: `${symbol} Stock Price`,
                font: { color: "#e5e7eb", size: 16 },
              },
              paper_bgcolor: "#0a0a0f",
              plot_bgcolor: "#0a0a0f",
              xaxis: {
                title: "Date",
                color: "#9ca3af",
                gridcolor: "#1f2937",
              },
              yaxis: {
                title: "Price (INR)",
                color: "#9ca3af",
                gridcolor: "#1f2937",
              },
              hovermode: "x unified",
              height: 400,
              margin: { t: 50, b: 50, l: 60, r: 20 },
              legend: {
                font: { color: "#9ca3af" },
                bgcolor: "rgba(0,0,0,0)",
              },
            }}
            config={{ responsive: true, displayModeBar: false }}
            style={{ width: "100%" }}
          />
        </div>

        {/* RSI Chart */}
        <div className="bg-[#0a0a0f] border border-gray-800 rounded-3xl p-4">
          <Plot
            data={[
              {
                x: data.map((d) => d.Date),
                y: data.map((d) => d.RSI),
                type: "scatter",
                mode: "lines",
                name: "RSI",
                line: { color: "#34d399", width: 2.5 },
              },
            ]}
            layout={{
              title: {
                text: `${symbol} RSI (Relative Strength Index)`,
                font: { color: "#e5e7eb", size: 16 },
              },
              paper_bgcolor: "#0a0a0f",
              plot_bgcolor: "#0a0a0f",
              xaxis: {
                title: "Date",
                color: "#9ca3af",
                gridcolor: "#1f2937",
              },
              yaxis: {
                title: "RSI Value",
                range: [0, 100],
                color: "#9ca3af",
                gridcolor: "#1f2937",
              },
              shapes: [
                {
                  type: "line",
                  y0: 70,
                  y1: 70,
                  xref: "paper",
                  x0: 0,
                  x1: 1,
                  line: { color: "#ef4444", dash: "dot", width: 2 },
                },
                {
                  type: "line",
                  y0: 30,
                  y1: 30,
                  xref: "paper",
                  x0: 0,
                  x1: 1,
                  line: { color: "#3b82f6", dash: "dot", width: 2 },
                },
                {
                  type: "line",
                  y0: 50,
                  y1: 50,
                  xref: "paper",
                  x0: 0,
                  x1: 1,
                  line: { color: "#6b7280", dash: "dot", width: 1 },
                },
              ],
              annotations: [
                {
                  x: 0.98,
                  y: 70,
                  xref: "paper",
                  yref: "y",
                  text: "Overbought (70)",
                  showarrow: false,
                  font: { color: "#ef4444", size: 10 },
                  xanchor: "right",
                },
                {
                  x: 0.98,
                  y: 30,
                  xref: "paper",
                  yref: "y",
                  text: "Oversold (30)",
                  showarrow: false,
                  font: { color: "#3b82f6", size: 10 },
                  xanchor: "right",
                },
              ],
              height: 350,
              margin: { t: 50, b: 50, l: 60, r: 20 },
              legend: {
                font: { color: "#9ca3af" },
                bgcolor: "rgba(0,0,0,0)",
              },
            }}
            config={{ responsive: true, displayModeBar: false }}
            style={{ width: "100%" }}
          />
        </div>
      </div>
    );
  };

  const renderComparison = () => {
    if (!data1 || !data2) {
      return (
        <div className="mt-8 pt-8 border-t border-gray-800">
          <h3 className="text-3xl font-bold text-white mb-6">
          Comparison Chart
          </h3>
          <div className="bg-[#0a0a0f] border border-gray-800 rounded-3xl p-8 text-center">
            <div className="text-cyan-400 text-5xl mb-4">📈</div>
            <p className="text-gray-400 text-lg">
              Enter a second stock symbol above to see side-by-side comparison
            </p>
            <p className="text-gray-500 text-sm mt-2">
              Compare price movements, trends, and correlations between two
              stocks
            </p>
          </div>
        </div>
      );
    }

    return (
      <div className="mt-8 pt-8 border-t border-gray-800">
        <h3 className="text-3xl font-bold text-white mb-6">
          📊 Comparison Chart
        </h3>
        <div className="bg-[#0a0a0f] border border-gray-800 rounded-3xl p-4">
          <Plot
            data={[
              {
                x: data1.map((d) => d.Date),
                y: data1.map((d) => d.Close),
                type: "scatter",
                mode: "lines",
                name: symbol1,
                line: { color: "#60a5fa", width: 2.5 },
              },
              {
                x: data2.map((d) => d.Date),
                y: data2.map((d) => d.Close),
                type: "scatter",
                mode: "lines",
                name: symbol2,
                line: { color: "#f472b6", width: 2.5 },
              },
            ]}
            layout={{
              title: {
                text: `${symbol1} vs ${symbol2}`,
                font: { color: "#e5e7eb", size: 18, weight: "bold" },
              },
              paper_bgcolor: "#0a0a0f",
              plot_bgcolor: "#0a0a0f",
              xaxis: {
                title: "Date",
                color: "#9ca3af",
                gridcolor: "#1f2937",
              },
              yaxis: {
                title: "Price (INR)",
                color: "#9ca3af",
                gridcolor: "#1f2937",
              },
              hovermode: "x unified",
              height: 450,
              margin: { t: 50, b: 50, l: 60, r: 20 },
              legend: {
                font: { color: "#9ca3af", size: 12 },
                bgcolor: "rgba(0,0,0,0)",
                orientation: "h",
                y: -0.15,
              },
            }}
            config={{ responsive: true, displayModeBar: false }}
            style={{ width: "100%" }}
          />
        </div>
      </div>
    );
  };

  return (
    <div>
      <h2 className="text-3xl font-bold bg-gradient-to-r from-neutral-100 via-cyan-100 to-neutral-100 bg-clip-text text-transparent mb-6">
        Stock Price & Technical Indicators
      </h2>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div>{renderStockSection(data1, error1, loading1, symbol1)}</div>

        <div>
          {symbol2 && symbol2 !== symbol1 ? (
            renderStockSection(data2, error2, loading2, symbol2)
          ) : (
            <div className="flex items-center justify-center h-full bg-[#0a0a0f] border border-gray-800 rounded-3xl text-gray-400 p-8 text-center">
              <div>
                <div className="text-4xl mb-3">💡</div>
                <p className="text-lg">Enter a second stock symbol above</p>
                <p className="text-sm text-gray-500 mt-2">
                  for side-by-side comparison
                </p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* COMPARISON CHART - Always rendered, shows placeholder when no data */}
      {renderComparison()}
    </div>
  );
}

export default StockAnalysis;