export default function RecommendationPill({ value, label }) {
  const tone = value?.toLowerCase() || 'watch';
  return <span className={`signal-pill signal-${tone}`}>{label || value}</span>;
}
