import RecommendationPill from '../components/RecommendationPill';
import SectionCard from '../components/SectionCard';

function formatPercent(value) {
  const numeric = Number(value || 0);
  return `${numeric > 0 ? '+' : ''}${numeric.toFixed(2)}%`;
}

export default function RadarModule({
  watchlistInput,
  setWatchlistInput,
  radarBusy,
  radarData,
  savedAlerts,
  loadRadar,
  suggestions,
  portfolioData,
  portfolioInput,
  setPortfolioInput,
  addPortfolioStock,
  removePortfolioStock,
  portfolioBusy,
}) {
  return (
    <div className="dashboard-grid">
      <SectionCard
        title="Watchlist Scan"
        subtitle="Scan NSE stocks only. Alerts include impact estimates, explainability, historical validation, and risk detection."
        actions={
          <button className="primary-button" onClick={loadRadar} disabled={radarBusy}>
            {radarBusy ? 'Scanning...' : 'Scan alerts'}
          </button>
        }
      >
        <label className="field">
          <span>Watchlist symbols</span>
          <input
            value={watchlistInput}
            onChange={(event) => setWatchlistInput(event.target.value.toUpperCase())}
            placeholder="RELIANCE.NS,TCS.NS,INFY.NS"
          />
        </label>
        <p className="muted-copy">Examples: {suggestions.join(', ')}</p>

        <div className="summary-grid">
          <div className="metric-card">
            <span>BUY</span>
            <strong>{radarData.summary?.buy ?? 0}</strong>
          </div>
          <div className="metric-card">
            <span>WATCH</span>
            <strong>{radarData.summary?.watch ?? 0}</strong>
          </div>
          <div className="metric-card">
            <span>AVOID</span>
            <strong>{radarData.summary?.avoid ?? 0}</strong>
          </div>
        </div>

        <div className="stack-list">
          {(radarData.errors || []).map((entry) => (
            <div className="error-banner" key={entry.symbol}>
              {entry.symbol}: {entry.error}
            </div>
          ))}

          {(radarData.alerts || []).map((alert) => (
            <article className="alert-card" key={alert.symbol}>
              <div className="alert-topline">
                <div>
                  <h3>{alert.symbol}</h3>
                  <p className="muted-copy">{alert.name}</p>
                </div>
                <div className="badge-column">
                  <RecommendationPill value={alert.recommendation} />
                  <span className="signal-strength">{alert.signal_strength}</span>
                </div>
              </div>

              <div className="price-row">
                <p className="price-line">Rs {alert.current_price}</p>
                <div className={`change-chip ${alert.change_percent >= 0 ? 'change-up' : 'change-down'}`}>
                  {formatPercent(alert.change_percent)}
                </div>
              </div>

              <p className="muted-copy">{alert.signal_summary}</p>

              <div className="detail-grid">
                <div className="detail-chip">
                  <span>Confidence</span>
                  <strong>{alert.confidence_score}/100</strong>
                </div>
                <div className="detail-chip">
                  <span>Historical Accuracy</span>
                  <strong>
                    {alert.historical_accuracy.success_rate !== null
                      ? `${alert.historical_accuracy.success_rate}%`
                      : 'N/A'}
                  </strong>
                </div>
                <div className="detail-chip">
                  <span>Volume Ratio</span>
                  <strong>{alert.metrics.volume_ratio}x</strong>
                </div>
                <div className="detail-chip">
                  <span>Trend</span>
                  <strong>{alert.metrics.trend}</strong>
                </div>
                <div className="detail-chip">
                  <span>Vs SMA20</span>
                  <strong>{formatPercent(alert.metrics.price_vs_sma20_pct)}</strong>
                </div>
              </div>

              <div className="impact-grid">
                <div className="detail-chip impact-chip">
                  <span>Estimated Impact</span>
                  <strong>
                    {alert.estimated_impact.weekly !== null ? `${alert.estimated_impact.weekly}% / week` : 'N/A'}
                  </strong>
                </div>
                <div className="detail-chip impact-chip">
                  <span>Monthly</span>
                  <strong>
                    {alert.estimated_impact.monthly !== null ? `${alert.estimated_impact.monthly}%` : 'N/A'}
                  </strong>
                </div>
                <div className="detail-chip impact-chip">
                  <span>Yearly</span>
                  <strong>
                    {alert.estimated_impact.yearly !== null ? `${alert.estimated_impact.yearly}%` : 'N/A'}
                  </strong>
                </div>
              </div>

              <p>{alert.explanation}</p>

              <div className="why-box">
                <span className="why-title">Why This Matters</span>
                <p>{alert.why_this_matters}</p>
              </div>

              <div className="why-box">
                <span className="why-title">How This Decision Was Made</span>
                <div className="detail-grid compact-top">
                  <div className="detail-chip">
                    <span>Price Contribution</span>
                    <strong>{alert.score_breakdown.price_change_score}</strong>
                  </div>
                  <div className="detail-chip">
                    <span>Volume Contribution</span>
                    <strong>{alert.score_breakdown.volume_score}</strong>
                  </div>
                  <div className="detail-chip">
                    <span>Trend Contribution</span>
                    <strong>{alert.score_breakdown.trend_score}</strong>
                  </div>
                  <div className="detail-chip">
                    <span>Total Score</span>
                    <strong>{alert.score_breakdown.total}</strong>
                  </div>
                </div>
                <p className="muted-copy">
                  Classification: {alert.signal_strength}. {alert.estimated_impact.summary}
                </p>
              </div>

              <div className="why-box risk-box">
                <span className="why-title">Risk Factors</span>
                <ul className="compact-list">
                  {alert.risk_factors.map((factor) => (
                    <li key={factor}>{factor}</li>
                  ))}
                </ul>
                <p className="muted-copy">{alert.historical_accuracy.summary}</p>
              </div>
            </article>
          ))}
        </div>
      </SectionCard>

      <SectionCard title="Saved Alert History" subtitle="Latest protected alert records for this account.">
        <div className="table-list">
          {savedAlerts.map((alert) => (
            <div className="table-row" key={alert.id}>
              <div>
                <strong>{alert.stock}</strong>
                <p className="muted-copy">{alert.signal}</p>
              </div>
              <div className="row-right">
                <RecommendationPill value={alert.recommendation} />
                <span className="muted-copy">{alert.created_at}</span>
              </div>
            </div>
          ))}
          {!savedAlerts.length ? <p className="muted-copy">No saved alerts yet.</p> : null}
        </div>
      </SectionCard>

      <SectionCard title="Risk Alerts" subtitle="Downtrend and sudden-drop warnings detected across the scanned universe.">
        <div className="stack-list">
          {(radarData.risk_alerts || []).map((risk) => (
            <article className="alert-card risk-card" key={`${risk.symbol}-${risk.type}`}>
              <div className="alert-topline">
                <div>
                  <h3>{risk.symbol}</h3>
                  <p className="muted-copy">{risk.type}</p>
                </div>
                <RecommendationPill value={risk.recommendation} label={risk.severity} />
              </div>
              <p>{risk.message}</p>
            </article>
          ))}
          {!(radarData.risk_alerts || []).length ? (
            <p className="muted-copy">No major risk warnings in the current scan.</p>
          ) : null}
        </div>
      </SectionCard>

      <SectionCard title="Portfolio Intelligence" subtitle="Track your own names and generate personalized opportunities and warnings.">
        <form className="portfolio-form" onSubmit={addPortfolioStock}>
          <label className="field field-grow">
            <span>Add stock</span>
            <input
              value={portfolioInput}
              onChange={(event) => setPortfolioInput(event.target.value.toUpperCase())}
              placeholder="RELIANCE or RELIANCE.NS"
            />
          </label>
          <button className="primary-button" type="submit" disabled={portfolioBusy}>
            {portfolioBusy ? 'Updating...' : 'Add'}
          </button>
        </form>

        <div className="portfolio-chip-row">
          {(portfolioData?.stocks || []).map((stock) => (
            <button
              key={stock}
              className="portfolio-chip"
              onClick={() => removePortfolioStock(stock)}
              disabled={portfolioBusy}
            >
              {stock} x
            </button>
          ))}
          {!(portfolioData?.stocks || []).length ? (
            <p className="muted-copy">No portfolio stocks yet.</p>
          ) : null}
        </div>

        <div className="why-box">
          <span className="why-title">Opportunity Summary</span>
          <p>{portfolioData?.opportunity_summary || 'Loading portfolio insights...'}</p>
        </div>

        <div className="stack-list">
          {(portfolioData?.alerts || []).map((alert) => (
            <article className="alert-card" key={`portfolio-${alert.symbol}`}>
              <div className="alert-topline">
                <div>
                  <h3>{alert.symbol}</h3>
                  <p className="muted-copy">{alert.signal_strength}</p>
                </div>
                <RecommendationPill value={alert.recommendation} />
              </div>
              <p className="muted-copy">
                Confidence {alert.confidence_score}/100 - Historical Accuracy{' '}
                {alert.historical_accuracy.success_rate !== null
                  ? `${alert.historical_accuracy.success_rate}%`
                  : 'N/A'}
              </p>
              <p>{alert.signal_summary}</p>
            </article>
          ))}
        </div>
      </SectionCard>
    </div>
  );
}
