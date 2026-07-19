// TODO: Renombrar este archivo a qwebchannel.js y eliminar la duplicidad en el plugin WWD


const COMMAND_CALL_RESPONSE_OK="ACK"
const COMMAND_CALL_RESPONSE_ERROR_EXECUTOR_NOT_FOUND="EXECUTOR_NOT_FOUND"
const COMMAND_CALL_RESPONSE_ERROR_PARSING_RESPONSE="ERROR_PARSING_RESPONSE"
const COMMAND_CALL_RESPONSE_ERROR_EXECUTOR_FAILS="EXECUTOR_FAILS"

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

    /**
     * @param {object} args
     * @returns {CommandCallResponse}
     */
    execute(args){
        throw new AbstractMethodError()
    }
}

class CommandCall{
    constructor(name, args){
        this.name = name;
        this.args = args;
    }
}

class CommandCallResponse{
    constructor(code, details){
        this.code = code;
        this.details = details;
    }

    static fromString(responseText){
        const response = JSON.parse(responseText);
        return new CommandCallResponse(response.code, response.details);
    }

    toString(){
        return JSON.stringify(this);
    }
}

class FireEventCommandCall extends CommandCall{
    constructor(event){
        super("fireEvent", { event: event });
    }
}

class FireEventExecutor extends CommandExecutor{
    constructor(inputChannel){
        super("fireEvent");
        this.inputChannel = inputChannel;
    }

    /**
     * @param {object} args
     * @returns {CommandCallResponse}
     */
    execute(args){
        try{
            this.inputChannel.handleEvent(args.event);
            return new CommandCallResponse(COMMAND_CALL_RESPONSE_OK, null);
        }catch(error){
            console.error('Error handling event',error)
            return new CommandCallResponse(COMMAND_CALL_RESPONSE_ERROR_EXECUTOR_FAILS, error)
        }
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
        throw new AbstractMethodError()
    }
}

class IOChannel{
    getChannel(){
        if(metadata.channel == undefined){
            throw new Error("WebChannel not initialized yet!!");
        }
        return metadata.channel;
    }

    getBackend(message){
        if(metadata.backend == undefined){
            throw new Error("WebChannel not initialized yet!!");
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
        const response = this.getBackend().send_to_python(message)
        return CommandCallResponse.fromString(response)
    }

    fireEvent(event){
        const commandCall = new FireEventCommandCall(event)
        const response = this.executeCommand(commandCall)
        if(response.code != COMMAND_CALL_RESPONSE_OK){
            const error = new Error('Error firing: ', response)
            console.error(error)
            throw error
        }
    }
}

class InputChannel extends IOChannel{
    executors = {}
    listeners = {}

    constructor(){
        super();
        this.addCommandExecutor(new FireEventExecutor(this))
    }

    addCommandExecutor(executor){
        if(this.executors[executor.name] != undefined){
            throw new Error(`Executor '${executor.name}' already registered`);
        }
        this.executors[executor.name] = executor
    }

    addEventListener(eventName, listener){
        let event_listeners = this.listeners[eventName]
        if(event_listeners == undefined){
            event_listeners = []
            this.listeners[eventName] = event_listeners
        }
        event_listeners.push(listener)
    }

    handleCommandCall(commandCall) {
        if(typeof commandCall === "string"){
            commandCall = JSON.parse(commandCall)
        }
        const response = this._handleCommandCall(commandCall)
        return response.toString()
    }

    _handleCommandCall(commandCall) {
        const executor = this.executors[commandCall.name]
        if(executor == undefined){
            console.warn(`Executor '${commandCall.name}' not registered`);
            return new CommandCallResponse(COMMAND_CALL_RESPONSE_ERROR_EXECUTOR_NOT_FOUND, null)
        }
        try{
            return executor.execute(commandCall.args)
        }catch(error){
            console.error(`Error occurred while executing command '${commandCall.name}':`, error)
            return new CommandCallResponse(COMMAND_CALL_RESPONSE_ERROR_EXECUTOR_FAILS, error)
        }
    }

    handleEvent(event) {
        const eventListeners = this.listeners[event.name] || []
        for(const listener of eventListeners){
            listener.onEvent(event)
        }
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
