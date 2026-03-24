import { initWebChannel } from './qwebchannel2.js';

const STATE_ERROR = 'error'
const STATE_LOADING = 'loading'
const STATE_READY = 'ready'


class TextLine {
    constructor(text) {
        this.text = text
        this.div = document.createElement("div");
        this.div.className = "script-line";

        this.span = document.createElement("span");
        this.span.className = "script-index";
        this.span.textContent = this.text
        this.div.appendChild(this.span)
    }

    getText() {
        return this.text
    }

    setText(text) {
        this.text = text
        this.span.textContent = this.text
    }

    appendText(text) {
        this.setText(`${this.getText()}${text}`)
    }
}

function getErrorText(error) {
    if (!error) {
        return "Error desconocido";
    }
    if (typeof error === "string") {
        return error;
    }
    if (error.stack) {
        return error.stack;
    }
    if (error.message) {
        return error.message;
    }
    try {
        return JSON.stringify(error);
    } catch (_ignored) {
        return String(error);
    }
}

function setPageState(state, error) {
    window.state = state
    const loadingView = document.getElementById("loadingView");
    const contentView = document.getElementById("contentView");
    const errorView = document.getElementById("errorView");
    const errorMessage = document.getElementById("errorMessage");
    console.log(`set window state to ${state}`);
    if (state === STATE_ERROR) {
        loadingView.style.display = "none";
        contentView.style.display = "none";
        errorView.style.display = "block";
        if (errorMessage) {
            console.error(error && error.stack ? error.stack : error)
            errorMessage.textContent = getErrorText(error);
        }
    } else if (state === STATE_READY) {
        loadingView.style.display = "none";
        contentView.style.display = "block";
        errorView.style.display = "none";
    } else {
        loadingView.style.display = "block";
        contentView.style.display = "none";
        errorView.style.display = "none";
    }
}

function addLine(text) {
    const log = document.querySelector(".script-log");
    if (!log) {
        return;
    }
    const line = new TextLine(text)
    log.appendChild(line.div);
    log.scrollTop = log.scrollHeight;

    return line
}

async function loadScripts(scripts) {
    console.log('Loading scripts')
    const total = scripts.length
    for (let i = 0; i < total; i += 1) {
        const position = i + 1;
        const scriptName = scripts[i];
        let line = addLine(`${position}/${total} - ${scriptName}...`);
        await import(`./scripts/${scriptName}`);
        if (line) {
            line.setText(`${line.getText()} DONE`);
        }
    }
}

function getScriptsList() {
    console.log('Getting scripts list')
    return [
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
}

function onError(error) {
    setPageState(STATE_ERROR, error);
};

function onDone() {
    setPageState(STATE_READY);
};

window.addEventListener("error", function (event) {
    const eventError = event && (event.error || event.message || event);
    setPageState(STATE_ERROR, eventError);
});

window.addEventListener("unhandledrejection", function (event) {
    const reason = event && event.reason ? event.reason : event;
    setPageState(STATE_ERROR, reason);
});


async function start() {
    setPageState(STATE_LOADING);
    let line = addLine('Creating qwebchannel... ');

    async function onQwebChannelReady() {
        console.log("onQwebChannelReady called");
        line.appendText(' DONE');
        try {
            const scripts = getScriptsList();
            await loadScripts(scripts);
            onDone();
        } catch (error) {
            onError(error);
        }
    }

    initWebChannel(onQwebChannelReady, onError);
}

start();
