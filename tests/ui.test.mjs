import assert from "node:assert/strict";
import { before, after, test } from "node:test";
import {
  startLocalSite,
  launchReviewBrowser,
  prepareInterviewFixture,
} from "../scripts/review-browser.mjs";

let site;
let browser;
before(async () => {
  site = await startLocalSite();
  browser = await launchReviewBrowser();
});
after(async () => {
  await browser?.close();
  await site?.close();
});

async function withPage(options, run) {
  const context = await browser.newContext({
    viewport: { width: 390, height: 844 },
    ...options,
  });
  await context.route("**/*", (route) =>
    route.request().url().startsWith(site.origin)
      ? route.continue()
      : route.abort(),
  );
  const page = await context.newPage();
  try {
    await run(page, context);
  } finally {
    await context.close();
  }
}

test("mesh deformation responds to the keyboard and has a static fallback", async () => {
  await withPage({}, async (page) => {
    await page.goto(site.origin + "/");
    const control = page.getByRole("slider", { name: "Mesh deformation" });
    await control.waitFor({ state: "visible" });
    const before = await page.locator("[data-mesh-surface]").innerHTML();
    await control.focus();
    await page.keyboard.press("End");
    assert.equal(await control.inputValue(), "100");
    assert.equal(
      await control.getAttribute("aria-valuetext"),
      "100% deformation",
    );
    assert.notEqual(
      await page.locator("[data-mesh-surface]").innerHTML(),
      before,
    );
  });
  await withPage({ javaScriptEnabled: false }, async (page) => {
    await page.goto(site.origin + "/");
    assert.equal(await page.locator(".mesh-fallback").isVisible(), true);
    assert.equal(
      await page
        .locator(".mesh-fallback")
        .evaluate((img) => img.complete && img.naturalWidth > 0),
      true,
    );
    assert.equal(await page.getByRole("slider").count(), 0);
  });
});

test("gallery controls and keyboard navigation stay synchronized with the images", async () => {
  await withPage({ reducedMotion: "reduce" }, async (page) => {
    await page.goto(site.origin + "/");
    const previous = page.getByRole("button", {
      name: "Previous Ecoride screenshot",
    });
    const next = page.getByRole("button", { name: "Next Ecoride screenshot" });
    const status = page.locator("[data-gallery-status]");
    assert.equal(await previous.isDisabled(), true);
    await next.click();
    await page.waitForFunction(
      () =>
        document.querySelector("[data-gallery-status]").textContent === "2 / 5",
    );
    assert.equal(await previous.isEnabled(), true);
    await page.locator(".project-slides").focus();
    await page.keyboard.press("ArrowLeft");
    await page.waitForFunction(
      () =>
        document.querySelector("[data-gallery-status]").textContent === "1 / 5",
    );
    assert.equal(await status.textContent(), "1 / 5");
    assert.equal(await previous.isDisabled(), true);
  });
});

for (const route of ["/", "/docs/guides/"]) {
  test(`mobile navigation contains focus, closes with Escape, and survives resizing: ${route}`, async () => {
    await withPage({}, async (page) => {
      await page.goto(site.origin + route);
      const button = page.getByRole("button", { name: "Toggle navigation" });
      await button.click();
      assert.equal(await button.getAttribute("aria-expanded"), "true");
      assert.equal(
        await page.locator("main").evaluate((element) => element.inert),
        true,
      );
      for (let i = 0; i < 12; i += 1) {
        await page.keyboard.press("Tab");
        assert.equal(
          await page.evaluate(() => {
            const menu = document.querySelector("[data-nav], .nav-links");
            const toggle = document.querySelector(
              "[data-menu-button], .hamburger",
            );
            return (
              menu.contains(document.activeElement) ||
              document.activeElement === toggle
            );
          }),
          true,
        );
      }
      await page.keyboard.press("Escape");
      assert.equal(await button.getAttribute("aria-expanded"), "false");
      assert.equal(
        await button.evaluate((element) => element === document.activeElement),
        true,
      );
      assert.equal(
        await page.locator("main").evaluate((element) => element.inert),
        false,
      );
      await button.click();
      await page.setViewportSize({ width: 1440, height: 900 });
      await page.waitForFunction(() => !document.querySelector("main").inert);
      assert.equal(
        await page.locator("main").evaluate((element) => element.inert),
        false,
      );
      assert.equal(
        await page
          .locator("[data-menu-button], .hamburger")
          .getAttribute("aria-expanded"),
        "false",
      );
    });
  });
}

