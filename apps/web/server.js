import { createReadStream, existsSync } from "node:fs";
import { readFile } from "node:fs/promises";
import http from "node:http";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { execFile } from "node:child_process";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const projectRoot = path.resolve(__dirname, "..", "..");
const port = Number(process.env.PORT || 4173);

const contentTypes = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
};

function sendJson(response, status, payload) {
  response.writeHead(status, { "Content-Type": "application/json; charset=utf-8" });
  response.end(JSON.stringify(payload));
}

function runPipeline(response) {
  const apiPath = path.join(__dirname, "web_api.py");
  execFile(
    "python",
    [apiPath],
    {
      cwd: projectRoot,
      timeout: 120000,
      maxBuffer: 1024 * 1024 * 8,
    },
    (error, stdout, stderr) => {
      if (error) {
        sendJson(response, 500, {
          ok: false,
          error: stderr || error.message,
        });
        return;
      }

      try {
        sendJson(response, 200, JSON.parse(stdout));
      } catch (parseError) {
        sendJson(response, 500, {
          ok: false,
          error: parseError.message,
          raw: stdout,
        });
      }
    },
  );
}

async function serveStatic(request, response) {
  const url = new URL(request.url, `http://localhost:${port}`);
  const routePath = url.pathname === "/" ? "/index.html" : url.pathname;
  const filePath = path.normalize(path.join(__dirname, routePath));

  if (!filePath.startsWith(__dirname) || !existsSync(filePath)) {
    sendJson(response, 404, { ok: false, error: "not found" });
    return;
  }

  const extension = path.extname(filePath);
  response.writeHead(200, { "Content-Type": contentTypes[extension] || "application/octet-stream" });
  createReadStream(filePath).pipe(response);
}

const server = http.createServer(async (request, response) => {
  if (request.method === "POST" && request.url === "/api/run") {
    runPipeline(response);
    return;
  }

  if (request.method === "GET" && request.url === "/api/health") {
    sendJson(response, 200, { ok: true });
    return;
  }

  if (request.method === "GET" && request.url === "/api/design") {
    const designPath = path.join(projectRoot, "web_design.txt");
    const design = await readFile(designPath, "utf-8");
    sendJson(response, 200, { ok: true, design });
    return;
  }

  if (request.method === "GET") {
    serveStatic(request, response);
    return;
  }

  sendJson(response, 405, { ok: false, error: "method not allowed" });
});

server.listen(port, () => {
  console.log(`Randomiser web app: http://localhost:${port}`);
});
