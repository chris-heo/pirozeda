function strRepeat(string, count) {
	if(count < 0) { return; }
	var retval = "";
	while(count--) { retval += string; }
	return retval;
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

function strUniqueChars(str) {
	var ret = "";
	for(var i = 0; i < str.length; i++) {
		var chr = str.charAt(i);
		if(ret.indexOf(chr) == -1) { ret += chr; }
	}
	return ret;
}