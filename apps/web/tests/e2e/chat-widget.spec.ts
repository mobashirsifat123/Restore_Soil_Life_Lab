import { expect, test } from "@playwright/test";

test.describe("BioSilk Chat Widget", () => {
  test("floating launcher stays visible in viewport and can open/close", async ({ page }) => {
    await page.goto("/");

    const launcher = page.getByRole("button", { name: "BioSilk Chat" });
    await expect(launcher).toBeVisible();

    const viewport = page.viewportSize();
    const box = await launcher.boundingBox();
    expect(viewport).not.toBeNull();
    expect(box).not.toBeNull();

    if (!viewport || !box) {
      throw new Error("Missing viewport or launcher bounds.");
    }

    expect(box.x).toBeGreaterThanOrEqual(0);
    expect(box.y).toBeGreaterThanOrEqual(0);
    expect(box.x + box.width).toBeLessThanOrEqual(viewport.width);
    expect(box.y + box.height).toBeLessThanOrEqual(viewport.height);

    await launcher.click();
    await expect(page.getByRole("button", { name: "Minimize chat" })).toBeVisible();

    await page.getByRole("button", { name: "Minimize chat" }).click();
    await expect(launcher).toBeVisible();
  });

  test("hero chat link opens chat page with active composer", async ({ page }) => {
    await page.goto("/");
    const heroChatLink = page.locator('a[href="/chat"]').first();
    await expect(heroChatLink).toBeVisible();
    await heroChatLink.click();

    await expect(page).toHaveURL(/\/chat$/, { timeout: 10000 });
    await expect(page.locator('textarea[placeholder*="Ask"]')).toBeVisible();
  });

  test("footer cookie policy link opens a valid page", async ({ page }) => {
    await page.goto("/");

    const cookieLink = page.locator('footer a[href="/cookies"]').first();
    await cookieLink.scrollIntoViewIfNeeded();
    await cookieLink.click();

    await expect(page).toHaveURL(/\/cookies$/, { timeout: 10000 });
    await expect(page.getByRole("heading", { name: "Cookie Policy" })).toBeVisible();
  });
});
