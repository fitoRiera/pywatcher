const scripts = [
  "core-utils.js",
  "data-loader.js",
  "ui-widgets-enterprise-runtime-observability-telemetry-bootstrap-loader-client.js",
  "chart-engine.js",
  "net-bridge.js",
  "storage-cache.js",
  "formatters.js",
  "event-bus.js",
  "theme-manager.js",
  "app-shell.js",
];

const total = scripts.length;
const digits = String(total).length;
const log = document.querySelector(".script-log");
const loadingContainer = document.querySelector(".container");
const content = document.getElementById("content");

function addLine(position, scriptName) {
  if (!log) {
    return;
  }
  const line = document.createElement("div");
  line.className = "script-line";
  const current = String(position).padStart(digits, " ");

  const textPart = document.createElement("span");
  textPart.className = "script-index";
  textPart.id = `line-${position}`;
  textPart.textContent = `${current}/${total} - ${scriptName}...`;

  line.appendChild(textPart);
  log.appendChild(line);
  log.scrollTop = log.scrollHeight;

  return line
}

async function loadScripts() {
  for (let i = 0; i < total; i += 1) {
    const position = i + 1;
    const scriptName = scripts[i];
    addLine(position, scriptName);
    await import(`./scripts/${scriptName}`);

    const line = document.getElementById(`line-${position}`);
    if (line) {
      line.textContent = `${line.textContent} DONE`;
    }
  }

  if (loadingContainer) {
    loadingContainer.style.display = "none";
  }
  if (content) {
    content.style.display = "block";
  }
}

loadScripts();
