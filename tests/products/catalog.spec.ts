import { test, expect } from '@playwright/test';

test.describe('Product Catalog', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/products');
  });

  test('should display product catalog correctly', async ({ page }) => {
    await expect(page).toHaveTitle(/Products/);
    
    // Check hero section
    await expect(page.locator('text=Discover Your')).toBeVisible();
    await expect(page.locator('text=Wellness Journey')).toBeVisible();
    
    // Check search and filter section
    await expect(page.locator('input[placeholder*="Search products"]')).toBeVisible();
    await expect(page.locator('select').first()).toBeVisible(); // Category filter
    await expect(page.locator('select').nth(1)).toBeVisible(); // Sort filter
    
    // Check view mode toggles
    await expect(page.locator('[data-testid="grid-view"]')).toBeVisible();
    await expect(page.locator('[data-testid="list-view"]')).toBeVisible();
  });

  test('should display products in grid format by default', async ({ page }) => {
    // Wait for products to load
    await page.waitForSelector('[data-testid="product-card"]', { timeout: 10000 });
    
    const productCards = page.locator('[data-testid="product-card"]');
    await expect(productCards).toHaveCountGreaterThan(0);
    
    // Check first product card structure
    const firstCard = productCards.first();
    await expect(firstCard.locator('img')).toBeVisible();
    await expect(firstCard.locator('text=R')).toBeVisible(); // Price
    await expect(firstCard.locator('button:has-text("Add to Cart")')).toBeVisible();
  });

  test('should search products correctly', async ({ page }) => {
    const searchInput = page.locator('input[placeholder*="Search products"]');
    
    await searchInput.fill('ashwagandha');
    await page.keyboard.press('Enter');
    
    // Wait for search results
    await page.waitForTimeout(1000);
    
    // Should show products containing search term
    const productCards = page.locator('[data-testid="product-card"]');
    const firstProduct = productCards.first();
    await expect(firstProduct.locator('text=Ashwagandha')).toBeVisible();
  });

  test('should filter products by category', async ({ page }) => {
    const categoryFilter = page.locator('select').first();
    
    await categoryFilter.selectOption('Adaptogens');
    await page.waitForTimeout(1000);
    
    // Should show only adaptogen products
    const resultText = page.locator('text=Showing');
    await expect(resultText).toBeVisible();
  });

  test('should sort products correctly', async ({ page }) => {
    const sortFilter = page.locator('select').nth(1);
    
    // Sort by price low to high
    await sortFilter.selectOption('price-low');
    await page.waitForTimeout(1000);
    
    // Get all price elements and verify sorting
    const prices = await page.locator('[data-testid="product-price"]').allTextContents();
    const numericPrices = prices.map(price => parseFloat(price.replace('R', '')));
    
    for (let i = 1; i < numericPrices.length; i++) {
      expect(numericPrices[i]).toBeGreaterThanOrEqual(numericPrices[i - 1]);
    }
  });

  test('should toggle between grid and list view', async ({ page }) => {
    const gridView = page.locator('[data-testid="grid-view"]');
    const listView = page.locator('[data-testid="list-view"]');
    
    // Initially should be in grid view
    await expect(gridView).toHaveClass(/bg-\[var\(--bb-mahogany\)\]/);
    
    // Switch to list view
    await listView.click();
    await expect(listView).toHaveClass(/bg-\[var\(--bb-mahogany\)\]/);
    
    // Products should be displayed in list format
    const productContainer = page.locator('[data-testid="products-container"]');
    await expect(productContainer).toHaveClass(/grid-cols-1/);
  });

  test('should add product to cart', async ({ page }) => {
    // Mock add to cart API
    await page.route('**/api/cart/items', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ success: true })
      });
    });

    const firstProduct = page.locator('[data-testid="product-card"]').first();
    const addToCartButton = firstProduct.locator('button:has-text("Add to Cart")');
    
    await addToCartButton.click();
    
    // Should show success feedback
    await expect(page.locator('text=Added to cart')).toBeVisible();
  });

  test('should handle out of stock products', async ({ page }) => {
    // Look for out of stock product
    const outOfStockProduct = page.locator('[data-testid="product-card"]:has-text("Out of Stock")');
    
    if (await outOfStockProduct.count() > 0) {
      const addToCartButton = outOfStockProduct.locator('button');
      await expect(addToCartButton).toBeDisabled();
      await expect(addToCartButton).toContainText('Out of Stock');
    }
  });

  test('should display product ratings', async ({ page }) => {
    const productCard = page.locator('[data-testid="product-card"]').first();
    
    // Should show star rating
    await expect(productCard.locator('[data-testid="star-rating"]')).toBeVisible();
    
    // Should show rating number and review count
    await expect(productCard.locator('text=/\\d+\\.\\d+/')).toBeVisible(); // Rating like 4.8
    await expect(productCard.locator('text=/\\(\\d+\\)/')).toBeVisible(); // Review count like (156)
  });

  test('should navigate to product detail page', async ({ page }) => {
    const firstProduct = page.locator('[data-testid="product-card"]').first();
    const productName = await firstProduct.locator('[data-testid="product-name"]').textContent();
    
    await firstProduct.click();
    
    // Should navigate to product detail page
    await expect(page).toHaveURL(/\/products\/.+/);
    await expect(page.locator(`text=${productName}`)).toBeVisible();
  });

  test('should handle wishlist functionality', async ({ page }) => {
    // Mock wishlist API
    await page.route('**/api/wishlist/items', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ success: true })
      });
    });

    const wishlistButton = page.locator('[data-testid="wishlist-button"]').first();
    
    await wishlistButton.click();
    
    // Heart should change state
    const heartIcon = wishlistButton.locator('svg');
    await expect(heartIcon).toHaveClass(/fill-red-500/);
  });

  test('should clear filters correctly', async ({ page }) => {
    // Apply some filters
    await page.locator('input[placeholder*="Search products"]').fill('test');
    await page.locator('select').first().selectOption('Adaptogens');
    
    // Should show filtered results
    await page.waitForTimeout(1000);
    
    // Clear filters
    await page.click('button:has-text("Clear Filters")');
    
    // Should reset to all products
    await expect(page.locator('input[placeholder*="Search products"]')).toHaveValue('');
    await expect(page.locator('select').first()).toHaveValue('All Products');
  });

  test('should show no results message when appropriate', async ({ page }) => {
    await page.locator('input[placeholder*="Search products"]').fill('nonexistentproduct123');
    await page.keyboard.press('Enter');
    
    await page.waitForTimeout(1000);
    
    // Should show no results message
    await expect(page.locator('text=No products found')).toBeVisible();
    await expect(page.locator('text=Clear Filters')).toBeVisible();
  });

  test('should handle mobile responsive design', async ({ page }) => {
    // Simulate mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    // Hero section should be responsive
    await expect(page.locator('text=Discover Your')).toBeVisible();
    
    // Search bar should be full width on mobile
    const searchInput = page.locator('input[placeholder*="Search products"]');
    const searchBox = await searchInput.boundingBox();
    expect(searchBox?.width).toBeGreaterThan(300);
    
    // Products should stack in single column on mobile
    const productContainer = page.locator('[data-testid="products-container"]');
    await expect(productContainer).toHaveClass(/grid-cols-1/);
  });

  test('should load more products with pagination', async ({ page }) => {
    // Scroll to bottom to trigger pagination
    await page.evaluate(() => {
      window.scrollTo(0, document.body.scrollHeight);
    });
    
    // If pagination exists, should load more products
    const loadMoreButton = page.locator('button:has-text("Load More")');
    if (await loadMoreButton.isVisible()) {
      const initialProductCount = await page.locator('[data-testid="product-card"]').count();
      
      await loadMoreButton.click();
      await page.waitForTimeout(1000);
      
      const newProductCount = await page.locator('[data-testid="product-card"]').count();
      expect(newProductCount).toBeGreaterThan(initialProductCount);
    }
  });

  test('should handle product quick view modal', async ({ page }) => {
    const quickViewButton = page.locator('[data-testid="quick-view-button"]').first();
    
    if (await quickViewButton.isVisible()) {
      await quickViewButton.click();
      
      // Should open modal with product details
      await expect(page.locator('[data-testid="quick-view-modal"]')).toBeVisible();
      await expect(page.locator('button:has-text("Add to Cart")')).toBeVisible();
      
      // Close modal
      await page.locator('[data-testid="close-modal"]').click();
      await expect(page.locator('[data-testid="quick-view-modal"]')).not.toBeVisible();
    }
  });
});