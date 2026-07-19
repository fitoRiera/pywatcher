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
class CommandCall{
    constructor(name, args){
        this.name = name;
        this.args = args;
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

class IOChannel{
    getChannel(){
        if(metadata.channel == undefined){
            throw Exception("WebChannel not initialized yet!!");
        }
        return metadata.channel;
    }

    getBackend(message){
        if(metadata.backend == undefined){
            throw Exception("WebChannel not initialized yet!!");
        }
        return metadata.backend;
    }
}

class OutputChannel extends IOChannel{
    constructor(){
        super()
    }

    executeCommand(commandCall){
        const message = JSON.stringify(commandCall)
        this.getBackend().send_to_python(message)
    }

    fireEvent(event){
        const message = JSON.stringify(event)
        this.getBackend().send_to_python(message)
    }
}

class InputChannel extends IOChannel{
    executors = {}
    listeners = {}

    constructor(){
        super();
    }

    addCommandExecutor(executor){
        if(self.getExecutor(executor.name) != undefined){
            throw new Exception(`Executor '${executor.name}' already registered`);
        }
        self.executors[executor.name] = executor
    }

    addEventListener(eventName, listener){
        if(self.getExecutor(executor.name) != undefined){
            throw new Exception(`Executor '${executor.name}' already registered`);
        }
        let event_listeners = self.listeners.eventName
        if(event_listeners == undefined){
            event_listeners = []
            self.listeners.eventName = event_listeners
        }
        event_listeners.push(listener)
    }

    handleCommandCall(commandCall) {
        console.log(`handleCommandCall(${commandCall.name}, ${commandCall.args})`)
    }

    handleEvent(event) {
        console.log(`handleEvent(${event})`)
    }
}


const inputChannel = new InputChannel()
const outputChannel = new OutputChannel()

const metadata = {}
metadata.inputChannel = inputChannel;
metadata.outputChannel = outputChannel;

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
                outputChannel.fireEvent(
                    new Event('webchannel.lifecycle', 'iniWebChannel', null)
                )
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


export {CommandExecutor, outputChannel, inputChannel, initWebChannel}