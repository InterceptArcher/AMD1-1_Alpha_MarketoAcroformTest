import { test, expect } from '@playwright/test';

test.describe('Landing Page - Query String Parsing', () => {

  test('should display the cta parameter from query string', async ({ page }) => {
    // Navigate to landing page with cta=compare query parameter
    await page.goto('/?cta=compare');

    // Wait for page to load
    await page.waitForLoadState('domcontentloaded');

    // Verify the CTA value is displayed
    const ctaText = page.locator('[data-testid="cta-display"]');
    await expect(ctaText).toBeVisible();
    await expect(ctaText).toContainText('compare');
  });

  test('should display default message when cta parameter is missing', async ({ page }) => {
    // Navigate to landing page without query parameters
    await page.goto('/');

    // Wait for page to load
    await page.waitForLoadState('domcontentloaded');

    // Verify default message is displayed
    const ctaText = page.locator('[data-testid="cta-display"]');
    await expect(ctaText).toBeVisible();
    await expect(ctaText).toContainText('Default CTA Message');
  });

  test('should handle special characters in cta parameter', async ({ page }) => {
    // Test with URL-encoded special characters
    await page.goto('/?cta=get-started');

    await page.waitForLoadState('domcontentloaded');

    const ctaText = page.locator('[data-testid="cta-display"]');
    await expect(ctaText).toBeVisible();
    await expect(ctaText).toContainText('get-started');
  });

  test('should ignore invalid query parameters', async ({ page }) => {
    // Navigate with invalid parameter
    await page.goto('/?invalid=test&cta=signup');

    await page.waitForLoadState('domcontentloaded');

    // Should still display the cta value correctly
    const ctaText = page.locator('[data-testid="cta-display"]');
    await expect(ctaText).toContainText('signup');
  });

  test('should update display when cta parameter changes', async ({ page }) => {
    // First navigation
    await page.goto('/?cta=compare');
    await page.waitForLoadState('domcontentloaded');

    let ctaText = page.locator('[data-testid="cta-display"]');
    await expect(ctaText).toContainText('compare');

    // Navigate to different cta value
    await page.goto('/?cta=signup');
    await page.waitForLoadState('domcontentloaded');

    ctaText = page.locator('[data-testid="cta-display"]');
    await expect(ctaText).toContainText('signup');
  });
});
