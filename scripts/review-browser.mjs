import { chromium } from "playwright";
import { createServer } from "node:http";
import { readFile, stat } from "node:fs/promises";
import { resolve, sep, extname } from "node:path";
import { fileURLToPath } from "node:url";

export const root = fileURLToPath(new URL("../", import.meta.url));

export async function startLocalSite() {
  const types = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css",
    ".js": "text/javascript",
    ".mjs": "text/javascript",
    ".woff2": "font/woff2",
    ".svg": "image/svg+xml",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
    ".ico": "image/x-icon",
    ".pdf": "application/pdf",
    ".json": "application/json",
  };
  const server = createServer(async (request, response) => {
    try {
      const pathname = decodeURIComponent(
        new URL(request.url, "http://localhost").pathname,
      );
      let path = resolve(root, `.${pathname}`);
      if (path !== resolve(root) && !path.startsWith(resolve(root) + sep)) {
        response.writeHead(403).end();
        return;
      }
      if ((await stat(path)).isDirectory()) path = resolve(path, "index.html");
      const data = await readFile(path);
      response.writeHead(200, {
        "Content-Type": types[extname(path)] || "text/plain",
      });
      response.end(data);
    } catch {
      response
        .writeHead(404, { "Content-Type": "text/plain" })
        .end("Page not found");
    }
  });
  await new Promise((done) => server.listen(0, "127.0.0.1", done));
  return {
    origin: `http://127.0.0.1:${server.address().port}`,
    close: () => new Promise((done) => server.close(done)),
  };
}

export async function launchReviewBrowser() {
  return chromium.launch({
    channel: process.env.REVIEW_BROWSER_CHANNEL || "chrome",
    headless: true,
  });
}

export async function prepareInterviewFixture(context) {
  const content = await readFile(
    resolve(root, "interviews/uct-cto/index.html"),
    "utf8",
  );
  const hash = content.match(/const H\s*=\s*"([a-f0-9]{64})"/)?.[1];
  if (!hash) throw new Error("Interview review fixture hash is missing.");
  // This fixture is confined to the isolated browser's local static preview.
  await context.addInitScript((value) => {
    if (location.hostname !== "127.0.0.1") return;
    if (/\/interviews\/uct-cto\/(?:index\.html)?$/.test(location.pathname)) {
      sessionStorage.removeItem("_ig_auth");
    } else {
      sessionStorage.setItem("_ig_auth", value);
    }
  }, hash);
}

export async function settlePage(page) {
  await page.evaluate(async () => {
    const timeout = (ms) => new Promise((done) => setTimeout(done, ms));
    await Promise.race([document.fonts.ready, timeout(5000)]);
    if (window.MathJax?.startup?.promise) {
      await Promise.race([
        window.MathJax.startup.promise.catch(() => {}),
        timeout(5000),
      ]);
    }
    const images = [...document.images].map((image) => {
      image.loading = "eager";
      return image.decode().catch(() => {});
    });
    await Promise.race([Promise.all(images), timeout(8000)]);
    await new Promise(requestAnimationFrame);
    await new Promise(requestAnimationFrame);
  });
}
