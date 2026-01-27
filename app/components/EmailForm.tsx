'use client';

import { useState, useEffect, FormEvent } from 'react';

interface EmailFormProps {
  onSubmit: (email: string) => void;
}

export default function EmailForm({ onSubmit }: EmailFormProps) {
  const [email, setEmail] = useState('');
  const [consent, setConsent] = useState(false);
  const [isValid, setIsValid] = useState(false);

  // Email validation regex
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  useEffect(() => {
    // Validate form: email must be valid and consent must be checked
    const emailValid = emailRegex.test(email);
    setIsValid(emailValid && consent);
  }, [email, consent]);

  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    if (!isValid) return;

    onSubmit(email);
  };

  return (
    <form
      onSubmit={handleSubmit}
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '1.5rem',
        padding: '2rem',
        border: '1px solid #e5e7eb',
        borderRadius: '8px',
        backgroundColor: 'white'
      }}
    >
      <div style={{ textAlign: 'left' }}>
        <label
          htmlFor="email"
          style={{
            display: 'block',
            marginBottom: '0.5rem',
            fontWeight: '600',
            color: '#374151'
          }}
        >
          Email Address
        </label>
        <input
          id="email"
          type="email"
          data-testid="email-input"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          pattern="[^\s@]+@[^\s@]+\.[^\s@]+"
          placeholder="your.email@example.com"
          style={{
            width: '100%',
            padding: '0.75rem',
            border: '1px solid #d1d5db',
            borderRadius: '4px',
            fontSize: '1rem',
            boxSizing: 'border-box'
          }}
        />
      </div>

      <div style={{ textAlign: 'left' }}>
        <label
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            cursor: 'pointer'
          }}
        >
          <input
            type="checkbox"
            data-testid="consent-checkbox"
            checked={consent}
            onChange={(e) => setConsent(e.target.checked)}
            required
            style={{
              width: '1.25rem',
              height: '1.25rem',
              cursor: 'pointer'
            }}
          />
          <span style={{ color: '#374151' }}>
            I consent to receiving communications and agree to the terms
          </span>
        </label>
      </div>

      <button
        type="submit"
        data-testid="submit-button"
        disabled={!isValid}
        style={{
          padding: '0.75rem 1.5rem',
          backgroundColor: isValid ? '#0A66C2' : '#9ca3af',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          fontSize: '1rem',
          fontWeight: '600',
          cursor: isValid ? 'pointer' : 'not-allowed',
          transition: 'background-color 0.2s'
        }}
      >
        Get Personalized Content
      </button>
    </form>
  );
}
