// https://github.com/pimterry/loglevel
(function (root, definition) {
    "use strict";
    if (typeof define === 'function' && define.amd) {
        define(definition);
    } else if (typeof module === 'object' && module.exports) {
        module.exports = definition();
    } else {
        root.log = definition();
    }
}(this, function () {
    "use strict";

    // Slightly dubious tricks to cut down minimized file size
    var noop = function () {
    };
    var undefinedType = "undefined";
    var isIE = (typeof window !== undefinedType) && (typeof window.navigator !== undefinedType) && (
        /Trident\/|MSIE /.test(window.navigator.userAgent)
    );

    var logMethods = [
        "trace",
        "debug",
        "info",
        "warn",
        "error"
    ];

    // Cross-browser bind equivalent that works at least back to IE6
    function bindMethod(obj, methodName) {
        var method = obj[methodName];
        if (typeof method.bind === 'function') {
            return method.bind(obj);
        } else {
            try {
                return Function.prototype.bind.call(method, obj);
            } catch (e) {
                // Missing bind shim or IE8 + Modernizr, fallback to wrapping
                return function () {
                    return Function.prototype.apply.apply(method, [obj, arguments]);
                };
            }
        }
    }

    // Trace() doesn't print the message in IE, so for that case we need to wrap it
    function traceForIE() {
        if (console.log) {
            if (console.log.apply) {
                console.log.apply(console, arguments);
            } else {
                // In old IE, native console methods themselves don't have apply().
                Function.prototype.apply.apply(console.log, [console, arguments]);
            }
        }
        if (console.trace) console.trace();
    }

    // Build the best logging method possible for this env
    // Wherever possible we want to bind, not wrap, to preserve stack traces
    function realMethod(methodName) {
        if (methodName === 'debug') {
            methodName = 'log';
        }

        if (typeof console === undefinedType) {
            return false; // No method possible, for now - fixed later by enableLoggingWhenConsoleArrives
        } else if (methodName === 'trace' && isIE) {
            return traceForIE;
        } else if (console[methodName] !== undefined) {
            return bindMethod(console, methodName);
        } else if (console.log !== undefined) {
            return bindMethod(console, 'log');
        } else {
            return noop;
        }
    }

    // These private functions always need `this` to be set properly

    function replaceLoggingMethods(level, loggerName) {
        /*jshint validthis:true */
        for (var i = 0; i < logMethods.length; i++) {
            var methodName = logMethods[i];
            this[methodName] = (i < level) ?
                noop :
                this.methodFactory(methodName, level, loggerName);
        }

        // Define log.log as an alias for log.debug
        this.log = this.debug;
    }

    // In old IE versions, the console isn't present until you first open it.
    // We build realMethod() replacements here that regenerate logging methods
    function enableLoggingWhenConsoleArrives(methodName, level, loggerName) {
        return function () {
            if (typeof console !== undefinedType) {
                replaceLoggingMethods.call(this, level, loggerName);
                this[methodName].apply(this, arguments);
            }
        };
    }

    // By default, we use closely bound real methods wherever possible, and
    // otherwise we wait for a console to appear, and then try again.
    function defaultMethodFactory(methodName, level, loggerName) {
        /*jshint validthis:true */
        return realMethod(methodName) ||
            enableLoggingWhenConsoleArrives.apply(this, arguments);
    }

    function Logger(name, defaultLevel, factory) {
        var self = this;
        var currentLevel;

        var storageKey = "loglevel";
        if (typeof name === "string") {
            storageKey += ":" + name;
        } else if (typeof name === "symbol") {
            storageKey = undefined;
        }

        function persistLevelIfPossible(levelNum) {
            var levelName = (logMethods[levelNum] || 'silent').toUpperCase();

            if (typeof window === undefinedType || !storageKey) return;

            // Use localStorage if available
            try {
                window.localStorage[storageKey] = levelName;
                return;
            } catch (ignore) {
            }

            // Use session cookie as fallback
            try {
                window.document.cookie =
                    encodeURIComponent(storageKey) + "=" + levelName + ";";
            } catch (ignore) {
            }
        }

        function getPersistedLevel() {
            var storedLevel;

            if (typeof window === undefinedType || !storageKey) return;

            try {
                storedLevel = window.localStorage[storageKey];
            } catch (ignore) {
            }

            // Fallback to cookies if local storage gives us nothing
            if (typeof storedLevel === undefinedType) {
                try {
                    var cookie = window.document.cookie;
                    var location = cookie.indexOf(
                        encodeURIComponent(storageKey) + "=");
                    if (location !== -1) {
                        storedLevel = /^([^;]+)/.exec(cookie.slice(location))[1];
                    }
                } catch (ignore) {
                }
            }

            // If the stored level is not valid, treat it as if nothing was stored.
            if (self.levels[storedLevel] === undefined) {
                storedLevel = undefined;
            }

            return storedLevel;
        }

        /*
         *
         * Public logger API - see https://github.com/pimterry/loglevel for details
         *
         */

        self.name = name;

        self.levels = {
            "TRACE": 0, "DEBUG": 1, "INFO": 2, "WARN": 3,
            "ERROR": 4, "SILENT": 5
        };

        self.methodFactory = factory || defaultMethodFactory;

        self.getLevel = function () {
            return currentLevel;
        };

        self.setLevel = function (level, persist) {
            if (typeof level === "string" && self.levels[level.toUpperCase()] !== undefined) {
                level = self.levels[level.toUpperCase()];
            }
            if (typeof level === "number" && level >= 0 && level <= self.levels.SILENT) {
                currentLevel = level;
                if (persist !== false) {  // defaults to true
                    persistLevelIfPossible(level);
                }
                replaceLoggingMethods.call(self, level, name);
                if (typeof console === undefinedType && level < self.levels.SILENT) {
                    return "No console available for logging";
                }
            } else {
                throw "log.setLevel() called with invalid level: " + level;
            }
        };

        self.setDefaultLevel = function (level) {
            if (!getPersistedLevel()) {
                self.setLevel(level, false);
            }
        };

        self.enableAll = function (persist) {
            self.setLevel(self.levels.TRACE, persist);
        };

        self.disableAll = function (persist) {
            self.setLevel(self.levels.SILENT, persist);
        };

        // Initialize with the right level
        var initialLevel = getPersistedLevel();
        if (initialLevel == null) {
            initialLevel = defaultLevel == null ? "WARN" : defaultLevel;
        }
        self.setLevel(initialLevel, false);
    }

    /*
     *
     * Top-level API
     *
     */

    var defaultLogger = new Logger();

    var _loggersByName = {};
    defaultLogger.getLogger = function getLogger(name) {
        if ((typeof name !== "symbol" && typeof name !== "string") || name === "") {
            throw new TypeError("You must supply a name when creating a logger.");
        }

        var logger = _loggersByName[name];
        if (!logger) {
            logger = _loggersByName[name] = new Logger(
                name, defaultLogger.getLevel(), defaultLogger.methodFactory);
        }
        return logger;
    };

    // Grab the current global log variable in case of overwrite
    var _log = (typeof window !== undefinedType) ? window.log : undefined;
    defaultLogger.noConflict = function () {
        if (typeof window !== undefinedType &&
            window.log === defaultLogger) {
            window.log = _log;
        }

        return defaultLogger;
    };

    defaultLogger.getLoggers = function getLoggers() {
        return _loggersByName;
    };

    // ES6 default export, for compatibility
    defaultLogger['default'] = defaultLogger;

    return defaultLogger;
}));

