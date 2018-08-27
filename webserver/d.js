var d = {
	d : document,
	w : window,
	b : document.body,
	// element by id
	ebi : function(i) { return document.getElementById(i); },
	// elements by name
	ebn : function(n) { return document.getElementsByName(n); },
	// first element by name
	febn : function(n) { return document.getElementsByName(n)[0]; },
	// create element
	ce : function(n, a) 
	{
		var e = document.createElement(n); 
		if(a !== undefined)
		{
			//console.log("apply attributes", a, "to", e)
			d.sa(e, a);
		}
		return e;
	},
	// create document fragment
	cdf : function() { return document.createDocumentFragment(); },
	// create text node
	ctn : function(n) { return document.createTextNode(n); },
	// append child
	ac : function(p, c) 
	{
		if(c instanceof Array)
		{
			var arr = [];
			for(var i = 0; i < c.length; i++)
			{
				arr.push(p.appendChild(c[i]));
			}
			return arr;
		}
		return p.appendChild(c); 
	},
	// append child(s) (return parent node)
	acp : function(p, c) 
	{
		if(c instanceof Array)
		{
			for(var i = 0; i < c.length; i++)
			{
				p.appendChild(c[i]);
			}
		}
		else
		{
			p.appendChild(c);
		}
		return p; 
	},
	// first child
	fc : function(e) { return e.firstChild; },
	// last child
	lc : function(e) { return e.lastChild; },
	// text content
	tc : function(e) { return e.textContent; },
	// remove all childs
	rac : function(e) { while(e.hasChildNodes()) { e.removeChild(e.lastChild);} return e },
	// concat elements & strings
	ces : function(a)
	{
		var f = document.createDocumentFragment();

		for(var i = 0; i < a.length; i++)
		{
			var e = a[i];
			if(d.iss(e))
			{
				d.ac(f, d.ctn(e))
			} 
			else if(d.isElem(e))
			{
				d.ac(f, e)
			}
		}
		return f;
	},
	// set attributes
	sa : function(o, a)
	{
		if(o instanceof Object)
		{
			for(var n in a) 
			{
				if(a[n] instanceof Object)
				{
					d.sa(o[n], a[n]);
				}
				else
				{
					o[n] = a[n]; 
				}
			}
		}	
		return o;
	},
	// create select, array of [title, value?, selected?]
	cs : function(o, a)
	{
		var s = d.ce("select", a);
		for(var i = 0; i < o.length; i++)
		{
			var e = d.ac(s, d.acp(d.ce("option"), d.ctn(o[i][0])));
			if(o[i][1] !== undefined &&  o[i][1] !== null) { e.value = o[i][1]; }
			if(o[i][2] === true) { e.selected = true; }
		}
		return s;
	},
	// element by xpath
	ebx : function(p, c) 
	{
		if(c == undefined) { c = document; }
		return document.evaluate(p, c, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue; 
	},
	// elements by xpath (multiple)
	ebxm : function(p, c)
	{
		if(c == undefined) { c = document; }
		var ret = []
		var res = document.evaluate(p, c, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
		for ( var i=0 ; i < res.snapshotLength; i++ )
		{
			ret.push(res.snapshotItem(i));
		}
		return ret;
	},
	// element offset
	eo : function(e)
	{
		var left = 0;
		var top = 0;
		var height = e.offsetHeight;
		var width = e.offsetWidth;
		if(e.offsetParent && e.style.position != "absolute") {
			do {
				left += e.offsetLeft;
				top += e.offsetTop;
				if(e.tagName == "BODY") { break; }
			} while (e = e.offsetParent);
		}
		return { "offsetLeft" : left, "offsetTop" : top, "offsetHeight" : height, "offsetWidth" : width };
	},
	// eventlistener add
	ea : function (o, e, f) 
	{
		if(o.addEventListener) 
		{
			o.addEventListener(e, f, false); 
		}
		else if(o.attachEvent) 
		{
			o.attachEvent("on" + e, f); 
		}
	},
	// eventlistener remove
	er : function (o, e, f) {
		if(o.removeEventListener) 
		{
			o.removeEventListener(e, f, false); 
		}
		else if(o.detachEvent) 
		{
			o.detachEvent("on" + e, f); 
		}
	},
	// is string
	iss : function(o)
	{
		return typeof o === "string" || o instanceof String;
	},
	// className add
	cna : function(e, c)
	{
		if(e.classList)
		{
			e.classList.add(c)
		}
		else
		{
			e.className += " " + c;
		}
	},
	// className remove
	cnr : function(e, c)
	{
		if(e.classList)
		{
			e.classList.remove(c)
		}
		else
		{
			e.className = e.className.replace(new RegExp("(?:^|\\s)" + d.res(c) + "(?!\\S)", "g"), "");
		}
	},
	// regex escape string
	res : function(s)
	{
		return s.replace(/[\-\[\]\/\{\}\(\)\*\+\?\.\\\^\$\|]/g, "\\$&");
	}

};

function Timer(interval, tick, enabled)
{
	this.interval = interval || 100;
	this.tick = tick || null
	this.repeat = true;
	this._id = null;
	if(this.enabled === true)
	{
		this.start();
	}
}

Timer.prototype = {
	start : function()
	{
		if(this._id != null)
		{
			this.stop();
		}
		var othis = this;
		this._id = window.setInterval(function() { othis._tick(); }, this.interval);
	},
	stop : function()
	{
		if(this._id !== null)
		{
			window.clearInterval(this._id);
			this._id = null;
		}
	},
	_tick : function()
	{
		if(this.repeat == false)
		{
			this.stop();
		}
		if(this.tick instanceof Function)
		{
			this.tick(this);
		}
	},
	isEnabled : function()
	{
		return this._id !== null;
	},
	setInterval : function(newInterval)
	{
		// caution: this will reset the timer
		this.interval = newInterval;
		if(this._id !== null)
		{
			this.stop();
			this.start();
		}
	},
}

// string extension
d.s = {
	// repeat string s n times
	repeat : function(s, n)
	{
		if(n < 1) { return ""; }
		return Array(n+1).join(s);
	},
	// add right padding p to string s with min l characters
	padr : function(s, l, p)
	{
		s = "" + s;
		p = p || " ";
		if(p == "") { return s; }
		var sl = s.length;
		var p = d.s.repeat(p, Math.ceil((l - sl) / p.length));
		return s + p.substr(0, l - sl);
	},
	// add left padding p to string s with min l characters
	padl : function(s, l, p)
	{
		s = "" + s;
		p = p || " ";
		if(p == "") { return s; }
		var sl = s.length;
		var p = d.s.repeat(p, Math.ceil((l - sl) / p.length));
		return p.substr(0, l - sl) + s;
	},

	// hex string to byte array
	hs2ba : function(s)
	{
		var re = /(?:0x)?([0-9a-f]{1,2})/gi;
		var a = [];
		while((m=re.exec(s))!==null)
		{
			if(m.index === re.lastIndex) re.lastIndex++;
			a.push(parseInt(m[1], 16));
		}
		return a;
	},
	// byte array to string
	ba2s : function(ba)
	{
		var r = "";
		for(var i = 0; i < ba.length; i++)
		{
			r += String.fromCharCode(ba[i]);
		}
		return r;
	},
	// string s to hex string with delimiter d and prefix p
	s2hs : function(s, de, p)
	{
		de = de || " ";
		p = p || "";
		var r = "";
		for(var i = 0; i < s.length; i++)
		{
			r += p + d.s.b2h(s.charCodeAt(i)) + de;
		}
		return r.substr(0, r.length - de.length);
	},
	// byte b to hex string
	b2h : function(b, l)
	{
		l = l || 2;
		return d.s.padl(b.toString(16).toUpperCase(), l, "0");
	}
}


/*function getCSSRule(ruleName, deleteFlag) {
	ruleName = ruleName.toLowerCase();
	var lastRule = null; var lastRuleCnt = 0;
	if(document.styleSheets) {
		for(var i=0; i<document.styleSheets.length; i++) {
			var styleSheet=document.styleSheets[i];
			var ii=0;
			var cssRule=false;
			do {
				if (styleSheet.cssRules) {
					cssRule = styleSheet.cssRules[ii];
				} else {
					cssRule = styleSheet.rules[ii];
				}
				if(cssRule) {
					if(cssRule.selectorText.toLowerCase()==ruleName) {
						if(deleteFlag===true) {
							if(styleSheet.cssRules) {
								styleSheet.deleteRule(ii);
							} else {
								styleSheet.removeRule(ii);
							}
							return true;
						} else {
							return cssRule;
						}
					}
				}
				ii++;
				if(lastRule === cssRule) { lastRuleCnt++; } else { lastRuleCnt = 0; }
				if(lastRuleCnt > 10) { return false; }
				lastRule = cssRule;
			} while (cssRule !== false);
		}
	}
	return false;
}

function killCSSRule(ruleName) {
	return getCSSRule(ruleName, true);
}

function addCSSRule(ruleName) {
	if(document.styleSheets) {
		if(!getCSSRule(ruleName)) {
			if(document.styleSheets[0].addRule) {
				document.styleSheets[0].addRule(ruleName, null,0);
			} else {
				document.styleSheets[0].insertRule(ruleName+' { }', 0);
			}
		}
	}
	return getCSSRule(ruleName);
}

function isElemVisible(obj) {
	if(obj == document) { return true; }
	
	if(!obj) { return false; }
	if(!obj.parentNode) { return false; }
	if(obj.style) {
		if(obj.style.display == 'none') { return false; }
		if(obj.style.visibility == 'hidden') { return false; }
	}

	if(window.getComputedStyle) {
		var style = window.getComputedStyle(obj, "");
		if(style.display == 'none') { return false; }
		if(style.visibility == 'hidden') { return false; }
	}
	
	style = obj.currentStyle;
	if(style) {
		if(style.display == 'none') { return false; }
		if(style.visibility == 'hidden') { return false; }
	}
	
	return isElemVisible(obj.parentNode);
}*/