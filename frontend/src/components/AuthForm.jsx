export default function AuthForm({
  title,
  subtitle,
  buttonLabel,
  values,
  error,
  busy,
  onChange,
  onSubmit,
  footer,
}) {
  return (
    <div className="auth-shell">
      <div className="auth-panel">
        <div>
          <p className="eyebrow">AI Investor Platform</p>
          <h1 className="auth-title">{title}</h1>
          <p className="auth-subtitle">{subtitle}</p>
        </div>

        <form className="auth-form" onSubmit={onSubmit}>
          <label className="field">
            <span>Email</span>
            <input
              type="email"
              name="email"
              value={values.email}
              onChange={onChange}
              placeholder="investor@example.com"
              autoComplete="email"
              required
            />
          </label>

          <label className="field">
            <span>Password</span>
            <input
              type="password"
              name="password"
              value={values.password}
              onChange={onChange}
              placeholder="Minimum 8 characters"
              autoComplete="current-password"
              minLength={8}
              required
            />
          </label>

          {error ? <p className="error-banner">{error}</p> : null}

          <button className="primary-button" type="submit" disabled={busy}>
            {busy ? 'Working...' : buttonLabel}
          </button>
        </form>

        <div className="auth-footer">{footer}</div>
      </div>
    </div>
  );
}
