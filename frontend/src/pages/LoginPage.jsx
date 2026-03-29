import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import AuthForm from '../components/AuthForm';
import { apiRequest, persistSession } from '../lib/api';

export default function LoginPage() {
  const navigate = useNavigate();
  const [values, setValues] = useState({ email: '', password: '' });
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setBusy(true);
    setError('');
    try {
      const payload = await apiRequest('/auth/login', {
        method: 'POST',
        body: values,
      });
      persistSession(payload);
      navigate('/dashboard', { replace: true });
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <AuthForm
      title="Welcome back"
      subtitle="Sign in to your Groq-powered investor workspace."
      buttonLabel="Login"
      values={values}
      error={error}
      busy={busy}
      onChange={(event) =>
        setValues((current) => ({ ...current, [event.target.name]: event.target.value }))
      }
      onSubmit={handleSubmit}
      footer={
        <p>
          Need an account? <Link to="/register">Create one</Link>
        </p>
      }
    />
  );
}
