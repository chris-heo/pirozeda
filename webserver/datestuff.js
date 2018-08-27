function strRepeat(str, count)
{
	return Array(count+1).join(str);
}

function strPad(input, padLength, padString, padType) {
	input = String(input);
	if(input.length >= padLength) { return input; }
	var paddingLen = padLength - input.length;
	var padding = strRepeat(padString, Math.ceil(paddingLen / padString.length));
	padding = padding.substr(0, padLength);
	switch(padType) {
		case "LEFT": case "PAD_LEFT": case "STR_PAD_LEFT":
			return padding + input;
		case "BOTH": case "PAD_BOTH": case "STR_PAD_BOTH":
			padding = padding.substr(0, Math.ceil(paddingLen / 2));
			input = padding + input + padding;
			return input.substr(0, padLength);
		default:
			return input + padding;
	}
}

function DateFormat(dateFormat) {
	this.dateFormat = (dateFormat === undefined) ? "YYYY-MM-DD HH:mm:ss" : dateFormat;
	
	this.dayNames = {
		"sh" : ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"],
		"ln" : ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
	};

	this.monthNames = {
		"sh" : ["Jan", "Feb", "Mär", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Aug", "Nov", "Dez"],
		"ln" : ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "August", "November", "Dezember"]
	};
}

DateFormat.prototype = {
	Format : function(date) {
		//TODO Fehlerbehandlung
		if(!(date instanceof Date)) { return ""; }
		var year = "" + date.getFullYear();
		var month = date.getMonth();
		var weekday = (date.getDay()+6) % 7;
		var day = date.getDate();
		var hour = date.getHours();
		var minute = date.getMinutes();
		var second = date.getSeconds();
		
		var tokens = {
			"YYYY" : year, 
			"YY" : year.substr(2,2), 
			"MMMM" : this.monthNames.ln[month], 
			"MMM" : this.monthNames.sh[month],
			"MM" : strPad((month + 1), 2, "0", "LEFT"),
			"M" : month + 1,
			"DDDD" : this.dayNames.ln[weekday],
			"DDD" : this.dayNames.sh[weekday],
			"DD" : strPad(day, 2, "0", "LEFT"),
			"D" : day,
			"HH" : strPad(hour, 2, "0", "LEFT"),
			"H" : hour,
			"hh" : strPad((hour % 12 || 12), 2, "0", "LEFT"),
			"h" : (hour % 12 || 12),
			"t": hour < 12 ? "a"  : "p",
			"tt": hour < 12 ? "am" : "pm",
			"T": hour < 12 ? "A"  : "P",
			"TT": hour < 12 ? "AM" : "PM",
			"mm" : strPad(minute, 2, "0", "LEFT"),
			"m" : minute,
			"ss" : strPad(second, 2, "0", "LEFT"),
			"s" : second,
			"fff" : strPad(date.getMilliseconds(), 3, "0", "LEFT"),
		};
		var retval = this.dateFormat.replace(/([\\]?[YMDHhmsTtf]{1,4}|\\ )/g, function(token) { 
			if(token.charAt(0) == "\\") {
				if(token.charAt(1) == " ") { return ""; }
				return token.substr(1);
			}
			return (token in tokens) ? tokens[token] : "?"+token+"?"; }
		);
		return retval;
	}
};

function ParseDate(str) {
	var r1 = null, r, y, m, d, h, i, s;
	r = str.match(/^(\d{1,2})([.,])(\d{1,2})\2(\d{1,4})(?:[ ,](\d{1,2})([:,])(\d{1,2})(?:\6(\d{1,2}))?)?$/); 
	if(r !== null) { y = r[4]; m = r[3]; d = r[1]; r1 = r; h = r[5]; i = r[7]; s = r[8]; }
	r = str.match(/^(\d{1,4})-(\d{1,2})-(\d{1,2})(?:[ ,](\d{1,2})([:,])(\d{1,2})(?:\5(\d{1,2}))?)?$/);
	if(r !== null) { y = r[1]; m = r[2]; d = r[3]; r1 = r; h = r[4]; i = r[6]; s = r[7]; }
	r = str.match(/^(\d{1,4})\/(\d{1,2})\/(\d{1,2})(?:[ ,](\d{1,2})([:,])(\d{1,2})(?:\5(\d{1,2}))?)?$/);
	if(r !== null) { y = r[2]; m = r[1]; d = r[3]; r1 = r; h = r[4]; i = r[6]; s = r[7]; }
	if(r1 === null) { return false; }
	y = parseFloat(y,10); m = parseFloat(m,10); d = parseFloat(d,10); if(y < 100) { y = ((y > 50) ? 1900 : 2000) + y; }
	h = parseFloat(h,10); if(isNaN(h)) { h = 0; } i = parseFloat(i,10); if(isNaN(i)) { i = 0; } s = parseFloat(s,10); if(isNaN(s)) { s = 0; }
	return new Date(y, m-1, d, h, i, s);
}