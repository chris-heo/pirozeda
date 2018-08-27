/**
 * @author: Christof Rueß, http://hobbyelektronik.org
 * @license: http://creativecommons.org/licenses/by-nc-sa/3.0/
 * Feel free to share and remix this 
 * but:
 * - leave this comment in the code
 * - don't use this code for commercial purposes
 * - when you alter this code: c'mon, share it like I did!
 */

function Tab(title) {
    this.titleelem = document.createTextNode(title);
    this.selected = false;
    this.color = "#000000";
    this.tabelem = null;
    this.textelem = null;
    this.iconelem = null;
    this.icon = null;
    this.bindobj = undefined;
    this._Construct();
}

Tab.prototype = {
    _Construct : function() {
        if(this.tabelem !== null) { return; }
        this.tabelem = document.createElement("li");
        this.textelem = document.createElement("a");
        this.iconelem = document.createElement("div");
        this.iconelem.className = "img";
        
        this.SetIcon(this.icon);
        
        this.textelem.appendChild(this.iconelem);
        this.textelem.appendChild(this.titleelem);
        this.tabelem.appendChild(this.textelem);
        
        var oThis = this;
        this.tabelem.onclick = function() { oThis.Click(); };
        this.tabelem.onkeydown = function(evt) { oThis.onkeydown(evt, oThis); };
        //this.textelem.href = "javascript:;";
        //this.textelem.tabIndex = 0;
        this.tabelem.tabIndex = 0;
    },
    
    SetText : function(text) {
        this.titleelem.nodeValue = text;
    },
    
    GetText : function() {
        return this.titleelem.nodeValue;
    },
    
    SetColor : function(color) {
        this.textelem.style.color = color;
    },
    
    GetColor : function() {
        return this.textelem.style.color;
    },
    
    SetToolTip : function(tip) {
        this.tabelem.title = tip;
    },
    
    SetIcon : function(icon) {
        this.icon = icon;
        if(this.icon === null) {
            this.iconelem.style.display = "none";
        } else {
            this.iconelem.style.display = "block";
            this.iconelem.style.backgroundImage = "url("+this.icon+")";
        }
    },
    
    GetIcon : function() {
        return this.icon;
    },
    
    Select : function(value) {
        if(value === undefined) { value = true; }
        this.selected = value;
        if(value === true) {
            this.tabelem.className = "active";
            if(this.bindobj !== undefined) { this.bindobj.style.display = "block"; }
        } else {
            this.tabelem.className = "";
            if(this.bindobj !== undefined) { this.bindobj.style.display = "none"; }
        }
    },
    
    Click : function() {
        this.onclick(this);
    },
    
    onkeydown : function(obj, evt) {},
    
    onclick : function() {}
};

function TabPane(container, vertical) {
    this.container = container;
    this.tabs = [];
    this.vertical = vertical;
    this.selectedtab = 0;
    
    this.onchange = function(oldtab, newtab) {};
    
    this._Construct();
}

TabPane.prototype = {
    _Construct : function() {
        if(this.container.tagName != "UL") {
            var tmp = document.createElement("ul");
            this.container.appendChild(tmp);
            this.container = tmp;
        }
        if(this.vertical === true) {
            this.container.className = "vertabs";
        } else {
            this.container.className = "hortabs";
        }
        
        /*var links = document.getElementsByTagName("link");
        for(var x = 0; x < links.length; x++) {
            if(links[x].href.match(/\/tabs\.css$/) !== null) return;
        }
        var link = document.createElement("link");
        link.type = "text/css";
        link.rel = "stylesheet";
        link.href = "css/tabs.css";
        var head = document.getElementsByTagName("head")[0];
        head.appendChild(link);*/
    },
    
    AddTab : function(title, bindobj) {
        var oThis = this;
        var newidx = this.tabs.length;
        var newtab = new Tab(title);
        newtab.bindobj = bindobj;
        
        this.container.appendChild(newtab.tabelem);
        
        newtab.Select(newidx === 0);
        newtab.index = newidx;
        newtab.onclick = function() { oThis.TabClicked(newtab); };
        
        newtab.onkeydown = function(evt) { oThis.KeyDown(newtab, evt); };
        
        this.tabs[newidx] = newtab;
        return newtab;
    },
    
    TabClicked : function(tab) {
        this.SelectTab(tab.index);
    },
    
    KeyDown : function(tab, evt) {
        var key = (evt) ? evt.keyCode : window.event.keyCode;
        var keyhandled = true;
        switch(key) {
            case 32: //Space
            case 13: //Return
                this.SelectTab(tab.index, true);
                break;
            case 36: //Home
                this.SelectTab(0, true);
                break;
            case 40: //Down
            case 39: //Right
                this.SelectTab(this.selectedtab + 1, true);
                break;
            case 37: //Left
            case 38: //Up
                this.SelectTab(this.selectedtab - 1, true);
                break;
            case 35: //End
                this.SelectTab(this.tabs.length - 1, true);
                break;
            default:
                keyhandled = false;
        }
        //weitergabe des Keyevents an den Browser unterdrücken
        if(keyhandled === true) {
            if(window.event) { 
                window.event.cancelBubble = true; 
            } else { 
                evt.preventDefault(); 
                evt.stopPropagation();
            }
        }
    },
    
    SelectTab : function(num, setfocus) {
        if(num < 0 || num >= this.tabs.length) { return false; }
        for(var x = 0; x < this.tabs.length; x++) {
            this.tabs[x].Select(false);
        }
        this.tabs[num].Select(true);
        
        if(setfocus === true) { this.tabs[num].tabelem.focus(); }
        this.onchange(this.selectedtab, num);
        this.selectedtab = num;
    }
};