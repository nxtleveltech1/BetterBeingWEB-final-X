import { test, expect } from '@playwright/test';

test.describe('Better Being Design Capture', () => {
  test('capture homepage design state', async ({ page }) => {
    // Navigate to homepage
    await page.goto('/');
    
    // Wait for page to fully load
    await page.waitForLoadState('networkidle');
    
    // Take full page screenshot
    await page.screenshot({ 
      path: 'design-screenshots/homepage-fullpage.png',
      fullPage: true 
    });
    
    // Take viewport screenshot
    await page.screenshot({ 
      path: 'design-screenshots/homepage-viewport.png'
    });
    
    // Check for console errors
    const consoleLogs = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleLogs.push(msg.text());
      }
    });
    
    // Reload to catch any console errors
    await page.reload();
    await page.waitForLoadState('networkidle');
    
    // Verify no critical console errors
    const criticalErrors = consoleLogs.filter(log => 
      !log.includes('Download the React DevTools') && 
      !log.includes('favicon')
    );
    expect(criticalErrors).toHaveLength(0);
  });

  test('capture product page design state', async ({ page }) => {
    await page.goto('/products');
    await page.waitForLoadState('networkidle');
    
    // Take screenshots
    await page.screenshot({ 
      path: 'design-screenshots/products-fullpage.png',
      fullPage: true 
    });
    
    // Test hover states on product cards
    const productCard = page.locator('[data-testid="product-card"]').first();
    if (await productCard.count() > 0) {
      await productCard.hover();
      await page.screenshot({ 
        path: 'design-screenshots/products-hover-state.png'
      });
    }
  });

  test('capture mobile responsive design', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    // Test homepage mobile
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.screenshot({ 
      path: 'design-screenshots/homepage-mobile.png',
      fullPage: true 
    });
    
    // Test navigation menu on mobile
    const navToggle = page.locator('[data-testid="mobile-nav-toggle"]');
    if (await navToggle.count() > 0) {
      await navToggle.click();
      await page.screenshot({ 
        path: 'design-screenshots/mobile-nav-open.png'
      });
    }
  });

  test('validate Better Being brand colors', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Check for brand colors in CSS
    const brandColors = {
      honey: '#e5c287',
      chocolate: '#7a4d3b', 
      cream: '#f0e9d2'
    };
    
    // Evaluate CSS custom properties
    const cssColors = await page.evaluate(() => {
      const style = getComputedStyle(document.documentElement);
      return {
        primary: style.getPropertyValue('--color-primary'),
        secondary: style.getPropertyValue('--color-secondary'),
        background: style.getPropertyValue('--color-background')
      };
    });
    
    console.log('Detected brand colors:', cssColors);
  });
});