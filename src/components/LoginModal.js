import React, { useState } from 'react';

const initialFormState = {
  username: '',
  password: '',
  registrationToken: ''
};

const LoginModal = ({
  onLogin,
  onRegister,
  onClose,
  error,
  isSubmitting
}) => {
  const [mode, setMode] = useState('login');
  const [form, setForm] = useState(initialFormState);

  const handleChange = (field) => (event) => {
    setForm((prev) => ({ ...prev, [field]: event.target.value }));
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    if (mode === 'login') {
      onLogin({ username: form.username, password: form.password });
    } else {
      onRegister({
        username: form.username,
        password: form.password,
        registration_token: form.registrationToken
      });
    }
  };

  const toggleMode = () => {
    setMode((prev) => (prev === 'login' ? 'register' : 'login'));
    setForm(initialFormState);
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>{mode === 'login' ? 'Sign in' : 'Create account'}</h2>
          <button className="close-button" onClick={onClose} disabled={isSubmitting}>
            x
          </button>
        </div>
        <form onSubmit={handleSubmit}>
          <div className="modal-content">
            <div className="form-group">
              <label className="form-label">Username</label>
              <input
                type="text"
                className="form-input"
                value={form.username}
                onChange={handleChange('username')}
                autoComplete="username"
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">Password</label>
              <input
                type="password"
                className="form-input"
                value={form.password}
                onChange={handleChange('password')}
                autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
                required
              />
            </div>

            {mode === 'register' && (
              <div className="form-group">
                <label className="form-label">Registration Token (optional)</label>
                <input
                  type="text"
                  className="form-input"
                  value={form.registrationToken}
                  onChange={handleChange('registrationToken')}
                />
              </div>
            )}

            {error && <div className="form-error">{error}</div>}
          </div>

          <div className="modal-footer">
            <button
              type="button"
              className="btn btn-secondary"
              onClick={toggleMode}
              disabled={isSubmitting}
            >
              {mode === 'login' ? "Need an account?" : 'Already registered?'}
            </button>
            <button type="submit" className="btn btn-primary" disabled={isSubmitting}>
              {isSubmitting ? 'Please wait…' : mode === 'login' ? 'Sign in' : 'Register'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default LoginModal;
