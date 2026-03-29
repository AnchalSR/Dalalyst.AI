export default function LoadingPanel({ label = 'Loading module...' }) {
  return (
    <div className="panel">
      <p className="muted-copy">{label}</p>
    </div>
  );
}
