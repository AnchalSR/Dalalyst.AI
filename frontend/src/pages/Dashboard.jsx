import { lazy, startTransition, Suspense, useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import LoadingPanel from '../components/LoadingPanel';
import { apiRequest, clearSession, getStoredUser } from '../lib/api';
import {
  INDIAN_SYMBOL_SUGGESTIONS,
  normalizeIndianSymbol,
  normalizeIndianSymbolList,
} from '../lib/indianMarket';
import ChatModule from '../modules/ChatModule';
import RadarModule from '../modules/RadarModule';

const ChartModule = lazy(() => import('../modules/ChartModule'));
const VideoModule = lazy(() => import('../modules/VideoModule'));

const TAB_LABELS = {
  radar: 'Opportunity Radar',
  chart: 'Chart Intelligence',
  chat: 'Market Chat',
  video: 'Video Engine',
};

const DEFAULT_WATCHLIST = 'RELIANCE.NS,TCS.NS,INFY.NS,HDFCBANK.NS,ICICIBANK.NS';

export default function Dashboard() {
  const navigate = useNavigate();
  const [user, setUser] = useState(getStoredUser());
  const [activeTab, setActiveTab] = useState('radar');
  const [pageError, setPageError] = useState('');

  const [watchlistInput, setWatchlistInput] = useState(DEFAULT_WATCHLIST);
  const [radarBusy, setRadarBusy] = useState(false);
  const [radarData, setRadarData] = useState({ alerts: [], summary: { buy: 0, watch: 0, avoid: 0 } });
  const [savedAlerts, setSavedAlerts] = useState([]);
  const [portfolioData, setPortfolioData] = useState(null);
  const [portfolioInput, setPortfolioInput] = useState('');
  const [portfolioBusy, setPortfolioBusy] = useState(false);

  const [chartSymbol, setChartSymbol] = useState('RELIANCE.NS');
  const [chartBusy, setChartBusy] = useState(false);
  const [chartData, setChartData] = useState(null);

  const [chatSymbol, setChatSymbol] = useState('RELIANCE.NS');
  const [chatInput, setChatInput] = useState('');
  const [chatBusy, setChatBusy] = useState(false);
  const [chatHistory, setChatHistory] = useState([]);

  const [videoSymbol, setVideoSymbol] = useState('TCS.NS');
  const [videoBusy, setVideoBusy] = useState(false);
  const [videoData, setVideoData] = useState(null);

  function handleUnauthorized() {
    clearSession();
    navigate('/login', { replace: true });
  }

  async function runProtectedRequest(work) {
    try {
      return await work();
    } catch (error) {
      if (error.status === 401) {
        handleUnauthorized();
        return null;
      }
      setPageError(error.message);
      return null;
    }
  }

  async function loadProfile() {
    const profile = await runProtectedRequest(() => apiRequest('/auth/me', { auth: true }));
    if (profile) {
      setUser(profile);
    }
  }

  async function loadRadar() {
    setRadarBusy(true);
    setPageError('');
    let normalizedWatchlist;
    try {
      normalizedWatchlist = normalizeIndianSymbolList(watchlistInput);
    } catch (error) {
      setPageError(error.message);
      setRadarBusy(false);
      return;
    }

    setWatchlistInput(normalizedWatchlist);
    const query = new URLSearchParams({ symbols: normalizedWatchlist });
    const payload = await runProtectedRequest(() =>
      Promise.all([
        apiRequest(`/radar/alerts?${query.toString()}`, { auth: true }),
        apiRequest('/radar/saved', { auth: true }),
      ]),
    );
    if (payload) {
      setRadarData(payload[0]);
      setSavedAlerts(payload[1].alerts || []);
    }
    setRadarBusy(false);
  }

  async function loadPortfolio() {
    const payload = await runProtectedRequest(() => apiRequest('/radar/portfolio', { auth: true }));
    if (payload) {
      setPortfolioData(payload);
    }
  }

  async function loadChart(symbol = chartSymbol) {
    setChartBusy(true);
    setPageError('');
    try {
      const normalizedSymbol = normalizeIndianSymbol(symbol);
      setChartSymbol(normalizedSymbol);
      const payload = await apiRequest(`/chart/analyze?symbol=${encodeURIComponent(normalizedSymbol)}`);
      setChartData(payload);
    } catch (error) {
      setPageError(error.message);
    }
    setChartBusy(false);
  }

  async function loadChatHistory() {
    const payload = await runProtectedRequest(() => apiRequest('/chat/history', { auth: true }));
    if (payload) {
      setChatHistory(payload.messages || []);
    }
  }

  async function sendMessage(event) {
    event.preventDefault();
    if (!chatInput.trim()) {
      return;
    }

    setChatBusy(true);
    setPageError('');
    let normalizedSymbol = null;
    try {
      normalizedSymbol = chatSymbol.trim() ? normalizeIndianSymbol(chatSymbol) : null;
      if (normalizedSymbol) {
        setChatSymbol(normalizedSymbol);
      }
    } catch (error) {
      setPageError(error.message);
      setChatBusy(false);
      return;
    }

    const payload = await runProtectedRequest(() =>
      apiRequest('/chat/message', {
        method: 'POST',
        auth: true,
        body: {
          message: chatInput,
          symbol: normalizedSymbol,
        },
      }),
    );
    if (payload) {
      setChatHistory((current) => [...current, payload.saved_message]);
      setChatInput('');
    }
    setChatBusy(false);
  }

  async function generateVideo() {
    setVideoBusy(true);
    setPageError('');
    let normalizedSymbol;
    try {
      normalizedSymbol = normalizeIndianSymbol(videoSymbol);
      setVideoSymbol(normalizedSymbol);
    } catch (error) {
      setPageError(error.message);
      setVideoBusy(false);
      return;
    }

    const payload = await runProtectedRequest(() =>
      apiRequest(`/video/generate?symbol=${encodeURIComponent(normalizedSymbol)}`, { auth: true }),
    );
    if (payload) {
      setVideoData(payload);
    }
    setVideoBusy(false);
  }

  async function addPortfolioStock(event) {
    event.preventDefault();
    if (!portfolioInput.trim()) {
      return;
    }

    setPortfolioBusy(true);
    setPageError('');
    let normalizedStock;
    try {
      normalizedStock = normalizeIndianSymbol(portfolioInput);
      setPortfolioInput(normalizedStock);
    } catch (error) {
      setPageError(error.message);
      setPortfolioBusy(false);
      return;
    }

    const payload = await runProtectedRequest(() =>
      apiRequest('/radar/portfolio', {
        method: 'POST',
        auth: true,
        body: { stock: normalizedStock },
      }),
    );
    if (payload) {
      setPortfolioInput('');
      await loadPortfolio();
    }
    setPortfolioBusy(false);
  }

  async function removePortfolioStock(stock) {
    setPortfolioBusy(true);
    setPageError('');
    const payload = await runProtectedRequest(() =>
      apiRequest(`/radar/portfolio/${encodeURIComponent(stock)}`, {
        method: 'DELETE',
        auth: true,
      }),
    );
    if (payload) {
      await loadPortfolio();
    }
    setPortfolioBusy(false);
  }

  useEffect(() => {
    loadProfile();
    loadRadar();
    loadPortfolio();
    loadChart();
    loadChatHistory();
  }, []);

  const chatTurns = useMemo(() => {
    const turns = [];
    chatHistory.forEach((entry) => {
      turns.push({
        id: `${entry.id}-user`,
        role: 'user',
        text: entry.message,
        symbol: entry.symbol,
        timestamp: entry.timestamp,
      });
      turns.push({
        id: `${entry.id}-assistant`,
        role: 'assistant',
        text: entry.response,
        symbol: entry.symbol,
        timestamp: entry.timestamp,
      });
    });
    return turns;
  }, [chatHistory]);

  return (
    <div className="dashboard-shell">
      <div className="dashboard-header">
        <div>
          <p className="eyebrow">Production-ready workspace</p>
          <h1 className="dashboard-title">AI Investor Platform</h1>
          <p className="hero-copy">
            Groq + LLaMA 3 reasoning layered on top of Indian market data, explainable scoring,
            portfolio intelligence, and persistent NSE investor chat.
          </p>
        </div>

        <div className="header-actions">
          <div className="user-chip">
            <span className="muted-copy">Signed in as</span>
            <strong>{user?.email || 'Investor'}</strong>
          </div>
          <button
            className="secondary-button"
            onClick={() => {
              clearSession();
              navigate('/login', { replace: true });
            }}
          >
            Logout
          </button>
        </div>
      </div>

      <div className="tab-strip">
        {Object.entries(TAB_LABELS).map(([key, label]) => (
          <button
            key={key}
            className={`tab-button ${activeTab === key ? 'tab-active' : ''}`}
            onClick={() => startTransition(() => setActiveTab(key))}
          >
            {label}
          </button>
        ))}
      </div>

      {pageError ? <p className="error-banner">{pageError}</p> : null}

      {activeTab === 'radar' ? (
        <RadarModule
          watchlistInput={watchlistInput}
          setWatchlistInput={setWatchlistInput}
          radarBusy={radarBusy}
          radarData={radarData}
          savedAlerts={savedAlerts}
          loadRadar={loadRadar}
          suggestions={INDIAN_SYMBOL_SUGGESTIONS}
          portfolioData={portfolioData}
          portfolioInput={portfolioInput}
          setPortfolioInput={setPortfolioInput}
          addPortfolioStock={addPortfolioStock}
          removePortfolioStock={removePortfolioStock}
          portfolioBusy={portfolioBusy}
        />
      ) : null}

      {activeTab === 'chart' ? (
        <Suspense fallback={<LoadingPanel label="Loading chart intelligence..." />}>
          <ChartModule
            chartSymbol={chartSymbol}
            setChartSymbol={setChartSymbol}
            chartBusy={chartBusy}
            chartData={chartData}
            loadChart={loadChart}
            suggestions={INDIAN_SYMBOL_SUGGESTIONS}
          />
        </Suspense>
      ) : null}

      {activeTab === 'chat' ? (
        <ChatModule
          chatTurns={chatTurns}
          chatSymbol={chatSymbol}
          setChatSymbol={setChatSymbol}
          chatInput={chatInput}
          setChatInput={setChatInput}
          chatBusy={chatBusy}
          sendMessage={sendMessage}
          suggestions={INDIAN_SYMBOL_SUGGESTIONS}
        />
      ) : null}

      {activeTab === 'video' ? (
        <Suspense fallback={<LoadingPanel label="Loading video engine..." />}>
          <VideoModule
            videoSymbol={videoSymbol}
            setVideoSymbol={setVideoSymbol}
            videoBusy={videoBusy}
            videoData={videoData}
            generateVideo={generateVideo}
            suggestions={INDIAN_SYMBOL_SUGGESTIONS}
          />
        </Suspense>
      ) : null}
    </div>
  );
}
