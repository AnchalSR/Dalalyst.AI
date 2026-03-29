import SectionCard from '../components/SectionCard';

export default function ChatModule({
  chatTurns,
  chatSymbol,
  setChatSymbol,
  chatInput,
  setChatInput,
  chatBusy,
  sendMessage,
  suggestions,
}) {
  return (
    <div className="dashboard-grid">
      <SectionCard title="Investor Chat" subtitle="Multi-turn NSE conversations are stored in SQLite per user.">
        <div className="why-box">
          <span className="why-title">Portfolio-Aware Mode</span>
          <p>
            Ask about Indian portfolio risk, strongest NSE signals, or what to prioritize next. The chat
            uses saved portfolio stocks plus their latest radar recommendations.
          </p>
        </div>

        <div className="chat-feed">
          {chatTurns.map((turn) => (
            <div key={turn.id} className={`chat-bubble chat-${turn.role}`}>
              <span className="chat-role">{turn.role === 'user' ? 'You' : 'Dalalyst AI'}</span>
              <p>{turn.text}</p>
              <span className="chat-meta">
                {turn.symbol ? `${turn.symbol} - ` : ''}
                {turn.timestamp}
              </span>
            </div>
          ))}
          {!chatTurns.length ? (
            <p className="muted-copy">No chat history yet. Ask about an NSE stock, portfolio opportunity, or risk setup.</p>
          ) : null}
        </div>

        <form className="chat-form" onSubmit={sendMessage}>
          <div className="chat-controls">
            <label className="field">
              <span>Symbol context</span>
              <input
                value={chatSymbol}
                onChange={(event) => setChatSymbol(event.target.value.toUpperCase())}
                placeholder="RELIANCE or RELIANCE.NS"
              />
            </label>
            <label className="field field-grow">
              <span>Your question</span>
              <input
                value={chatInput}
                onChange={(event) => setChatInput(event.target.value)}
                placeholder="Which portfolio stock has the best near-term setup?"
              />
            </label>
          </div>
          <p className="muted-copy">Examples: {suggestions.join(', ')}</p>
          <button className="primary-button" type="submit" disabled={chatBusy}>
            {chatBusy ? 'Sending...' : 'Send message'}
          </button>
        </form>
      </SectionCard>
    </div>
  );
}