const win = window;

if (!win) {
    throw new Error('Plugin for browser usage only');
}

let CIRCULAR_ERROR_MESSAGE;

// https://github.com/nodejs/node/blob/master/lib/util.js
function tryStringify(arg) {
    try {
        return JSON.stringify(arg);
    } catch (error) {
        // Populate the circular error message lazily
        if (!CIRCULAR_ERROR_MESSAGE) {
            try {
                const a = {};
                a.a = a;
                JSON.stringify(a);
            } catch (circular) {
                CIRCULAR_ERROR_MESSAGE = circular.message;
            }
        }
        if (error.message === CIRCULAR_ERROR_MESSAGE) {
            return '[Circular]';
        }
        throw error;
    }
}

function getConstructorName(obj) {
    if (!Object.getOwnPropertyDescriptor || !Object.getPrototypeOf) {
        return Object.prototype.toString.call(obj).slice(8, -1);
    }

    // https://github.com/nodejs/node/blob/master/lib/internal/util.js
    while (obj) {
        const descriptor = Object.getOwnPropertyDescriptor(obj, 'constructor');
        if (
            descriptor !== undefined
            && typeof descriptor.value === 'function'
            && descriptor.value.name !== ''
        ) {
            return descriptor.value.name;
        }

        obj = Object.getPrototypeOf(obj);
    }

    return '';
}

