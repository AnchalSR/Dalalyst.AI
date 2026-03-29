import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import SectionCard from '../components/SectionCard';

export default function ChartModule({
  chartSymbol,
  setChartSymbol,
  chartBusy,
  chartData,
  loadChart,
  suggestions,
}) {
  return (
    <div className="dashboard-grid">
      <SectionCard
        title="Trend Detection"
        subtitle="Fetch NSE historical prices, classify trend, and visualize moving averages."
        actions={
          <button className="primary-button" onClick={() => loadChart()} disabled={chartBusy}>
            {chartBusy ? 'Loading...' : 'Analyze chart'}
          </button>
        }
      >
        <label className="field">
          <span>Symbol</span>
          <input
            value={chartSymbol}
            onChange={(event) => setChartSymbol(event.target.value.toUpperCase())}
            placeholder="RELIANCE or RELIANCE.NS"
          />
        </label>
        <p className="muted-copy">Examples: {suggestions.join(', ')}</p>

        {chartData ? (
          <>
            <div className="insight-grid">
              <div className="metric-card">
                <span>Trend</span>
                <strong>{chartData.trend}</strong>
              </div>
              <div className="metric-card">
                <span>Support</span>
                <strong>Rs {chartData.support}</strong>
              </div>
              <div className="metric-card">
                <span>Resistance</span>
                <strong>Rs {chartData.resistance}</strong>
              </div>
            </div>

            <p>{chartData.summary}</p>

            <div className="chart-shell">
              <ResponsiveContainer width="100%" height={320}>
                <LineChart data={chartData.chart_data || []}>
                  <CartesianGrid stroke="rgba(255,255,255,0.08)" vertical={false} />
                  <XAxis dataKey="date" tick={{ fill: '#d8d1bf', fontSize: 11 }} />
                  <YAxis tick={{ fill: '#d8d1bf', fontSize: 11 }} />
                  <Tooltip />
                  <Line type="monotone" dataKey="close" stroke="#ffb347" strokeWidth={3} dot={false} />
                  <Line type="monotone" dataKey="sma20" stroke="#3dd9b1" strokeWidth={2} dot={false} />
                  <Line type="monotone" dataKey="sma50" stroke="#7cb7ff" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </>
        ) : null}
      </SectionCard>
    </div>
  );
}
