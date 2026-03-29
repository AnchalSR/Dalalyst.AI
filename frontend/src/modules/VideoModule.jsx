import SectionCard from '../components/SectionCard';

export default function VideoModule({
  videoSymbol,
  setVideoSymbol,
  videoBusy,
  videoData,
  generateVideo,
  suggestions,
}) {
  return (
    <div className="dashboard-grid">
      <SectionCard
        title="Storyboard Generator"
        subtitle="Create slide-ready JSON summaries for Indian market videos."
        actions={
          <button className="primary-button" onClick={generateVideo} disabled={videoBusy}>
            {videoBusy ? 'Generating...' : 'Generate slides'}
          </button>
        }
      >
        <label className="field">
          <span>Symbol</span>
          <input
            value={videoSymbol}
            onChange={(event) => setVideoSymbol(event.target.value.toUpperCase())}
            placeholder="TCS or TCS.NS"
          />
        </label>
        <p className="muted-copy">Examples: {suggestions.join(', ')}</p>

        {videoData ? (
          <>
            <p>{videoData.summary}</p>
            <div className="stack-list">
              {(videoData.slides || []).map((slide, index) => (
                <article key={`${slide.title}-${index}`} className="slide-card">
                  <div className="slide-index">Slide {index + 1}</div>
                  <h3>{slide.title}</h3>
                  <p className="muted-copy">{slide.visual}</p>
                  <ul className="slide-bullets">
                    {slide.bullets.map((bullet) => (
                      <li key={bullet}>{bullet}</li>
                    ))}
                  </ul>
                  <p>{slide.narration}</p>
                </article>
              ))}
            </div>
          </>
        ) : null}
      </SectionCard>
    </div>
  );
}
