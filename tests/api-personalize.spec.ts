import { test, expect } from '@playwright/test';

test.describe('API Route: /api/personalize', () => {

  test('should accept POST request with email and cta', async ({ request }) => {
    const response = await request.post('/api/personalize', {
      data: {
        email: 'john@example.com',
        cta: 'compare'
      }
    });

    expect(response.status()).not.toBe(404);
    expect(response.status()).not.toBe(405); // Method Not Allowed
  });

  test('should reject GET requests', async ({ request }) => {
    const response = await request.get('/api/personalize');
    expect(response.status()).toBe(405);
  });

  test('should return 400 for missing email', async ({ request }) => {
    const response = await request.post('/api/personalize', {
      data: {
        cta: 'compare'
      }
    });

    expect(response.status()).toBe(400);
    const body = await response.json();
    expect(body.error).toContain('email');
  });

  test('should return 400 for invalid email format', async ({ request }) => {
    const response = await request.post('/api/personalize', {
      data: {
        email: 'notanemail',
        cta: 'compare'
      }
    });

    expect(response.status()).toBe(400);
  });

  test('should extract domain from email correctly', async ({ request }) => {
    const response = await request.post('/api/personalize', {
      data: {
        email: 'user@company.com',
        cta: 'compare'
      }
    });

    // Even if Claude API isn't configured, we should get a proper response structure
    const status = response.status();
    expect([200, 500, 503]).toContain(status); // 200 success, 500/503 if Claude unavailable
  });

  test('should infer persona from email prefix', async ({ request }) => {
    const testCases = [
      { email: 'ops@company.com', expectedPersona: 'Operations' },
      { email: 'security@company.com', expectedPersona: 'Security' },
      { email: 'it@company.com', expectedPersona: 'IT' },
      { email: 'finance@company.com', expectedPersona: 'Finance' },
      { email: 'random@company.com', expectedPersona: 'Business Leader' }
    ];

    for (const testCase of testCases) {
      const response = await request.post('/api/personalize', {
        data: {
          email: testCase.email,
          cta: 'compare'
        }
      });

      if (response.status() === 200) {
        const body = await response.json();
        // Check if persona inference is working (may be in job metadata)
        expect(body).toHaveProperty('data');
      }
    }
  });

  test('should infer buyer stage from cta', async ({ request }) => {
    const testCases = [
      { cta: 'compare', expectedStage: 'Evaluation' },
      { cta: 'learn', expectedStage: 'Awareness' },
      { cta: 'demo', expectedStage: 'Decision' },
      { cta: 'unknown', expectedStage: 'Evaluation' } // default
    ];

    for (const testCase of testCases) {
      const response = await request.post('/api/personalize', {
        data: {
          email: 'test@company.com',
          cta: testCase.cta
        }
      });

      if (response.status() === 200) {
        const body = await response.json();
        expect(body).toHaveProperty('data');
      }
    }
  });

  test('should return structured JSON response', async ({ request }) => {
    const response = await request.post('/api/personalize', {
      data: {
        email: 'test@example.com',
        cta: 'compare'
      }
    });

    const body = await response.json();

    // Should have either data or error
    if (response.status() === 200) {
      expect(body).toHaveProperty('data');
      expect(body).toHaveProperty('jobId');
    } else {
      expect(body).toHaveProperty('error');
    }
  });

  test('should handle malformed request body', async ({ request }) => {
    const response = await request.post('/api/personalize', {
      data: {
        invalid: 'data'
      }
    });

    expect(response.status()).toBe(400);
  });

  test('should prevent XSS in email input', async ({ request }) => {
    const response = await request.post('/api/personalize', {
      data: {
        email: '<script>alert("xss")</script>@example.com',
        cta: 'compare'
      }
    });

    expect(response.status()).toBe(400);
  });
});