test("guide search exposes selection and an accessible empty result", async () => {
  await withPage({}, async (page) => {
    await page.goto(site.origin + "/docs/guides/");
    const data = page.getByRole("button", { name: "Data", exact: true });
    await data.click();
    assert.equal(await data.getAttribute("aria-pressed"), "true");
    assert.equal(
      await page
        .getByRole("button", { name: "All", exact: true })
        .getAttribute("aria-pressed"),
      "false",
    );
    await page.getByRole("searchbox").fill("zzzauditnomatch 🧪 العربية");
    assert.equal(await page.getByRole("status").textContent(), "0 guides");
    assert.equal(await page.locator("[data-empty-state]").isVisible(), true);
    assert.equal(await page.locator("[data-guide-card]:visible").count(), 0);
    await page.getByRole("searchbox").fill("");
    assert.ok((await page.locator("[data-guide-card]:visible").count()) > 0);
  });
});

test("dropdown and course disclosure work with keyboard activation", async () => {
  await withPage({}, async (page) => {
    await page.goto(site.origin + "/learning/ibm-data-engineering/");
    const dropdown = page.locator(".dropdown-button").first();
    await dropdown.focus();
    await page.keyboard.press("Enter");
    assert.equal(await dropdown.getAttribute("aria-expanded"), "true");
    await page.keyboard.press("ArrowDown");
    assert.equal(
      await page.evaluate(
        () => document.activeElement.closest(".dropdown-content") !== null,
      ),
      true,
    );
    await page.keyboard.press("Escape");
    assert.equal(
      await dropdown.evaluate((element) => element === document.activeElement),
      true,
    );
    assert.equal(await dropdown.getAttribute("aria-expanded"), "false");
    const disclosure = page.locator(".expand-btn").first();
    await disclosure.focus();
    await page.keyboard.press("Space");
    assert.equal(await disclosure.getAttribute("aria-expanded"), "true");
    assert.equal(await disclosure.textContent(), "Show less");
    assert.equal(
      await page.locator(".expand-wrapper").first().isVisible(),
      true,
    );
    await page.keyboard.press("Space");
    assert.equal(await disclosure.getAttribute("aria-expanded"), "false");
    assert.equal(
      await page.locator(".expand-wrapper").first().isVisible(),
      false,
    );
  });
});

test("interview answer disclosure remains usable with reduced motion", async () => {
  await withPage({ reducedMotion: "reduce" }, async (page, context) => {
    await prepareInterviewFixture(context);
    await page.goto(site.origin + "/interviews/uct-cto/level3-competency.html");
    const question = page.locator(".qa-question").first();
    await question.focus();
    await page.keyboard.press("Space");
    assert.equal(await question.getAttribute("aria-expanded"), "true");
    assert.equal(await page.locator(".qa-answer").first().isVisible(), true);
    assert.equal(
      await page
        .locator(".qa-answer")
        .first()
        .evaluate((element) => getComputedStyle(element).animationName),
      "none",
    );
  });
});

