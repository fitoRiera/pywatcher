(function initWebChannel(attempt) {
    console.log("initWebChannel...")

    var retries = typeof attempt === "number" ? attempt : 0;
    var qtObject = (typeof qt !== "undefined" && qt) || window.qt;
    var hasTransport = qtObject && qtObject.webChannelTransport;

    if (window.QWebChannel && hasTransport) {
        console.log("creating QWebChannel...")
        try{
            var qWebChannel = new QWebChannel(qtObject.webChannelTransport, function (channel) {
                window.channel = channel;
                window.backend = channel.objects.backend;
                window.backendReady = true;
                console.log("dispatching event...");
                window.addEventListener("backend-ready", function () {
                  console.log("evento backend-ready recibido en qwebchannel.js")
                });
                window.dispatchEvent(new CustomEvent("backend-ready"));
                console.log("QWebChannel backend inicializado.");
            });
        } catch(error){
            console.error(error)
        }
        return;
    } else {
        console.log("window.QWebChannel && hasTransport=", (window.QWebChannel && hasTransport))
    }

    if (retries < 50) {
        window.setTimeout(function () {
            initWebChannel(retries + 1);
        }, 100);
        return;
    }

    console.warn("No se pudo inicializar QWebChannel.");
}());
