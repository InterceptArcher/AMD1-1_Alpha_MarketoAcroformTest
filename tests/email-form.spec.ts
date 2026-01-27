import { test, expect } from '@playwright/test';

test.describe('Email and Consent Form', () => {

  test('should display form elements correctly', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('domcontentloaded');

    // Check email input exists
    const emailInput = page.locator('[data-testid="email-input"]');
    await expect(emailInput).toBeVisible();
    await expect(emailInput).toHaveAttribute('type', 'email');

    // Check consent checkbox exists
    const consentCheckbox = page.locator('[data-testid="consent-checkbox"]');
    await expect(consentCheckbox).toBeVisible();
    await expect(consentCheckbox).toHaveAttribute('type', 'checkbox');

    // Check submit button exists
    const submitButton = page.locator('[data-testid="submit-button"]');
    await expect(submitButton).toBeVisible();
  });

  test('submit button should be disabled by default', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('domcontentloaded');

    const submitButton = page.locator('[data-testid="submit-button"]');
    await expect(submitButton).toBeDisabled();
  });

  test('submit button should remain disabled with only email filled', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('domcontentloaded');

    const emailInput = page.locator('[data-testid="email-input"]');
    await emailInput.fill('test@example.com');

    const submitButton = page.locator('[data-testid="submit-button"]');
    await expect(submitButton).toBeDisabled();
  });

  test('submit button should remain disabled with only consent checked', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('domcontentloaded');

    const consentCheckbox = page.locator('[data-testid="consent-checkbox"]');
    await consentCheckbox.check();

    const submitButton = page.locator('[data-testid="submit-button"]');
    await expect(submitButton).toBeDisabled();
  });

  test('submit button should be enabled with valid email and consent', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('domcontentloaded');

    const emailInput = page.locator('[data-testid="email-input"]');
    await emailInput.fill('valid@example.com');

    const consentCheckbox = page.locator('[data-testid="consent-checkbox"]');
    await consentCheckbox.check();

    const submitButton = page.locator('[data-testid="submit-button"]');
    await expect(submitButton).toBeEnabled();
  });

  test('should validate email format', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('domcontentloaded');

    const emailInput = page.locator('[data-testid="email-input"]');
    const consentCheckbox = page.locator('[data-testid="consent-checkbox"]');
    const submitButton = page.locator('[data-testid="submit-button"]');

    // Enter invalid email (missing @)
    await emailInput.fill('invalidemail');
    await consentCheckbox.check();

    // Button should be disabled due to invalid email
    await expect(submitButton).toBeDisabled();

    // Enter valid email
    await emailInput.fill('valid@example.com');

    // Button should now be enabled
    await expect(submitButton).toBeEnabled();
  });

  test('should handle various invalid email formats', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('domcontentloaded');

    const emailInput = page.locator('[data-testid="email-input"]');
    const consentCheckbox = page.locator('[data-testid="consent-checkbox"]');
    const submitButton = page.locator('[data-testid="submit-button"]');

    await consentCheckbox.check();

    const invalidEmails = [
      'notanemail',
      '@example.com',
      'user@',
      'user @example.com',
      'user@.com'
    ];

    for (const invalidEmail of invalidEmails) {
      await emailInput.fill(invalidEmail);
      await expect(submitButton).toBeDisabled();
    }
  });

  test('should accept valid email formats', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('domcontentloaded');

    const emailInput = page.locator('[data-testid="email-input"]');
    const consentCheckbox = page.locator('[data-testid="consent-checkbox"]');
    const submitButton = page.locator('[data-testid="submit-button"]');

    await consentCheckbox.check();

    const validEmails = [
      'user@example.com',
      'user.name@example.com',
      'user+tag@example.co.uk',
      'user123@sub.example.com'
    ];

    for (const validEmail of validEmails) {
      await emailInput.fill(validEmail);
      await expect(submitButton).toBeEnabled();
    }
  });

  test('submit button should disable after submission', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('domcontentloaded');

    const emailInput = page.locator('[data-testid="email-input"]');
    const consentCheckbox = page.locator('[data-testid="consent-checkbox"]');
    const submitButton = page.locator('[data-testid="submit-button"]');

    await emailInput.fill('test@example.com');
    await consentCheckbox.check();

    // Click submit
    await submitButton.click();

    // Button should be disabled during submission to prevent double-submit
    await expect(submitButton).toBeDisabled();
  });

  test('should display success message after submission', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('domcontentloaded');

    const emailInput = page.locator('[data-testid="email-input"]');
    const consentCheckbox = page.locator('[data-testid="consent-checkbox"]');
    const submitButton = page.locator('[data-testid="submit-button"]');

    await emailInput.fill('test@example.com');
    await consentCheckbox.check();
    await submitButton.click();

    // Check for success message or state change
    const successMessage = page.locator('[data-testid="success-message"]');
    await expect(successMessage).toBeVisible({ timeout: 5000 });
  });

  test('should handle form with XSS attempt in email', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('domcontentloaded');

    const emailInput = page.locator('[data-testid="email-input"]');
    const submitButton = page.locator('[data-testid="submit-button"]');

    // Try to inject script tag
    await emailInput.fill('<script>alert("xss")</script>@example.com');

    // Form should reject this as invalid email
    await expect(submitButton).toBeDisabled();
  });
});