test("access form labels visibility and preserves an incorrect code", async () => {
  await withPage({}, async (page) => {
    await page.goto(site.origin + "/interviews/uct-cto/index.html");
    const input = page.getByLabel("Access code", { exact: true });
    await input.fill("an-incorrect-review-code");
    await page.getByRole("button", { name: "Show access code" }).click();
    assert.equal(await input.getAttribute("type"), "text");
    assert.equal(
      await page
        .getByRole("button", { name: "Hide access code" })
        .getAttribute("aria-pressed"),
      "true",
    );
    await input.press("Enter");
    await page.getByRole("alert").waitFor({ state: "visible" });
    assert.equal(await input.inputValue(), "an-incorrect-review-code");
    assert.equal(await input.getAttribute("aria-invalid"), "true");
    assert.equal(
      await page.getByRole("button", { name: "Unlock" }).isEnabled(),
      true,
    );
  });
});

test("presentation fits mobile, exposes reading content, and reports unavailable PDF export", async () => {
  await withPage({ reducedMotion: "reduce" }, async (page) => {
    await page.goto(site.origin + "/presentations/africomp7/index.html");
    assert.equal(
      await page
        .locator(".supervisor-profile")
        .evaluateAll((profiles) =>
          profiles.every(
            (profile) => profile.getBoundingClientRect().right <= innerWidth,
          ),
        ),
      true,
    );
    assert.equal(
      await page
        .locator(".reveal")
        .evaluateAll((sections) =>
          sections.every(
            (section) => getComputedStyle(section).opacity === "1",
          ),
        ),
      true,
    );
    const download = page.getByRole("button", {
      name: "Download PDF",
    });
    await download.focus();
    await page.keyboard.press("Space");
    await page.waitForFunction(
      () => !document.getElementById("pdf-export-status").hidden,
    );
    assert.match(
      await page.getByRole("status").textContent(),
      /Refresh the page/,
    );
    assert.equal(await download.isEnabled(), true);
  });
});

test("static navigation and reading remain available without JavaScript", async () => {
  await withPage({ javaScriptEnabled: false }, async (page) => {
    await page.goto(site.origin + "/");
    assert.equal(
      await page
        .getByRole("link", { name: "Tech Guides", exact: true })
        .first()
        .isVisible(),
      true,
    );
    await page.goto(site.origin + "/docs/guides/");
    assert.equal(
      await page.locator("[data-guide-card]").first().isVisible(),
      true,
    );
    assert.equal(await page.locator(".docs-toolbar").isVisible(), false);
  });
});

test("learning content survives unavailable third-party scripts", async () => {
  await withPage({}, async (page) => {
    const errors = [];
    page.on("pageerror", (error) => errors.push(error.message));
    await page.goto(
      site.origin +
        "/learning/ibm-data-engineering/course-9/module-1/lecture-1.html",
    );
    assert.equal(await page.locator("main h1").isVisible(), true);
    assert.deepEqual(errors, []);
  });
});

test("native gallery handles synthesized touch, cancellation, and vertical page scrolling", async () => {
  await withPage({ isMobile: true, hasTouch: true }, async (page, context) => {
    await page.goto(site.origin + "/");
    const gallery = page.locator(".project-slides").first();
    await gallery.scrollIntoViewIfNeeded();
    const box = await gallery.boundingBox();
    const session = await context.newCDPSession(page);
    const y = box.y + Math.min(box.height / 2, 200);
    const startX = box.x + box.width * 0.85;
    await session.send("Input.dispatchTouchEvent", {
      type: "touchStart",
      touchPoints: [{ x: startX, y }],
    });
    for (let i = 1; i <= 8; i += 1) {
      await session.send("Input.dispatchTouchEvent", {
        type: "touchMove",
        touchPoints: [{ x: startX - (box.width * 0.6 * i) / 8, y }],
      });
      await page.waitForTimeout(20);
    }
    await session.send("Input.dispatchTouchEvent", {
      type: "touchEnd",
      touchPoints: [],
    });
    await page.waitForFunction(
      () => document.querySelector(".project-slides").scrollLeft > 0,
    );
    await session.send("Input.dispatchTouchEvent", {
      type: "touchStart",
      touchPoints: [{ x: startX, y }],
    });
    await session.send("Input.dispatchTouchEvent", {
      type: "touchCancel",
      touchPoints: [],
    });
    const before = await page.evaluate(() => scrollY);
    await session.send("Input.dispatchTouchEvent", {
      type: "touchStart",
      touchPoints: [{ x: box.x + box.width / 2, y: y + 70 }],
    });
    for (let i = 1; i <= 6; i += 1) {
      await session.send("Input.dispatchTouchEvent", {
        type: "touchMove",
        touchPoints: [{ x: box.x + box.width / 2, y: y + 70 - i * 22 }],
      });
      await page.waitForTimeout(20);
    }
    await session.send("Input.dispatchTouchEvent", {
      type: "touchEnd",
      touchPoints: [],
    });
    await page.waitForFunction((value) => scrollY > value, before);
  });
});