function interpolate(array) {
    let result = '';
    let index = 0;

    if (array.length > 1 && typeof array[0] === 'string') {
        result = array[0].replace(/(%?)(%([sdjo]))/g, (match, escaped, ptn, flag) => {
            if (!escaped) {
                index += 1;
                const arg = array[index];
                let a = '';
                switch (flag) {
                    case 's':
                        a += arg;
                        break;
                    case 'd':
                        a += +arg;
                        break;
                    case 'j':
                        a = tryStringify(arg);
                        break;
                    case 'o': {
                        let obj = tryStringify(arg);
                        if (obj[0] !== '{' && obj[0] !== '[') {
                            obj = `<${obj}>`;
                        }
                        a = getConstructorName(arg) + obj;
                        break;
                    }
                }
                return a;
            }
            return match;
        });

        // update escaped %% values
        result = result.replace(/%{2,2}/g, '%');

        index += 1;
    }

    // arguments remaining after formatting
    if (array.length > index) {
        if (result) result += ' ';
        result += array.slice(index).join(' ');
    }

    return result;
}

const {hasOwnProperty} = Object.prototype;

// Light deep Object.assign({}, ...sources)
function assign() {
    const target = {};
    for (let s = 0; s < arguments.length; s += 1) {
        const source = Object(arguments[s]);
        for (const key in source) {
            if (hasOwnProperty.call(source, key)) {
                target[key] = typeof source[key] === 'object' && !Array.isArray(source[key])
                    ? assign(target[key], source[key])
                    : source[key];
            }
        }
    }
    return target;
}

function getStacktrace() {
    try {
        throw new Error();
    } catch (trace) {
        return trace.stack;
    }
}

function Queue(capacity) {
    let queue = [];
    let sent = [];

    this.length = () => queue.length;
    this.sent = () => sent.length;

    this.push = (message) => {
        queue.push(message);
        if (queue.length > capacity) {
            queue.shift();
        }
    };

    this.send = () => {
        if (!sent.length) {
            sent = queue;
            queue = [];
        }
        return sent;
    };

    this.confirm = () => {
        sent = [];
        this.content = '';
    };

    this.fail = () => {
        const overflow = 1 + queue.length + sent.length - capacity;

        if (overflow > 0) {
            sent.splice(0, overflow);
            queue = sent.concat(queue);
            this.confirm();
        }
        // if (queue.length + sent.length >= capacity) this.confirm();
    };
}

const hasStacktraceSupport = !!getStacktrace();

let loglevel;
let originalFactory;
let pluginFactory;

function plain(log) {
    return `[${log.timestamp}] ${log.level.label.toUpperCase()}${
        log.logger ? ` (${log.logger})` : ''
    }: ${log.message}${log.stacktrace ? `\n${log.stacktrace}` : ''}`;
}

function json(log) {
    log.level = log.level.label;
    return log;
}

function setToken() {
    throw new Error("You can't set token for a not appled plugin");
}

const save = win.remote;

const defaultCapacity = 500;
const defs = {
    url: '/logger',
    method: 'POST',
    headers: {},
    token: '',
    onUnauthorized: () => {
    },
    timeout: 0,
    interval: 1000,
    level: 'trace',
    backoff: {
        multiplier: 2,
        jitter: 0.1,
        limit: 30000,
    },
    capacity: 0,
    stacktrace: {
        levels: ['trace', 'warn', 'error'],
        depth: 3,
        excess: 0,
    },
    timestamp: () => new Date().toISOString(),
    format: plain,
};

