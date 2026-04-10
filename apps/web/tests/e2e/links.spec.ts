import { expect, test } from "@playwright/test";

const marketingPages = [
  "/",
  "/about",
  "/science",
  "/blog",
  "/case-studies",
  "/contact",
  "/privacy",
  "/terms",
  "/cookies",
  "/login",
];

test.describe("Hyperlink audit", () => {
  test("security headers are present on public responses", async ({ page }) => {
    const response = await page.request.get("/");
    expect(response.status()).toBeLessThan(400);
    const headers = response.headers();
    expect(headers["x-content-type-options"]).toBe("nosniff");
    expect(headers["x-frame-options"]).toBe("DENY");
    expect(headers["referrer-policy"]).toBe("strict-origin-when-cross-origin");
    expect(headers["permissions-policy"]).toContain("camera=()");
  });

  test("all discovered internal links from key pages should resolve", async ({ page }) => {
    const discoveredLinks = new Set<string>();
    const placeholderLinks = new Set<string>();

    for (const path of marketingPages) {
      await page.goto(path);

      const hrefs = await page.$$eval("a[href]", (anchors) =>
        anchors
          .map((anchor) => anchor.getAttribute("href"))
          .filter((value): value is string => Boolean(value)),
      );

      for (const href of hrefs) {
        if (href === "#" || href === "/#") {
          placeholderLinks.add(`${path} -> ${href}`);
          continue;
        }
        if (href.startsWith("/")) {
          discoveredLinks.add(href.split("#")[0] ?? href);
        }
      }
    }

    expect(Array.from(placeholderLinks)).toEqual([]);

    for (const href of discoveredLinks) {
      const response = await page.request.get(href, { maxRedirects: 10 });
      expect(
        response.status(),
        `Expected "${href}" to resolve without client/server error`,
      ).toBeLessThan(400);
    }
  });
});
