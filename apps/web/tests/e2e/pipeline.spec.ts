import { expect, test } from "@playwright/test";
import { loginViaUi, logoutViaUi, registerViaUi } from "./auth-helpers";

test.describe("End-to-End Simulation Pipeline", () => {
  test.setTimeout(120_000);

  test("should allow a user to create a project, sample, scenario, and run", async ({ page }) => {
    const timestamp = Date.now();
    const user = {
      email: `pipeline-e2e-${timestamp}@example.com`,
      password: "Password123!",
      name: "E2E Pipeline User",
      organization: "QA",
    };

    await registerViaUi(page, user);
    await logoutViaUi(page);
    await loginViaUi(page, user);

    await page.goto("/projects/new");
    await expect(page).toHaveURL(/\/projects\/new$/);

    const projectName = `E2E Project ${timestamp}`;
    await page.getByPlaceholder("North pasture regeneration program").fill(projectName);
    await page
      .getByPlaceholder(
        "A project for collecting baseline soil biology measurements and testing scenario outcomes over time.",
      )
      .fill("E2E pipeline project");
    await page.getByRole("button", { name: "Create project" }).click();

    await expect(page).toHaveURL(/\/projects\/[0-9a-f-]+$/, { timeout: 30000 });
    await expect(page.getByRole("heading", { name: projectName })).toBeVisible();

    await page.getByRole("link", { name: "Add sample" }).first().click();
    await expect(page).toHaveURL(/\/projects\/[0-9a-f-]+\/samples\/new$/, {
      timeout: 15000,
    });

    const sampleCode = `SAMPLE-${timestamp.toString().slice(-6)}`;
    await page.getByLabel("Sample code").fill(sampleCode);
    await page.getByLabel("Sample name").fill("E2E Sample");
    await page.getByRole("button", { name: "Create soil sample" }).click();

    await expect(page).toHaveURL(/\/projects\/[0-9a-f-]+$/, { timeout: 30000 });
    await expect(page.getByText(sampleCode)).toBeVisible();

    await page.getByRole("link", { name: "Create scenario" }).first().click();
    await expect(page).toHaveURL(/\/projects\/[0-9a-f-]+\/scenarios\/new$/, {
      timeout: 15000,
    });

    const scenarioName = `E2E Scenario ${timestamp}`;
    await page.getByLabel("Scenario name").fill(scenarioName);
    await page.getByRole("button", { name: "Create scenario" }).click();

    await expect(page).toHaveURL(/\/projects\/[0-9a-f-]+$/, { timeout: 30000 });
    const submitRunButton = page.getByRole("button", { name: "Submit simulation run" }).first();
    await expect(submitRunButton).toBeVisible({ timeout: 15000 });
    await submitRunButton.click();
    await expect(page).toHaveURL(/\/runs\/[0-9a-f-]+$/, { timeout: 60000 });
    await expect(page.getByText("succeeded").first()).toBeVisible({ timeout: 30000 });
    await expect(page.getByRole("heading", { name: "Result summary" })).toBeVisible({
      timeout: 30000,
    });
  });
});
