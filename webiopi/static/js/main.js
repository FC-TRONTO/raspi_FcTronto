webiopi()
 
function reboot() {
	webiopi().callMacro("reboot", 0, callbackGetValue);
}

function start() {
	webiopi().callMacro("start", 0, callbackGetValue);
}

function stop() {
	webiopi().callMacro("stop", 0, callbackGetValue);
}

function set_motor_setting(setting) {
	webiopi().callMacro("set_motor_setting", setting, callbackGetValue);
}

function set_goal_mode(color) {
	webiopi().callMacro("set_goal_mode", color, callbackGetValue);
}

function set_shoot_algo(num) {
	webiopi().callMacro("set_shoot_algo", num, callbackGetValue);
}

function set_chase_algo(num) {
	webiopi().callMacro("set_chase_algo", num, callbackGetValue);
}

function set_shoot_speed(speed) {
	webiopi().callMacro("set_shoot_speed", speed, callbackGetValue);
}

function set_k_shoot_angle(k) {
	webiopi().callMacro("set_k_shoot_angle", k, callbackGetValue);
}

function set_chase_speed(speed) {
	webiopi().callMacro("set_chase_speed", speed, callbackGetValue);
}

function set_k_chase_angle(k) {
	webiopi().callMacro("set_k_chase_angle", k, callbackGetValue);
}

function set_go_center(speed) {
	webiopi().callMacro("set_go_center", speed, callbackGetValue);
}

function set_k_go_center(k) {
	webiopi().callMacro("set_k_go_center", k, callbackGetValue);
}
 
function callbackGetValue(macro, args, data) {
	console.log(macro);
	console.log(args);
	console.log(data);
}
