// TODO: Renombrar este archivo a qwebchannel.js y eliminar la duplicidad en el plugin WWD
class AbstractMethodError extends Error {
  constructor(message) {
    if (message == undefined){
        message = 'Must be override by child class';
    }
    super(message);
    this.name = "AbstractMethodError";
  }
}

class CommandExecutor{
    constructor(commandName){
        this.name = commandName
    }

    execute(args){
        throw AbstractMethodError()
    }
}

class Event{
    constructor(name, source, details){
        this.name = name;
        this.source = source;
        this.details = details;
    }
}

class EventListener{
    onEvent(event){
        throw AbstractMethodError()
    }
}

class OutputChannel{
    constructor(){
    }

    executeCommand(name, args){
        throw AbstractMethodError()
    }

    fireEvent(event){
        throw AbstractMethodError()
    }
}

class InputChannel{
    constructor(){
    }

    addCommandExecutor(executor){
        return this.addCommand(executor.name, executor)
    }

    addEventListener(eventName, listener){
        throw AbstractMethodError()
    }
}


const metadata = {}

function initWebChannel(onDone, onError, attempt) {
    console.log("initWebChannel...")

    if(attempt==undefined){
        attempt = 1
    }

    var retries = typeof attempt === "number" ? attempt : 0;
    var qtObject = (typeof qt !== "undefined" && qt) || window.qt;
    var hasTransport = qtObject && qtObject.webChannelTransport;

    if (window.QWebChannel && hasTransport) {
        console.log("creating QWebChannel...")
        try{
            var qWebChannel = new QWebChannel(qtObject.webChannelTransport, function (channel) {
                metadata.channel = channel;
                metadata.backend = channel.objects.backend;
                metadata.backendReady = true;
            });
            console.log("QWebChannel ready :D")
            onDone()
        } catch(error){
            console.log("QWebChannel error :(")
            onError(error)
        }
        return;
    } else {
        console.log("window.QWebChannel && hasTransport=", (window.QWebChannel && hasTransport))
    }

    if (retries < 50) {
        window.setTimeout(function () {
            initWebChannel(onDone, onError, retries + 1);
        }, 100);
        return;
    }

    onError("No se pudo inicializar QWebChannel.");
};

export {CommandExecutor, OutputChannel, InputChannel, initWebChannel}