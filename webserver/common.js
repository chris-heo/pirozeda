function XhrGet(url, callback, params, notimestamp)
{
    // build url with parameters
    var sep = url.indexOf("?") == -1 ? "?" : "&";
    if(params !== null && params !== undefined)
    {
        for (var key in params) 
        {
            if (params.hasOwnProperty(key)) 
            {
                const value = params[key];
                url += sep + encodeURIComponent(key) + "=" + encodeURIComponent(value);
                sep = "&";
            }
        }
    }
    // add timestamp to avoid caching
    if(notimestamp != true)
    {
        url += sep + "ts=" + (new Date()).getTime();
    }

    var req = new XMLHttpRequest();
    var othis = this;
    req.open("GET", url);
    req.addEventListener("abort", function (evt) { callback(evt, req); });
    req.addEventListener("error", function (evt) { callback(evt, req); });
    req.addEventListener("load", function (evt) { callback(evt, req); });
    req.send();
    return req;
}

function XhrGetJson(url, callback, params, notimestamp)
{
    var time = new Date();
    var cb = function(evt, req)
    {
        time = new Date() - time;
        var data = null;
        var success = false;
        if (req.status >= 200 && req.status < 300)
        {
            data = JSON.parse(req.responseText);
            success = true;
        }
        if(callback instanceof Function) callback(success, data, time)
    }
    XhrGet(url, cb, params, notimestamp);
}

function JsonHttpRequest(url, params, callback, addtimestamp)
{
    this.running = false;
    this.url = url;
    this.params = params || {};
    this.callback = callback;
    this.addtimestamp = addtimestamp || true;

    this.req = null;

    this.lastresp = {"success" : false, "reqdate" : null, "respdate" : null, "data" : null, "duration" : null };
}

JsonHttpRequest.prototype =
{
    load : function()
    {
        var url = this.url;
        if(this.running == true)
        {
            return false;
        }
        // build url with parameters
        var sep = url.indexOf("?") == -1 ? "?" : "&";
        if(this.params !== null && this.params !== undefined)
        {
            for (var key in this.params) 
            {
                if (this.params.hasOwnProperty(key)) 
                {
                    const value = this.params[key];
                    url += sep + encodeURIComponent(key) + "=" + encodeURIComponent(value);
                    sep = "&";
                }
            }
        }
        // add timestamp to avoid caching
        if(this.addtimestamp == true)
        {
            url += sep + "ts=" + (new Date()).getTime();
        }

        this.req = new XMLHttpRequest();
        var othis = this;
        this.req.open("GET", url);
        this.req.addEventListener("abort", function (evt) { othis.loaded(evt); });
        this.req.addEventListener("error", function (evt) { othis.loaded(evt); });
        this.req.addEventListener("load", function (evt) { othis.loaded(evt); });

        this.running = true;
        this.lastresp.success = null;
        this.lastresp.reqdate = new Date();
        this.lastresp.respdate = null;
        this.lastresp.data = null;
        this.lastresp.duration = null;
        
        this.req.send();

        return true;
    },
    loaded : function(evt)
    {
        this.lastresp.respdate = new Date();
        this.lastresp.duration = this.lastresp.respdate - this.lastresp.reqdate;
        if (!(this.req.status >= 200 && this.req.status < 300)) 
        {
            this.lastresp.success = false;
        }
        else
        {
            try
            {
                this.lastresp.data = JSON.parse(this.req.responseText);
                this.lastresp.success = true;
            } catch (error) { }
        }

        this.running = false;
        if(this.callback instanceof Function)
        {
            this.callback(this, this.lastresp.success, this.lastresp.data);
        }
        
    }
}

function Postscaler(counts, offset)
{
    this.counts = counts;
    this.offset = offset || 0;
    this.ticks = this.offset;
    this.ticked = false;
}

