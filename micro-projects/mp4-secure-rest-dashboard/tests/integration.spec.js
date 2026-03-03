import { expect, test } from "@playwright/test";

async function ensureServiceWorkerControl(page) {
  await page.goto("/#/login");
  await page.waitForFunction(() => "serviceWorker" in navigator);
  await page.evaluate(() => navigator.serviceWorker.ready);

  let isControlled = await page.evaluate(() => Boolean(navigator.serviceWorker.controller));
  if (!isControlled) {
    await page.reload();
    await page.waitForFunction(() => Boolean(navigator.serviceWorker.controller), null, { timeout: 20_000 });
    isControlled = true;
  }

  expect(isControlled).toBeTruthy();
}

test("register -> create task -> analytics via service worker API", async ({ page }) => {
  await ensureServiceWorkerControl(page);

  const username = `mp4user${Date.now()}`;
  const taskTitle = `Integration task ${Date.now()}`;

  await page.getByRole("tab", { name: "Register" }).click();
  await page.getByLabel("Username").fill(username);
  await page.locator("#password").fill("pass12345");
  await page.locator("#confirmPassword").fill("pass12345");

  const registerResponsePromise = page.waitForResponse((response) => {
    return response.url().includes("/api/auth/register") && response.request().method() === "POST";
  });

  await page.locator("form button[type='submit']").click();
  const registerResponse = await registerResponsePromise;
  expect(registerResponse.status()).toBe(201);
  await expect(page).toHaveURL(/#\/tasks/);

  await page.getByRole("button", { name: "Add Task" }).click();
  await page.getByLabel("Title").fill(taskTitle);

  const createTaskResponsePromise = page.waitForResponse((response) => {
    return response.url().includes("/api/tasks") && response.request().method() === "POST";
  });

  await page.getByRole("button", { name: "Create Task" }).click();
  const createTaskResponse = await createTaskResponsePromise;
  expect(createTaskResponse.status()).toBe(201);
  await expect(page.getByRole("heading", { name: taskTitle })).toBeVisible();

  const summaryResponsePromise = page.waitForResponse((response) => {
    return response.url().includes("/api/analytics/summary");
  });
  const trendsResponsePromise = page.waitForResponse((response) => {
    return response.url().includes("/api/analytics/trends");
  });

  await page.getByRole("link", { name: "Analytics" }).click();
  await expect(page).toHaveURL(/#\/analytics/);
  await expect(page.getByRole("heading", { name: "Analytics Dashboard" })).toBeVisible();

  const summaryResponse = await summaryResponsePromise;
  const trendsResponse = await trendsResponsePromise;
  expect(summaryResponse.status()).toBe(200);
  expect(trendsResponse.status()).toBe(200);
});
