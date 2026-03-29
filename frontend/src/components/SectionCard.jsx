export default function SectionCard({ title, subtitle, children, actions }) {
  return (
    <section className="panel">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">{title}</p>
          {subtitle ? <p className="muted-copy">{subtitle}</p> : null}
        </div>
        {actions}
      </div>
      {children}
    </section>
  );
}
