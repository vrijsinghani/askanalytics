/*
WebSockets Extension
============================
This extension adds support for WebSockets to htmx.
*/

(function () {

	/** @type {import("../htmx").HtmxInternalApi} */
	var api;

	htmx.defineExtension("ws", {

		/**
		 * init is called once, when this extension is first registered.
		 * @param {import("../htmx").HtmxInternalApi} apiRef
		 */
		init: function (apiRef) {

			// Store reference to internal API
			api = apiRef;

			// Default function for creating new EventSource objects
			if (!htmx.createWebSocket) {
				htmx.createWebSocket = createWebSocket;
			}

			// Default setting for reconnect delay
			if (!htmx.config.wsReconnectDelay) {
				htmx.config.wsReconnectDelay = "full-jitter";
			}
		},

		/**
		 * onEvent handles all events passed to this extension.
		 *
		 * @param {string} name
		 * @param {Event} evt
		 */
		onEvent: function (name, evt) {

			switch (name) {

				// Try to close the socket when elements are removed
				case "htmx:beforeCleanupElement":

					var internalData = api.getInternalData(evt.target)

					if (internalData.webSocket) {
						internalData.webSocket.close();
					}
					return;

				// Try to create websockets when elements are processed
				case "htmx:beforeProcessNode":
					var parent = evt.target;

					forEach(queryAttributeOnThisOrChildren(parent, "ws-connect"), function (child) {
						ensureWebSocket(child)
					});
					forEach(queryAttributeOnThisOrChildren(parent, "ws-send"), function (child) {
						ensureWebSocketSend(child)
					});
			}
		}
	});

	/**
	 * ensureWebSocket creates a new WebSocket on the element, using the element's "ws-connect" attribute.
	 * @param {HTMLElement} socketElt
	 * @returns {void}
	 */
	function ensureWebSocket(socketElt) {
		// If the socket already exists, don't create it again
		if (api.getInternalData(socketElt).webSocket) {
			return;
		}

		// Get the WebSocket URL from the ws-connect attribute
		var wssSource = api.getAttributeValue(socketElt, "ws-connect");
		if (wssSource.length === 0) {
			return;
		}

		// Create a new WebSocket and store it in the element's internal data
		var webSocket = htmx.createWebSocket(wssSource);

		// Create a wrapper for the WebSocket that we can use to send messages
		var socketWrapper = createSocketWrapper(socketElt, webSocket);
		api.getInternalData(socketElt).webSocket = socketWrapper;
	}

	/**
	 * ensureWebSocketSend adds event listeners to the element that will send messages to the WebSocket.
	 * @param {HTMLElement} socketElt
	 * @returns {void}
	 */
	function ensureWebSocketSend(sendElt) {
		// Get the WebSocket element ID from the ws-send attribute
		var socketId = api.getAttributeValue(sendElt, "ws-send");
		if (socketId.length === 0) {
			return;
		}

		// Find the WebSocket element
		var socketElt = document.getElementById(socketId);
		if (!socketElt) {
			api.triggerErrorEvent(sendElt, "htmx:wsConfigError", {error: "Socket element not found: " + socketId});
			return;
		}

		// Get the WebSocket wrapper from the element's internal data
		var socketWrapper = api.getInternalData(socketElt).webSocket;
		if (!socketWrapper) {
			api.triggerErrorEvent(sendElt, "htmx:wsConfigError", {error: "No WebSocket found for element: " + socketId});
			return;
		}

		// Add the event listener to the element
		api.getTriggerSpecs(sendElt).forEach(function (spec) {
			api.addTriggerHandler(sendElt, spec, function (elt, evt) {
				// Get the message to send from the element's value or innerHTML
				var headers = api.getHeaders(sendElt, api.getTarget(sendElt));
				var results = api.getInputValues(sendElt, 'post');
				var errors = results.errors;
				var rawParameters = results.values;
				var expressionVars = api.getExpressionVars(sendElt);
				var allParameters = api.mergeObjects(rawParameters, expressionVars);
				var filteredParameters = api.filterValues(allParameters, sendElt);

				var sendConfig = {
					parameters: filteredParameters,
					unfilteredParameters: allParameters,
					headers: headers,
					errors: errors,
					triggeringEvent: evt,
					messageBody: getMessageBody(sendElt)
				};

				if (!api.triggerEvent(sendElt, 'htmx:wsSendBeforeRequest', sendConfig)) {
					return;
				}

				socketWrapper.send(sendConfig.messageBody || filteredParameters);

				if (api.triggerEvent(sendElt, 'htmx:wsSendAfterRequest', sendConfig)) {
					// Maybe do something
				}
			});
		});
	}

	/**
	 * createSocketWrapper creates a wrapper for the WebSocket that we can use to send messages.
	 * @param {HTMLElement} socketElt
	 * @param {WebSocket} webSocket
	 * @returns {Object}
	 */
	function createSocketWrapper(socketElt, webSocket) {
		var wrapper = {
			socket: webSocket,
			socketElt: socketElt,
			messageQueue: [],
			sendImmediately: function (message) {
				webSocket.send(message);
			},
			send: function (message) {
				if (webSocket.readyState !== WebSocket.OPEN) {
					wrapper.messageQueue.push(message);
				} else {
					wrapper.sendImmediately(message);
				}
			},
			handleQueuedMessages: function () {
				while (wrapper.messageQueue.length > 0) {
					var message = wrapper.messageQueue.shift();
					wrapper.sendImmediately(message);
				}
			},
			close: function () {
				webSocket.close();
			},
			// The publicInterface is the object that will be passed to the event handlers
			publicInterface: {
				send: function (message) {
					wrapper.send(message);
				},
				close: function () {
					wrapper.close();
				}
			}
		};

		// Set up the event handlers
		webSocket.onopen = function (evt) {
			wrapper.handleQueuedMessages();
			api.triggerEvent(socketElt, "htmx:wsOpen", {
				event: evt,
				socketWrapper: wrapper.publicInterface
			});
		};

		webSocket.onclose = function (evt) {
			// If the socket is still in the element's internal data, trigger the event
			if (api.getInternalData(socketElt).webSocket) {
				api.triggerEvent(socketElt, "htmx:wsClose", {
					event: evt,
					socketWrapper: wrapper.publicInterface
				});
			}

			// If the socket is closed abnormally, try to reconnect
			if (!evt.wasClean) {
				var delay = getWebSocketReconnectDelay(socketElt);
				setTimeout(function () {
					ensureWebSocket(socketElt);
				}, delay);
			}
		};

		webSocket.onerror = function (evt) {
			api.triggerErrorEvent(socketElt, "htmx:wsError", {
				error: evt,
				socketWrapper: wrapper.publicInterface
			});
		};

		webSocket.onmessage = function (event) {
			if (maybeCloseWebSocketSource(socketElt)) {
				return;
			}

			var response = event.data;
			if (!api.triggerEvent(socketElt, "htmx:wsBeforeMessage", {
				message: response,
				socketWrapper: wrapper.publicInterface
			})) {
				return;
			}

			api.withExtensions(socketElt, function (extension) {
				response = extension.transformResponse(response, null, socketElt);
			});

			var settleInfo = api.makeSettleInfo(socketElt);
			var fragment = api.makeFragment(response);

			if (fragment.children.length) {
				var children = Array.from(fragment.children);
				for (var i = 0; i < children.length; i++) {
					api.oobSwap(api.getAttributeValue(children[i], "hx-swap-oob") || "true", children[i], settleInfo);
				}
			}

			api.settleImmediately(settleInfo.tasks);
			api.triggerEvent(socketElt, "htmx:wsAfterMessage", {
				message: response,
				socketWrapper: wrapper.publicInterface
			});
		};

		return wrapper;
	}

	/**
	 * maybeCloseWebSocketSource checks if the socket should be closed based on the "hx-preserve" attribute.
	 * @param {HTMLElement} socketElt
	 * @returns {boolean}
	 */
	function maybeCloseWebSocketSource(socketElt) {
		if (!api.getInternalData(socketElt).webSocket) {
			return true;
		}
		if (socketElt.getAttribute('hx-preserve') === "true") {
			return false;
		}
		return document.body.contains(socketElt) === false;
	}

	/**
	 * getWebSocketReconnectDelay returns the delay before reconnecting the WebSocket.
	 * @param {HTMLElement} socketElt
	 * @returns {number}
	 */
	function getWebSocketReconnectDelay(socketElt) {
		var delay = api.getAttributeValue(socketElt, "ws-reconnect-delay") || htmx.config.wsReconnectDelay;
		if (delay === "full-jitter") {
			var retryCount = api.getInternalData(socketElt).retryCount || 0;
			api.getInternalData(socketElt).retryCount = retryCount + 1;
			var cappedRetryCount = Math.min(retryCount, 6);
			var maxValue = Math.pow(2, cappedRetryCount) * 1000;
			delay = Math.floor(Math.random() * maxValue);
		}
		return delay;
	}

	/**
	 * createWebSocket creates a new WebSocket.
	 * @param {string} url
	 * @returns {WebSocket}
	 */
	function createWebSocket(url) {
		return new WebSocket(url);
	}

	/**
	 * queryAttributeOnThisOrChildren returns all elements that have the given attribute, including the parent.
	 * @param {HTMLElement} elt
	 * @param {string} attributeName
	 * @returns {Array}
	 */
	function queryAttributeOnThisOrChildren(elt, attributeName) {
		var result = [];
		// If the parent element has the attribute, add it to the results
		if (api.hasAttribute(elt, attributeName)) {
			result.push(elt);
		}
		// Get all children with the attribute
		var children = elt.querySelectorAll("[" + attributeName + "]");
		for (var i = 0; i < children.length; i++) {
			result.push(children[i]);
		}
		return result;
	}

	/**
	 * forEach executes a function for each element in an array.
	 * @param {Array} arr
	 * @param {Function} func
	 */
	function forEach(arr, func) {
		for (var i = 0; i < arr.length; i++) {
			func(arr[i]);
		}
	}

	/**
	 * getMessageBody returns the message body from the element.
	 * @param {HTMLElement} elt
	 * @returns {string}
	 */
	function getMessageBody(elt) {
		return elt.getAttribute("ws-message-body") || elt.getAttribute("message-body");
	}

})();
