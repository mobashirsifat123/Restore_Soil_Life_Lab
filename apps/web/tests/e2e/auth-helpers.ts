import { expect, type Page } from "@playwright/test";

export type AuthUser = {
  email: string;
  password: string;
  name?: string;
  organization?: string;
};

export async function registerViaUi(page: Page, user: AuthUser) {
  await page.goto("/login");
  await page.getByRole("button", { name: "Request Access" }).click();

  await page.getByLabel("Full Name").fill(user.name ?? "E2E User");
  await page.getByLabel("Farm / Organization").fill(user.organization ?? "QA");
  await page.getByLabel("Email Address").fill(user.email);
  await page.getByLabel("Create Password").fill(user.password);
  await page.getByLabel(/I agree to the Terms of Service/i).check();
  await page.getByRole("button", { name: "Create Account" }).click();

  await expect(page).toHaveURL(/\/dashboard$/, { timeout: 30000 });
  await expect(page.getByRole("heading", { name: "Your member home" })).toBeVisible({
    timeout: 15000,
  });
}

export async function logoutViaUi(page: Page) {
  await page.goto("/logout?redirect=/login");
  await expect(page).toHaveURL(/\/login$/, { timeout: 15000 });
}

export async function loginViaUi(page: Page, user: Pick<AuthUser, "email" | "password">) {
  await page.goto("/login");
  await page.getByLabel("Email Address").fill(user.email);
  await page.getByLabel("Password").fill(user.password);
  await page.getByRole("button", { name: "Sign In to Workspace" }).click();

  await expect(page).toHaveURL(/\/dashboard$/, { timeout: 30000 });
  await expect(page.getByRole("heading", { name: "Your member home" })).toBeVisible({
    timeout: 15000,
  });
}

export async function requestResetLinkViaUi(page: Page, email: string) {
  await page.goto("/login");
  await page.getByRole("button", { name: "Forgot password?" }).click();
  await page.getByLabel("Email Address").fill(email);
  await page.getByRole("button", { name: "Send Reset Link" }).click();

  await expect(
    page.getByText("If that account exists, a password reset link has been sent.").last(),
  ).toBeVisible({ timeout: 15000 });
}
