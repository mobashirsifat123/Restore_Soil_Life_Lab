import { expect, test } from "@playwright/test";
import { loginViaUi, logoutViaUi, registerViaUi, requestResetLinkViaUi } from "./auth-helpers";

test.describe("Authentication flows", () => {
  test.setTimeout(90_000);

  test("login with valid credentials redirects to dashboard", async ({ page }) => {
    const timestamp = Date.now();
    const user = {
      email: `auth-login-${timestamp}@example.com`,
      password: "Password123!",
      name: "Auth Login User",
      organization: "QA",
    };

    await registerViaUi(page, user);
    await logoutViaUi(page);
    await loginViaUi(page, user);
  });

  test("login with invalid credentials shows an error message", async ({ page }) => {
    await page.goto("/login");
    await page.getByLabel("Email Address").fill("nobody@example.com");
    await page.getByLabel("Password").fill("WrongPassword123!");
    await page.getByRole("button", { name: "Sign In to Workspace" }).click();

    await expect(page.getByText("Invalid email or password.").last()).toBeVisible({
      timeout: 15000,
    });
    await expect(page).toHaveURL(/\/login$/, { timeout: 15000 });
  });

  test("registration with a new user reaches the member dashboard", async ({ page }) => {
    const timestamp = Date.now();
    const user = {
      email: `auth-register-${timestamp}@example.com`,
      password: "Password123!",
      name: "Auth Register User",
      organization: "QA",
    };

    await registerViaUi(page, user);
  });

  test("forgot password shows a success message after submitting an email", async ({ page }) => {
    const timestamp = Date.now();
    const user = {
      email: `auth-forgot-${timestamp}@example.com`,
      password: "Password123!",
      name: "Auth Forgot User",
      organization: "QA",
    };

    await registerViaUi(page, user);
    await logoutViaUi(page);
    await requestResetLinkViaUi(page, user.email);
  });

  test("reset password with a valid token in the URL updates the password", async ({ page }) => {
    const timestamp = Date.now();
    const user = {
      email: `auth-reset-${timestamp}@example.com`,
      password: "Password123!",
      name: "Auth Reset User",
      organization: "QA",
    };
    const newPassword = "Password456!";

    await registerViaUi(page, user);
    await logoutViaUi(page);
    await requestResetLinkViaUi(page, user.email);

    const resetLink = page.getByRole("link", { name: "Open Reset Page" });
    await expect(resetLink).toBeVisible({ timeout: 15000 });
    await resetLink.click();

    await expect(page).toHaveURL(/\/reset-password\?token=/, { timeout: 15000 });
    await expect(page.getByLabel("New Password")).toBeEnabled({ timeout: 15000 });
    await page.getByLabel("New Password").fill(newPassword);
    await expect(page.getByRole("button", { name: "Reset Password" })).toBeEnabled({
      timeout: 15000,
    });
    await page.getByRole("button", { name: "Reset Password" }).click();

    await expect(page.getByText(/Password successfully reset/i).last()).toBeVisible({
      timeout: 15000,
    });

    await page.getByRole("link", { name: "Return to Sign In" }).click();
    await expect(page).toHaveURL(/\/login$/, { timeout: 15000 });

    await page.getByLabel("Email Address").fill(user.email);
    await page.getByLabel("Password").fill(newPassword);
    await page.getByRole("button", { name: "Sign In to Workspace" }).click();

    await expect(page).toHaveURL(/\/dashboard$/, { timeout: 30000 });
  });
});