const remote = {
    noConflict() {
        if (win.remote === remote) {
            win.remote = save;
        }
        return remote;
    },
    plain,
    json,
    apply(logger, options) {
        if (!logger || !logger.getLogger) {
            throw new TypeError('Argument is not a root loglevel object');
        }

        if (loglevel) {
            throw new Error('You can assign a plugin only one time');
        }

        if (!win.XMLHttpRequest) return logger;

        loglevel = logger;

        const config = assign(defs, options);

        config.capacity = config.capacity || defaultCapacity;

        const {backoff} = config;

        const backoffFunc = typeof backoff === 'object'
            ? (duration) => {
                let next = duration * backoff.multiplier;
                if (next > backoff.limit) next = backoff.limit;
                next += next * backoff.jitter * Math.random();
                return next;
            }
            : backoff;

        let {interval} = config;
        let contentType;
        let isJSON;
        let isSending = false;
        let isSuspended = false;

        const queue = new Queue(config.capacity);

        function send() {
            if (isSuspended || isSending || config.token === undefined) {
                return;
            }

            if (!queue.sent()) {
                if (!queue.length()) {
                    return;
                }

                const logs = queue.send();

                queue.content = isJSON ? `{"logs":[${logs.join(',')}]}` : logs.join('\n');
            }

            isSending = true;

            const xhr = new win.XMLHttpRequest();
            xhr.open(config.method, config.url, true);
            xhr.setRequestHeader('Content-Type', contentType);
            if (config.token) {
                xhr.setRequestHeader('Authorization', `Bearer ${config.token}`);
            }

            const {headers} = config;
            for (const header in headers) {
                if (hasOwnProperty.call(headers, header)) {
                    const value = headers[header];
                    if (value) {
                        xhr.setRequestHeader(header, value);
                    }
                }
            }

            function suspend(successful) {
                if (!successful) {
                    // interval = config.backoff(interval || 1);
                    interval = backoffFunc(interval || 1);
                    queue.fail();
                }

                isSuspended = true;
                win.setTimeout(() => {
                    isSuspended = false;
                    send();
                }, interval);
            }

            let timeout;
            if (config.timeout) {
                timeout = win.setTimeout(() => {
                    isSending = false;
                    xhr.abort();
                    suspend();
                }, config.timeout);
            }

            xhr.onreadystatechange = () => {
                if (xhr.readyState !== 4) {
                    return;
                }

                isSending = false;
                win.clearTimeout(timeout);

                if (xhr.status === 200) {
                    // eslint-disable-next-line prefer-destructuring
                    interval = config.interval;
                    queue.confirm();
                    suspend(true);
                } else {
                    if (xhr.status === 401) {
                        const {token} = config;
                        config.token = undefined;
                        config.onUnauthorized(token);
                    }
                    suspend();
                }
            };

            xhr.send(queue.content);
        }

        originalFactory = logger.methodFactory;

        pluginFactory = function remoteMethodFactory(methodName, logLevel, loggerName) {
            const rawMethod = originalFactory(methodName, logLevel, loggerName);
            const needStack = hasStacktraceSupport
                && config.stacktrace.levels.some(level => level === methodName);
            const levelVal = loglevel.levels[methodName.toUpperCase()];
            const needLog = levelVal >= loglevel.levels[config.level.toUpperCase()];

            return (...args) => {
                if (needLog) {
                    const timestamp = config.timestamp();

                    let stacktrace = needStack ? getStacktrace() : '';
                    if (stacktrace) {
                        const lines = stacktrace.split('\n');
                        lines.splice(0, config.stacktrace.excess + 3);
                        const {depth} = config.stacktrace;
                        if (depth && lines.length !== depth + 1) {
                            const shrink = lines.splice(0, depth);
                            stacktrace = shrink.join('\n');
                            if (lines.length) stacktrace += `\n    and ${lines.length} more`;
                        } else {
                            stacktrace = lines.join('\n');
                        }
                    }

                    const log = config.format({
                        message: interpolate(args),
                        level: {
                            label: methodName,
                            value: levelVal,
                        },
                        logger: loggerName || '',
                        timestamp,
                        stacktrace,
                    });

                    if (isJSON === undefined) {
                        isJSON = typeof log !== 'string';
                        contentType = isJSON ? 'application/json' : 'text/plain';
                    }

                    let content = '';
                    if (isJSON) {
                        try {
                            content += JSON.stringify(log);
                        } catch (error) {
                            rawMethod(...args);
                            loglevel.getLogger('logger').error(error);
                            return;
                        }
                    } else {
                        content += log;
                    }

                    queue.push(content);
                    send();
                }

                rawMethod(...args);
            };
        };

        logger.methodFactory = pluginFactory;
        logger.setLevel(logger.getLevel());

        remote.setToken = (token) => {
            config.token = token;
            send();
        };

        return logger;
    },
    disable() {
        if (!loglevel) {
            throw new Error("You can't disable a not appled plugin");
        }

        if (pluginFactory !== loglevel.methodFactory) {
            throw new Error("You can't disable a plugin after appling another plugin");
        }

        loglevel.methodFactory = originalFactory;
        loglevel.setLevel(loglevel.getLevel());
        loglevel = undefined;
        remote.setToken = setToken;
    },
    setToken,
};

var logger = log.noConflict();
var sender = remote.noConflict();
options = {
    url: '/utils/log/',
    headers: {
        "X-CSRFToken": csrftoken
    },
    format: remote.json
}
sender.apply(logger, options);

