webiopi()
 
function start() {
	webiopi().callMacro("start", 0, callbackGetValue);
}

function stop() {
	webiopi().callMacro("stop", 0, callbackGetValue);
}

function set_goal_mode(color) {
	webiopi().callMacro("set_goal_mode", color, callbackGetValue);
}
 
function callbackGetValue(macro, args, data) {
	console.log(macro);
	console.log(args);
	console.log(data);
}