test("assessment links activate independently of native checklist state", async () => {
  await withPage({}, async (page, context) => {
    await prepareInterviewFixture(context);
    await page.goto(
      site.origin + "/interviews/uct-cto/assessment-cto-architecture.html",
    );
    const checkbox = page.getByRole("checkbox", {
      name: "Create a clean diagram on Excalidraw or Draw.io",
    });
    const link = page.getByRole("link", {
      name: "excalidraw.com",
      exact: true,
    });
    await link.focus();
    const popupPromise = page.waitForEvent("popup");
    await page.keyboard.press("Enter");
    const popup = await popupPromise;
    assert.equal(await checkbox.isChecked(), false);
    await popup.close();
    assert.match(
      await link.evaluate((el) => getComputedStyle(el).textDecorationLine),
      /underline/,
    );
    await checkbox.focus();
    await page.keyboard.press("Space");
    assert.equal(await checkbox.isChecked(), true);
    assert.ok(
      Number(
        await page
          .getByRole("progressbar", { name: "Preparation Progress" })
          .getAttribute("aria-valuenow"),
      ) > 0,
    );
    await page.reload();
    assert.equal(await checkbox.isChecked(), true);
    page.once("dialog", (dialog) => dialog.accept());
    await page.locator("#resetBtn").click();
    assert.equal(await checkbox.isChecked(), false);
    await checkbox.check();
    await page.reload();
    assert.equal(
      await page.locator('input[type="checkbox"]:checked').count(),
      1,
    );
  });
});

test("all seven assessment progress bars have visible labels and tolerate unavailable storage", async () => {
  await withPage({}, async (page, context) => {
    await prepareInterviewFixture(context);
    await context.addInitScript(() => {
      Object.defineProperty(window, "localStorage", {
        value: {
          getItem() {
            throw new Error("Storage unavailable");
          },
          setItem() {
            throw new Error("Storage unavailable");
          },
          removeItem() {
            throw new Error("Storage unavailable");
          },
        },
      });
    });
    for (const name of [
      "cto-architecture",
      "de-docker",
      "de-wsl",
      "iot-edge",
      "web-servers-dotnet",
      "web-servers-python",
      "tips-strategy",
    ]) {
      await page.goto(
        `${site.origin}/interviews/uct-cto/assessment-${name}.html`,
      );
      const progress = page.getByRole("progressbar", {
        name: "Preparation Progress",
      });
      assert.equal(await progress.count(), 1, name);
      await page.getByRole("checkbox").first().check();
      assert.ok(Number(await progress.getAttribute("aria-valuenow")) > 0, name);
    }
  });
});

test("standalone guide links provide 44px touch targets", async () => {
  await withPage({}, async (page) => {
    for (const [path, selector] of [
      ["/", ".guide-feature > a"],
      ["/docs/guides/", ".guide-card > a"],
      [
        "/docs/system-scripts/",
        ".docs-container > .grid > .card :is(h2, h3) a",
      ],
    ]) {
      await page.goto(site.origin + path);
      const sizes = await page
        .locator(selector)
        .evaluateAll((elements) =>
          elements.map((el) => el.getBoundingClientRect().height),
        );
      assert.ok(sizes.length, path);
      assert.ok(
        sizes.every((height) => height >= 44),
        `${path}: ${sizes}`,
      );
    }
  });
});

