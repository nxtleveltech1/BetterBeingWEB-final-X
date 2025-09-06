import { test, expect } from '@playwright/test';

test.describe('Shopping Cart', () => {
  test.beforeEach(async ({ page }) => {
    // Mock authentication
    await page.route('**/api/auth/me', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 1,
          email: 'test@example.com',
          first_name: 'Test',
          last_name: 'User'
        })
      });
    });

    await page.goto('/cart');
  });

  test('should display empty cart message when cart is empty', async ({ page }) => {
    // Mock empty cart API response
    await page.route('**/api/cart', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [],
          total_items: 0,
          subtotal: 0,
          estimated_tax: 0,
          estimated_shipping: 0,
          estimated_total: 0
        })
      });
    });

    await page.reload();
    
    await expect(page.locator('text=Your cart is empty')).toBeVisible();
    await expect(page.locator('text=Continue Shopping')).toBeVisible();
  });

  test('should display cart items correctly', async ({ page }) => {
    // Mock cart with items
    await page.route('**/api/cart', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [
            {
              id: 1,
              product_id: 1,
              product_name: 'Organic Ashwagandha Capsules',
              product_price: 89.99,
              product_slug: 'organic-ashwagandha-capsules',
              quantity: 2,
              subtotal: 179.98,
              stock_quantity: 150
            },
            {
              id: 2,
              product_id: 2,
              product_name: 'Himalayan Shilajit Resin',
              product_price: 149.99,
              product_slug: 'himalayan-shilajit-resin',
              quantity: 1,
              subtotal: 149.99,
              stock_quantity: 75
            }
          ],
          total_items: 3,
          subtotal: 329.97,
          estimated_tax: 49.50,
          estimated_shipping: 0,
          estimated_total: 379.47
        })
      });
    });

    await page.reload();
    
    // Should display cart items
    await expect(page.locator('text=Organic Ashwagandha Capsules')).toBeVisible();
    await expect(page.locator('text=Himalayan Shilajit Resin')).toBeVisible();
    
    // Should display quantities
    await expect(page.locator('input[value="2"]')).toBeVisible();
    await expect(page.locator('input[value="1"]')).toBeVisible();
    
    // Should display prices
    await expect(page.locator('text=R179.98')).toBeVisible();
    await expect(page.locator('text=R149.99')).toBeVisible();
    
    // Should display totals
    await expect(page.locator('text=R329.97').first()).toBeVisible(); // Subtotal
    await expect(page.locator('text=R49.50')).toBeVisible(); // Tax
    await expect(page.locator('text=R379.47')).toBeVisible(); // Total
  });

  test('should update item quantity', async ({ page }) => {
    // Mock cart with items
    await page.route('**/api/cart', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [{
            id: 1,
            product_id: 1,
            product_name: 'Organic Ashwagandha Capsules',
            product_price: 89.99,
            quantity: 2,
            subtotal: 179.98
          }],
          subtotal: 179.98
        })
      });
    });

    // Mock update quantity API
    await page.route('**/api/cart/items/1', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 1,
          quantity: 3,
          subtotal: 269.97
        })
      });
    });

    await page.reload();
    
    const quantityInput = page.locator('input[type="number"]').first();
    await quantityInput.fill('3');
    await quantityInput.blur();
    
    // Should update the cart
    await expect(page.locator('text=Updated')).toBeVisible();
  });

  test('should remove item from cart', async ({ page }) => {
    // Mock cart with items
    await page.route('**/api/cart', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [{
            id: 1,
            product_name: 'Organic Ashwagandha Capsules',
            quantity: 1
          }]
        })
      });
    });

    // Mock remove item API
    await page.route('**/api/cart/items/1', async route => {
      if (route.request().method() === 'DELETE') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ message: 'Item removed' })
        });
      }
    });

    await page.reload();
    
    const removeButton = page.locator('[data-testid="remove-item"]').first();
    await removeButton.click();
    
    // Should confirm removal
    await expect(page.locator('text=Are you sure?')).toBeVisible();
    await page.click('button:has-text("Remove")');
    
    // Should show removal feedback
    await expect(page.locator('text=Item removed')).toBeVisible();
  });

  test('should clear entire cart', async ({ page }) => {
    // Mock cart with items
    await page.route('**/api/cart', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [
            { id: 1, product_name: 'Product 1', quantity: 1 },
            { id: 2, product_name: 'Product 2', quantity: 2 }
          ]
        })
      });
    });

    // Mock clear cart API
    await page.route('**/api/cart', async route => {
      if (route.request().method() === 'DELETE') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ message: 'Cart cleared' })
        });
      }
    });

    await page.reload();
    
    await page.click('button:has-text("Clear Cart")');
    
    // Should confirm clearing
    await expect(page.locator('text=Clear entire cart?')).toBeVisible();
    await page.click('button:has-text("Clear All")');
    
    // Should show success message
    await expect(page.locator('text=Cart cleared')).toBeVisible();
  });

  test('should handle quantity validation', async ({ page }) => {
    // Mock cart with items
    await page.route('**/api/cart', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [{
            id: 1,
            product_name: 'Test Product',
            quantity: 1,
            stock_quantity: 5
          }]
        })
      });
    });

    await page.reload();
    
    const quantityInput = page.locator('input[type="number"]').first();
    
    // Try to set quantity higher than stock
    await quantityInput.fill('10');
    await quantityInput.blur();
    
    // Should show error message
    await expect(page.locator('text=Only 5 items available')).toBeVisible();
    
    // Try to set quantity to 0
    await quantityInput.fill('0');
    await quantityInput.blur();
    
    // Should prevent setting to 0
    expect(await quantityInput.inputValue()).toBe('1');
  });

  test('should calculate shipping correctly', async ({ page }) => {
    // Mock cart under free shipping threshold
    await page.route('**/api/cart', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [{ id: 1, subtotal: 300 }],
          subtotal: 300.00,
          estimated_shipping: 75.00,
          estimated_total: 375.00
        })
      });
    });

    await page.reload();
    
    await expect(page.locator('text=R75.00').first()).toBeVisible(); // Shipping cost
    await expect(page.locator('text=Add R200.00 for free shipping')).toBeVisible();
  });

  test('should show free shipping when threshold met', async ({ page }) => {
    // Mock cart over free shipping threshold
    await page.route('**/api/cart', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [{ id: 1, subtotal: 600 }],
          subtotal: 600.00,
          estimated_shipping: 0.00,
          estimated_total: 600.00
        })
      });
    });

    await page.reload();
    
    await expect(page.locator('text=Free shipping')).toBeVisible();
    await expect(page.locator('text=R0.00').first()).toBeVisible(); // Shipping cost
  });

  test('should proceed to checkout', async ({ page }) => {
    // Mock cart with items
    await page.route('**/api/cart', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [{ id: 1, product_name: 'Test Product', quantity: 1 }],
          estimated_total: 100.00
        })
      });
    });

    await page.reload();
    
    const checkoutButton = page.locator('button:has-text("Proceed to Checkout")');
    await checkoutButton.click();
    
    await expect(page).toHaveURL('/checkout');
  });

  test('should continue shopping', async ({ page }) => {
    await page.click('text=Continue Shopping');
    await expect(page).toHaveURL('/products');
  });

  test('should display estimated delivery date', async ({ page }) => {
    // Mock cart with delivery estimate
    await page.route('**/api/cart', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [{ id: 1, product_name: 'Test Product' }],
          estimated_delivery: '2024-01-15'
        })
      });
    });

    await page.reload();
    
    await expect(page.locator('text=Estimated delivery')).toBeVisible();
  });

  test('should handle cart sync for authenticated user', async ({ page }) => {
    // Mock cart sync API
    await page.route('**/api/cart/sync', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ message: 'Cart synced successfully' })
      });
    });

    // Simulate login
    await page.evaluate(() => {
      window.dispatchEvent(new CustomEvent('user-authenticated'));
    });

    await expect(page.locator('text=Cart synced')).toBeVisible();
  });

  test('should handle mobile responsive design', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    
    // Mock cart with items
    await page.route('**/api/cart', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [{ id: 1, product_name: 'Test Product', quantity: 1 }]
        })
      });
    });

    await page.reload();
    
    // Cart should be responsive on mobile
    const cartContainer = page.locator('[data-testid="cart-container"]');
    await expect(cartContainer).toBeVisible();
    
    // Buttons should be properly sized for mobile
    const checkoutButton = page.locator('button:has-text("Proceed to Checkout")');
    const buttonBox = await checkoutButton.boundingBox();
    expect(buttonBox?.width).toBeGreaterThan(200);
  });

  test('should save cart to local storage for guest users', async ({ page }) => {
    // Mock guest user (no auth)
    await page.route('**/api/auth/me', async route => {
      await route.fulfill({ status: 401 });
    });

    await page.goto('/products');
    
    // Add item to cart as guest
    await page.click('button:has-text("Add to Cart")');
    
    // Check local storage
    const cartData = await page.evaluate(() => {
      return localStorage.getItem('guest-cart');
    });
    
    expect(cartData).toBeTruthy();
  });
});