Postscaler.prototype =
{
    tick : function()
    {
        this.ticks++;
        if(this.ticks >= this.counts)
        {
            this.ticks = 0;
            this.ticked = true;
            return true;
        }
        return false;
    },
    reset : function()
    {
        this.ticks = this.offset;
    }
}

ParamTable = function(className)
{
    this.rows = [];
    this.highlight = true;
    
    this.table = d.ce("table", className ? {"className" : className } : undefined);
}

ParamTable.prototype =
{
    addRow : function(title, unit, objectgroup, objectkey, formatter, className)
    {
        return this.addRowObj(new ParamTableEntry(title, unit, objectgroup, objectkey, formatter, className));
    },
    addSep : function(title)
    {
        var row = new ParamTableSeparator(title);
        this.rows.push(row);
        d.ac(this.table, row.buildTableRow());
        return row;
    },
    addCustomRow : function(row)
    {
        d.ac(this.table, row);
    },
    addRowObj : function(row)
    {
        this.rows.push(row);
        d.ac(this.table, row.buildTableRow());
        return row;
    },
    removeRow : function(entry)
    {
        var i = this.rows.indexOf(entry);
        if (i == -1) return false;
        this.rows.splice(i, 1);
        this.table.removeChild(entry.tableRow);
        return true;
    },
    update : function(object, objectgroup)
    {
        for(var i = 0; i < this.rows.length; i++)
        {
            var row = this.rows[i];
            if(row.objectgroup == objectgroup)
            {
                var value = (row.objectkey == null) ? object : object[row.objectkey];
                row.update(value, this.highlight);
            }
        }
    }

}

ParamTableSeparator = function(title)
{
    this.title = title;
    this.tableRow = null;
}

ParamTableSeparator.prototype =
{
    buildTableRow : function()
    {
        this.tableRow = d.ce("tr", {"className" : "sep"});
        d.ac(this.tableRow, d.acp(d.ce("td", {"colSpan" : 3}), d.ctn(this.title)));
        return this.tableRow;
    },
    update : function() {},
}

ParamTableEntry = function(title, unit, objectgroup, objectkey, formatter, className)
{
    this.title = title;
    this.unit = unit;
    this.objectkey = objectkey;
    this.objectgroup = objectgroup;
    this.formatter = formatter;
    this.className = className;

    this.valtext = null;
    this.tableRow = null;
    this.cols = [];
    this.valuectn = d.ctn("-");
}

ParamTableEntry.prototype =
{
    buildTableRow : function()
    {
        this.tableRow = d.ce("tr");
        if (this.className != undefined)
        {
            this.tableRow.className = this.className;
        }

        this.cols = [d.ctn(this.title), this.valuectn];
        if(this.unit != null)
        {
            this.cols.push(d.ctn(this.unit));
        }
        for (let i = 0; i < this.cols.length; i++) 
        {
            d.ac(this.tableRow, d.acp(d.ce("td"), this.cols[i]));
        }
        if(this.unit == null)
        {
            this.valuectn.parentNode.colSpan = 2; //yeah, this pretty much sucks
        }
        return this.tableRow;
    },

    update : function(value, highlight)
    {
        var newtext = (this.formatter instanceof Function) ? this.formatter(value) : value;
        if(this.valtext != newtext)
        {
            this.valtext = newtext;
            this.valuectn.textContent = newtext;

            var td = this.valuectn.parentNode;
            //restart animation
            if(highlight == true)
            {
                d.cnr(td, "txtchani");
                void td.offsetWidth;
                d.cna(td, "txtchani");
            }
            
        }
    }
}

function SaveFile(content, filename, mimetype)
{
    var a = d.ac(d.d.body, d.ce("a", {"style" : "display: none"}));
    var blob = new Blob([content], { type: (mimetype || "octet/stream") });
    var url = window.URL.createObjectURL(blob);
    a.href = url;
    a.download = filename;
    a.click();
    window.URL.revokeObjectURL(url);
    a.remove();
}