test("PDF export waits for original images and restores responsive sources after success or failure", async () => {
  await withPage({}, async (page) => {
    await page.goto(site.origin + "/presentations/africomp7/index.html");
    const before = await page.locator("img").evaluateAll((images) =>
      images.map((image) => ({
        src: image.getAttribute("src"),
        srcset: image.getAttribute("srcset"),
        loading: image.getAttribute("loading"),
      })),
    );
    for (const fail of [false, true]) {
      await page.evaluate((fail) => {
        window.exportCaptured = null;
        window.exportedSections = [];
        window.html2pdf = () => ({
          pdf: { addPage() {} },
          canvas: { width: 100, height: 100 },
          set(options) {
            if (options.pdf) this.pdf = options.pdf;
            return this;
          },
          from(section) {
            window.exportedSections.push(section.id);
            return this;
          },
          async toPdf() {},
          async get(key) {
            return this[key];
          },
          async save() {
            window.exportCaptured = [...document.images].map((image) => ({
              ready: image.complete && image.naturalWidth > 0,
              original: image.getAttribute("src") === image.dataset.printSrc,
              loading: image.loading,
            }));
            if (fail) throw new Error("Simulated PDF failure");
          },
        });
      }, fail);
      await page.locator("#downloadPdfBtn").click();
      await page.waitForFunction(
        () =>
          window.exportCaptured &&
          !document.querySelector("#downloadPdfBtn").disabled,
      );
      assert.ok(
        await page.evaluate(() =>
          exportCaptured.every(
            (image) =>
              image.ready && image.original && image.loading === "eager",
          ),
        ),
      );
      assert.deepEqual(
        await page.evaluate(() => exportedSections),
        await page
          .locator("main > .slide")
          .evaluateAll((sections) => sections.map((section) => section.id)),
      );
      assert.deepEqual(
        await page.locator("img").evaluateAll((images) =>
          images.map((image) => ({
            src: image.getAttribute("src"),
            srcset: image.getAttribute("srcset"),
            loading: image.getAttribute("loading"),
          })),
        ),
        before,
      );
      assert.equal(
        await page
          .locator("body")
          .evaluate((el) => el.classList.contains("pdf-export-mode")),
        false,
      );
      if (fail)
        assert.match(await page.getByRole("status").textContent(), /failed/);
    }
  });
});

test("technical pages reflow at 320px and enlarged portfolio text stays in its grid", async () => {
  await withPage(
    { viewport: { width: 320, height: 844 } },
    async (page, context) => {
      await prepareInterviewFixture(context);
      for (const path of [
        "/docs/guides/DJANGO_MULTI-AUTHENTICATION_POWERSHELL_POWERUSER_GUIDE.html",
        "/interviews/uct-cto/assessment-web-servers-python.html",
        "/learning/ibm-data-engineering/course-9/module-1/lecture-7.html",
        "/presentations/africomp7/index.html",
      ]) {
        await page.goto(site.origin + path);
        assert.equal(
          await page.evaluate(
            () => document.documentElement.scrollWidth <= innerWidth,
          ),
          true,
          path,
        );
      }
      await page.setViewportSize({ width: 1440, height: 1000 });
      for (const path of [
        "/",
        "/docs/",
        "/presentations/africomp7/index.html",
      ]) {
        await page.goto(site.origin + path);
        await page.evaluate(
          () => (document.documentElement.style.fontSize = "200%"),
        );
        assert.equal(
          await page.evaluate(
            () => document.documentElement.scrollWidth <= innerWidth,
          ),
          true,
          path,
        );
        if (path === "/")
          assert.equal(
            await page
              .locator(".capability-grid h3")
              .evaluateAll((headings) =>
                headings.every(
                  (heading) => heading.scrollWidth <= heading.clientWidth + 1,
                ),
              ),
            true,
          );
      }
    },
  );
});
