import { readdir, mkdir, writeFile } from "node:fs/promises";
import { resolve, relative, dirname } from "node:path";
import {
  root,
  startLocalSite,
  launchReviewBrowser,
  prepareInterviewFixture,
  settlePage,
} from "./review-browser.mjs";

const args = process.argv.slice(2);
const outputIndex = args.indexOf("--output");
const output = resolve(
  root,
  outputIndex < 0 ? "ux-review" : args[outputIndex + 1],
);
const targetsIndex = args.indexOf("--targets");
const explicitTargets =
  targetsIndex < 0 ? null : args[targetsIndex + 1].split(",");
const skipDirectories = new Set([
  ".git",
  "node_modules",
  ".impeccable",
  "ux-review",
]);

async function discover(directory) {
  const pages = [];
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    if (entry.isDirectory() && !skipDirectories.has(entry.name)) {
      pages.push(...(await discover(resolve(directory, entry.name))));
    } else if (entry.isFile() && entry.name.endsWith(".html")) {
      pages.push(
        relative(root, resolve(directory, entry.name)).replaceAll("\\", "/"),
      );
    }
  }
  return pages.sort();
}

const pages = explicitTargets || (await discover(root));
const site = await startLocalSite();
const browser = await launchReviewBrowser();
const report = {
  browser: "Chrome (isolated headless Chromium)",
  pages: pages.length,
  captures: [],
  failures: [],
};
await mkdir(output, { recursive: true });

try {
  for (const viewport of [
    {
      name: "desktop",
      width: 1440,
      height: 1000,
      isMobile: false,
      hasTouch: false,
    },
    { name: "mobile", width: 390, height: 844, isMobile: true, hasTouch: true },
  ]) {
    const context = await browser.newContext({
      viewport: { width: viewport.width, height: viewport.height },
      deviceScaleFactor: 1,
      isMobile: viewport.isMobile,
      hasTouch: viewport.hasTouch,
      reducedMotion: "reduce",
    });
    await prepareInterviewFixture(context);
    let cursor = 0;
    let finished = 0;
    await Promise.all(
      Array.from({ length: 2 }, async () => {
        while (cursor < pages.length) {
          const target = pages[cursor++];
          const page = await context.newPage();
          const errors = [];
          page.on("pageerror", (error) => errors.push(error.message));
          try {
            const response = await page.goto(`${site.origin}/${target}`, {
              waitUntil: "load",
              timeout: 30000,
            });
            if (!response?.ok()) throw new Error(`HTTP ${response?.status()}`);
            await settlePage(page);
            const metrics = await page.evaluate(() => ({
              title: document.title,
              viewportWidth: innerWidth,
              scrollWidth: document.documentElement.scrollWidth,
              height: document.documentElement.scrollHeight,
              missingImages: [...document.images]
                .filter(
                  (image) =>
                    image.getAttribute("src")?.startsWith("assets/") &&
                    !image.naturalWidth,
                )
                .map((image) => image.getAttribute("src")),
            }));
            const filename = target.replace(/\.html$/, ".png");
            const screenshots = [];
            const tileHeight = 14000;
            const tiles = Math.ceil(metrics.height / tileHeight);
            for (let tile = 0; tile < tiles; tile += 1) {
              const path = resolve(
                output,
                viewport.name,
                tiles === 1
                  ? filename
                  : filename.replace(/\.png$/, `--part-${tile + 1}.png`),
              );
              await mkdir(dirname(path), { recursive: true });
              await page.screenshot({
                path,
                fullPage: true,
                animations: "disabled",
                ...(tiles > 1
                  ? {
                      clip: {
                        x: 0,
                        y: tile * tileHeight,
                        width: viewport.width,
                        height: Math.min(
                          tileHeight,
                          metrics.height - tile * tileHeight,
                        ),
                      },
                    }
                  : {}),
              });
              screenshots.push(relative(output, path));
            }
            report.captures.push({
              target,
              viewport: viewport.name,
              ...metrics,
              errors,
              screenshots,
            });
          } catch (error) {
            report.failures.push({
              target,
              viewport: viewport.name,
              error: error.message,
            });
          } finally {
            await page.close();
            finished += 1;
            if (finished % 20 === 0 || finished === pages.length)
              console.log(
                `${viewport.name}: ${finished}/${pages.length} pages captured`,
              );
          }
        }
      }),
    );
    await context.close();
  }
} finally {
  await browser.close();
  await site.close();
}
report.captures.sort((a, b) =>
  `${a.viewport}/${a.target}`.localeCompare(`${b.viewport}/${b.target}`),
);
await writeFile(
  resolve(output, "manifest.json"),
  JSON.stringify(report, null, 2) + "\n",
);
console.log(
  JSON.stringify({
    pages: report.pages,
    screenshots: report.captures.reduce(
      (sum, entry) => sum + entry.screenshots.length,
      0,
    ),
    failures: report.failures.length,
    output,
  }),
);
if (report.failures.length) {
  console.error(JSON.stringify(report.failures));
  process.exitCode = 1;
}
