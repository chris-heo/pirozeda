
d.ea(window, "load", function()
{
    foo = new SolarManager();
});

function SolarManager()
{
    this.plot_latestdata = [];
    this.tabs = new TabPane(d.ebi("tabs"), false);
    this.lcd = new ProzedaLCDisplay(this);
    this.lcd_refresh = d.ac(d.ebi("lcd_lastupdate"), d.ctn("nie"));
    this.plot_refresh = d.ac(d.ebi("graph_lastupdate"), d.ctn("nie"));
    this.dateformat = new DateFormat("DD.MM.YYYY HH:mm:ss.fff");
    this.ptCurrLogdata = new ParamTable("currentdata");

    this.ptDebugInfo = new ParamTable("debugtable");
    
    this.psUpdatePlot = new Postscaler(5);
    this.updateplot = false;
    
    this.settings = null;
    var othis = this;

    var refreshInterval = 500;
    this.timer = new Timer(refreshInterval, function() { othis.tick(); });
    // instead of loading via XHR, the settings could be directly integrated via a script
    XhrGetJson("settings.php", function(success, data, time) { othis.settingsloaded(success, data, time); });

    this.jhrCurrdata = new JsonHttpRequest("data_current.php", null, function(obj, success, data) {othis.currentdata_loaded(success, data); }, true);
    this.jhrLastdata = new JsonHttpRequest("data_last.php",    null, function(obj, success, data) {othis.latestdata_loaded(success, data); }, true);
    this.jhrDispdata = new JsonHttpRequest("display.php",      null, function(obj, success, data) {othis.displaydata_loaded(success, data); }, true);
    this.jhrSysinfo =  new JsonHttpRequest("sysinfo.php",      null, function(obj, success, data) {othis.sysinfo_loaded(success, data); }, true);

    this.hv = new HexView(null, 16);
}

SolarManager.prototype = 
{
    settingsloaded : function(success, data, time)
    {
        if(success == false || data == null)
        {
            alert("Einstellungen konnten nicht geladen werden.");
            return;
        }
        this.settings = data;
        this.init();
    },

    prozedavalUnit : function(coltype)
    {
        switch (coltype) {
            case 0x01: return "°C";
            case 0x02: return "W";
            case 0x07: return "kWh";
            case 0x0F: return "h";
            case 0x10: return "s";
            case 0x13: 
            case 0x1B: return "l/min";
            //case 0x08: // date
            //case 0x09: // time
            //case 0xFE: return ""; // timestamp
            default: return "";
        }
    },

    prozedavalFormatter : function(coltype)
    {
        //TODO: get rid of quirks
        switch (coltype) {
            case 0x01: return [function(value) { return value.toFixed(1); }, "°C"];
            case 0x02: return [function(value) { return value.toString(); }, "W"];
            case 0x07: return [function(value) { return value.toString(); }, "kWh"];
            case 0x08: return [function(value) { return (value % 100) + "." + Math.floor(value / 100) + "."; }, ""];
            case 0x09: return [function(value) { return Math.floor(value / 60) + ":" + d.s.padl(value % 60, 2, "0"); }, ""];
            case 0x0F: return [function(value) { return value.toString(); }, "h"];
            case 0x10: return [function(value) { return value.toString(); }, "s"];
            case 0x13: return [function(value) { return value.toString(); }, "l/min"];
            case 0x1B: return [function(value) { return value.toString(); }, "l/min"];
            case 0xFE: return [function(value) { return (new Date(value * 1000)).toLocaleString(); }, ""];
            default: return [function(value) { return "0x" + value.toString(16).toUpperCase(); }, ""];
        }
    },

    init : function()
    {
        var othis = this;
        this.tabs.AddTab("Diagramm", d.ebi("tab_graph"));
        this.tabs.AddTab("3D-Diagramm", d.ebi("tab_3dgraph"));
        this.tabs.AddTab("Aktuelle Daten/Display", d.ebi("tab_display"));
        this.tabs.AddTab("Debug", d.ebi("tab_debug"));

        this.tabs.onchange = function(oldtab, newtab) { othis.tabchange(oldtab, newtab); }

        this.plot = new ProzedaPlot("graph", this);
        if(d.ebi("graphdata_hist_from").valueAsDate !== undefined)
        {
            this.plot3d = new Prozeda3dPlot("graph3d", this);
        }
        

        this.jhrCurrdata.load();
        this.jhrLastdata.load();

        var othis = this;
        this.ptCurrLogdata.addRow("Empfangen", null, null, 0, function(value) {
            return othis.dateformat.Format(new Date(value*1000)); 
        });
        // some manual adjustments to get a slightly better look
        for(var i = 0; i < this.settings.system.length; i++)
        {
            var row = this.settings.system[i];
            var meh = this.prozedavalFormatter(row[0]);
            this.ptCurrLogdata.addRow(row[2], meh[1], null, i+1, meh[0], row[3] == true ? "hidden" : undefined);
        }

        d.ac(d.ebi("currdata_list"), this.ptCurrLogdata.table);

        this.hvLcddata_target = d.ac(d.ebi("lcddata_raw"), d.ctn());
        this.hvCurrdata_target = d.ac(d.ebi("currdata_raw"), d.ctn());
        
        // debug tab
        var pdi = this.ptDebugInfo;
        pdi.addSep("RAM");
        pdi.addRow("Garbage Collector", "KiB", 0, null, function(obj) { return Math.round(obj.thisram / 1024)});
        pdi.addRow("Log-Kapazität", "Einträge", 0, null, function(obj) { return obj.ramlog.size; });
        pdi.addRow("Log-Belegung", "Einträge", 0, null, function(obj) { return obj.ramlog.items; });
        
        pdi.addSep("Prozeda-Reader");
        pdi.addRow("Stats seit", null, 0, null, function(obj) { return othis.dateformat.Format(new Date(obj.reader.resettime * 1000)); });
        pdi.addRow("Log", "Nachrichten", 0, null, function(obj) { return obj.reader.logdata; });
        pdi.addRow("Display", "Nachrichten", 0, null, function(obj) { return obj.reader.displaydata; });
        pdi.addRow("Rx-Fehler", "", 0, null, function(obj) { return obj.reader.rxerror; });
        pdi.addRow("HW-Resets", "", 0, null, function(obj) { return obj.reader.reset; });
        pdi.addRow("Fehlende Daten", "", 0, null, function(obj) { return obj.reader.datamissing; });

        pdi.addSep("Laufzeit HTTP-Requests");
        pdi.addRow("Aktuelle Daten", "ms", 1, null, function(obj) {return othis.jhrCurrdata.lastresp.duration; })
        pdi.addRow("Display-Daten", "ms", 2, null, function(obj) {return othis.jhrDispdata.lastresp.duration; })
        pdi.addRow("Letzte Daten", "ms", 3, null, function(obj) {return othis.jhrLastdata.lastresp.duration; })
        pdi.addRow("Statistik", "ms", 0, null, function(obj) {return othis.jhrSysinfo.lastresp.duration; })

        pdi.addSep("UART-Trace");
        // add rows for trace control
        var tr = d.acp(d.ce("tr"), d.acp(d.ce("td"), d.ctn("Aufzeichnung")));
        var td = d.ac(tr, d.ce("td", {"colSpan" : 2}));
        var tracetimes = [["10 s", 10], ["20 s", 20], ["30 s", 30], ["1 min", 60, true], ["2 min", 120], ["5 min", 300], ["10 min", 600], ["30 min", 1800]];
        var durationcs = d.ac(td, d.cs(tracetimes, {"style" : {"textAlign" : "right"}}));

        var startbtn = d.ac(td, d.ce("input", {"type" : "button", "value" : "Start"}));
        startbtn.onclick = function()
        {
            var duration = durationcs.options[durationcs.selectedIndex].value;
            XhrGetJson("filetrace.php", null, {"action" : "start", "duration" : duration})
        }
        var stopbtn = d.ac(td, d.ce("input", {"type" : "button", "value" : "Stopp"}));
        stopbtn.onclick = function()
        {
            XhrGetJson("filetrace.php", null, {"action" : "stop"})
        }
        pdi.addCustomRow(tr);

        pdi.addRow("Datei", null, 0, null, function(obj) { return obj.tracing.file; });
        pdi.addRow("Start", null, 0, null, function(obj) { return obj.tracing.start == null ? "-" : othis.dateformat.Format(new Date(obj.tracing.start * 1000)); });
        pdi.addRow("Ende", null, 0, null, function(obj) { return obj.tracing.stop == null ? "-" : othis.dateformat.Format(new Date(obj.tracing.stop * 1000)); });
        pdi.addRow("Restlaufzeit", "s", 0, null, function(obj) { return Math.round(obj.tracing.remaining); });
        pdi.addRow("Dateigröße", "KiB", 0, null, function(obj) { return Math.round(obj.tracing.size/1024); });
        
        
        tr = d.ce("tr");
        var chkShowRawdata = d.ce("input", {"type" : "checkbox"});
        d.ac(tr, d.acp(d.ce("td", {"colSpan" : 3}), d.acp(d.ce("label"), [chkShowRawdata, d.ctn("Rohdaten anzeigen")])));
        chkShowRawdata.onclick = function()
        {
            othis.chkShowRawdata_click(this);
        }
        pdi.addCustomRow(tr);
        
        d.ac(d.ebi("tab_debug"), pdi.table);
        
        this.timer.start();
    },

    chkShowRawdata_click : function(sender)
    {
        if(sender.checked == true)
        {
            this.jhrCurrdata.params["raw"] = "true";
            this.jhrDispdata.params["raw"] = "true";
        }
        else
        {
            delete this.jhrCurrdata.params["raw"]
            delete this.jhrDispdata.params["raw"]
        }
    },

    currentdata_loaded : function(success, data)
    {
        if(success == false || data == null) return;
        if(this.tabs.selectedtab == 1)
        {
            //only update the table when it's shown
            this.ptCurrLogdata.update(data.data);
        }
        if(this.jhrLastdata.running == false && this.psUpdatePlot.ticked == true)
        {
            //only update the diagram when the "base data" are already loaded
            //and only every x seconds
            this.psUpdatePlot.ticked = false;
            this.plot.updateCurrent(data.data);
            this.plot_refresh.textContent = this.dateformat.Format(new Date());
        }
        this.ptDebugInfo.update(null, 1);

        this.hvCurrdata_target.textContent = (data.raw != undefined) ? this.hv.renderAscii(d.s.ba2s(d.s.hs2ba(data.raw))) : "";
    },

    latestdata_loaded : function(success, data, time)
    {
        if(success == false || data == null) return;
        this.plot.initCurrent(data.data);
        this.plot_refresh.textContent = this.dateformat.Format(new Date());
        this.ptDebugInfo.update(null, 3);
    },


    displaydata_loaded : function(success, data, time)
    {
        if(success == false || data == null) return;
        this.lcd_refresh.textContent = this.dateformat.Format(new Date());
        this.lcd.update(data);
        this.ptDebugInfo.update(null, 2);

        this.hvLcddata_target.textContent = (data.raw != undefined) ? this.hv.renderAscii(d.s.ba2s(d.s.hs2ba(data.raw))) : "";
    },

    sysinfo_loaded : function(success, data, time)
    {
        this.ptDebugInfo.update(data, 0);

    },

    tick : function()
    {
        this.psUpdatePlot.tick();
        this.jhrCurrdata.load();
        if(this.tabs.selectedtab == 1)
        {
            // current data & display is selected
            this.jhrDispdata.load();
        }
        else if(this.tabs.selectedtab == 2)
        {
            this.jhrSysinfo.load();
        }
    },

    tabchange : function(oldtab, newtab)
    {
        if(newtab == 1)
        {
            this.jhrDispdata.load();
        }
        else if(newtab == 2)
        {
            this.jhrSysinfo.load();
        }
    },

    datemagic_init(from, to, days)
    {
        if(from.valueAsDate === undefined)
        {
            return false;
        }
        days = days || 10;
        var tmp = new Date();
        tmp.setHours(0,0,0,0);
        to.valueAsDate = tmp;
        tmp.setDate(tmp.getDate() - days);
        from.valueAsDate = tmp;
        return true;
    },
    datemagic_fixdayrange(from, to, unixts, complain)
    {
        unixts = unixts || false;
        complain = complain || false;

        if(from.valueAsDate === undefined)
        {
            if(complain == true)
            {
                alert("Dieser Browser unterstützt keine Datepicker. Bitte einen modernen Browser verwenden.")
            }
            return false;
        }
        if(from.valueAsDate === null || to.valueAsDate === null)
        {
            if(complain == true)
            {
                alert("Kein Datumspaar gesetzt");
            }
            return false;
        }
        //swap dates if from > to
        if(from.valueAsDate > to.valueAsDate)
        {
            var tmp = from.valueAsDate;
            from.valueAsDate = to.valueAsDate;
            to.valueAsDate = tmp;
        }

        var f = from.valueAsDate;
        var t = to.valueAsDate;
        // get the full days
        f.setHours(0, 0, 0, 0);
        t.setHours(23, 59, 59, 999);
        if(unixts)
        {
            f = Math.round(f.getTime() / 1000);
            t = Math.round(t.getTime() / 1000);
        }
        return {"from": f, "to": t};
    }
}

function ProzedaPlot(containerId, manager)
{
    this.currentData = { "x" : [], "y" : [] }; // current (latest and updated) data
    this.historyData = { "x" : [], "y" : [] }; // historic data
    this.columnDefs = [];

    this.plotdata = []; // plotdata that are being displayed

    this.currentDisplay = 0; // 0: current data, 1: historic data

    this.containerId = containerId;
    this.solarmanager = manager;

    this.f_datefrom = d.ebi("graphdata_hist_from");
    this.f_dateto = d.ebi("graphdata_hist_to");

    // initialize date pickers
    this.solarmanager.datemagic_init(this.f_datefrom, this.f_dateto, 10);

    this.initPlot();
}

ProzedaPlot.prototype =
{
    initPlot : function()
    {
        //prepare plotly
        /*var selectorOptions = {
            buttons: [
                { step: 'month', stepmode: 'backward', count: 1, label: '1 Monat'},
                { step: 'month', stepmode: 'backward', count: 6, label: '6 Monate'},
                { step: 'year', stepmode: 'todate', count: 1, label: 'Jahr'},
                { step: 'year', stepmode: 'backward', count: 1, label: '1 Jahr'},
                { step: 'all', label: 'Alles' },
            ]
        };*/

        var layout = {
            xaxis: {
                /*rangeselector: buttons: [
                    { step: 'month', stepmode: 'backward', count: 1, label: '1 Monat'},
                    { step: 'month', stepmode: 'backward', count: 6, label: '6 Monate'},
                    { step: 'year', stepmode: 'todate', count: 1, label: 'Jahr'},
                    { step: 'year', stepmode: 'backward', count: 1, label: '1 Jahr'},
                    { step: 'all', label: 'Alles' },
                ],*/
                rangeslider: {}
            },
            yaxis1: {
                title: "Leistung [%]",
                fixedrange: true,
                domain: [0, 0.45]
            },
            yaxis2: {
                title: "Temperatur [°C]",
                fixedrange: true,
                domain: [0.55, 1]
            },
        };

        //clear plotdata
        this.plotdata.length = 0;
        // prepare data series
        var columns = this.solarmanager.settings.system;
        
        for (var i = 0; i < columns.length; i++) {
            var col = columns[i];
            var coltype = col[0];
            var colhidden = col[3] || false;
            var colname = col[2];
            if (coltype == 1 && colhidden == false) 
            {
                // non-hidden temperature-column
                // __colid must be offset by 1 because data contains the timestamp as first item
                var series = { "name": colname, "mode": "lines", "line": { "width": 1 }, "x": [], "y": [], "xaxis": 'x', "yaxis": "y2", "__colid": (i + 1) };
                this.plotdata.push(series);
            }
            else if (coltype == 10 && colhidden == false) 
            {
                // non-hidden output-column
                var series = { "name": colname, "mode": "lines", "line" : {"width": 1 }, "x": [], "y": [], "xaxis": 'x', "yaxis": "y1", "__colid": (i + 1) };
                this.plotdata.push(series);
            }
        }

        var othis = this;
        d.ebi("graphdata_current").checked = true;
        d.ea(d.ebi("graphdata_current"), "click", function() { othis.updatePlot(0, true); });
        d.ea(d.ebi("graphdata_history"), "click", function() { othis.updatePlot(1, true); });
        d.ea(d.ebi("graphdata_hist_load"), "click", function() { d.ebi("graphdata_history").click(); othis.loadHistorydata(); });

        

        Plotly.plot(this.containerId, this.plotdata, layout, { scrollZoom: true });
    },

    initCurrent : function(data)
    {
        // first set of data contains historic rows
        if(this.solarmanager.settings.system.length == 0)
        {
            return false;
        }

        for (var i = 0; i < data.length; i++) 
        {
            var row = data[i];
            this.currentData.x.push(new Date(row[0] * 1000));
            for (var j = 0; j < this.plotdata.length; j++) 
            {
                // holy f... this is quite messed up
                var target = this.currentData.y[j];
                if(target === undefined)
                {
                    this.currentData.y.push([]);
                }
                this.currentData.y[j].push(row[this.plotdata[j].__colid]);
            }
        }
        
        this.updatePlot(0);
    },

    updateCurrent : function(row)
    {

        this.currentData.x.push(new Date(row[0] * 1000));
        for (var j = 0; j < this.plotdata.length; j++) 
        {
            this.currentData.y[j].push(row[this.plotdata[j].__colid]);
        }
        
        this.updatePlot(0);
    },

    setHistoric : function(data)
    {
        this.historyData = { "x" : [], "y" : [] };
        
        for(var i = 0; i < data.length; i++)
        {
            var row = data[i];
            this.historyData.x.push(new Date(row[0] * 1000));
            for (var j = 0; j < this.plotdata.length; j++) 
            {
                if(this.historyData.y[j] == undefined)
                {
                    this.historyData.y.push([]);
                }
                this.historyData.y[j].push(row[this.plotdata[j].__colid]);
            }
        }
        this.updatePlot(1);
    },

    loadHistorydata : function()
    {
        var daterange = this.solarmanager.datemagic_fixdayrange(this.f_datefrom, this.f_dateto, true, true);
        if(daterange == false)
        {
            return;
        }

        var othis = this;
        XhrGetJson("fslog.php", function(success, data, time) 
        {
            if(success == false)
            {
                alert("Fehler beim Laden der Daten");
            }
            othis.setHistoric(data);

        }, {"action" : "chart", "datefrom" : daterange.from, "dateto" : daterange.to })
    },

    updatePlot : function(plottype, changePlottype)
    {
        if(changePlottype == true)
        {
            this.currentDisplay = plottype;
        }
        else if(plottype != this.currentDisplay)
        {
            return;
        }

        var ref = null;

        if(this.currentDisplay == 0)
            ref = this.currentData;
        else
            ref = this.historyData;

        for(var i = 0; i < this.plotdata.length; i++)
        {
            this.plotdata[i].x = ref.x;
            this.plotdata[i].y = ref.y[i];
        }
        Plotly.redraw(this.containerId);
    }
}

function Prozeda3dPlot(containerId, manager)
{
    this.containerId = containerId;
    this.solarmanager = manager;

    this.colorscale = [
        [ "0", "rgb(0,0,255)"],
        [ "0.2", "rgb(107,215,255)"], 
        [ "0.4", "rgb(20,209,0)"], 
        [ "0.6", "rgb(255,225,0)"], 
        [ "0.8", "rgb(255,0,0)"], 
        [ "1", "rgb(255,0,255)"]
    ];
    this.map = { type: "surface", z: [], y: [], x: [], scene: "scene", colorscale: this.colorscale };
    this.layout = {
        title: "",
        autosize: true,
        width: 900,
        height: 600,
        scene : {
            camera : {
                center : { z: -0.25 },
                eye : { x: 1.8, y: 0.8, z: 0.85 }
            },
            aspectratio: { x: 1, y: 2, z: 1 },
            xaxis: { title: '', tickformat: '%H:%M' },
            yaxis: { title: '', tickformat: '%e.%m.%Y' },
            zaxis: { title: '' }
        }
    };

    // build list of columns
    var colsel = d.ebi("graphdata3d_column");
    
    for(var i = 0; i < this.solarmanager.settings.system.length; i++)
    {
        var col = this.solarmanager.settings.system[i];
        var unit = this.solarmanager.prozedavalUnit(col[0]); 
        //only output columns that are not hidden and have a unit (exclude i.e. date/time)
        if((col.length < 4 || (col.length >= 4 && col[3] == false)) && unit != "")
        {
            var txt = col[2] + " [" + unit + "]"
            var e = d.ac(colsel, d.acp(d.ce("option"), d.ctn(txt)));
            e.value = i;
        }
    }
    var othis = this;
    d.ea(d.ebi("graphdata3d_load"), "click", function() { othis.loadData(); });

    this.virgin = true;

    this.f_datefrom = d.ebi("graphdata3d_hist_from");
    this.f_dateto = d.ebi("graphdata3d_hist_to");
    this.f_column = d.ebi("graphdata3d_column");

    // initialize date pickers
    this.solarmanager.datemagic_init(this.f_datefrom, this.f_dateto, 10);

    this.initPlot();
}

Prozeda3dPlot.prototype = 
{
    initPlot : function()
    {
        // nothing
    },

    loadData : function()
    {
        var daterange = this.solarmanager.datemagic_fixdayrange(this.f_datefrom, this.f_dateto, true, true);
        if(daterange == false)
        {
            return;
        }

        var column = d.ebi("graphdata3d_column").value;

        var othis = this;
        XhrGetJson("fslog_cond.php", function(success, data, time) 
        {
            if(success == false)
            {
                alert("Fehler beim Laden der Daten");
            }
            othis.updatePlot(data);
        }, {"action" : "chart", "datefrom" : daterange.from, "dateto" : daterange.to, "col" : column });
    },

    updatePlot : function(data)
    {
        // clear diagram
        this.map.x.length = 0;
        this.map.y.length = 0;
        this.map.z.length = 0;

        // this is highly dependent on the data shown.
        // it's important to set these variables to have a consistent
        // assignment of the colorscale to the values
        this.map.cmin = -20;
        this.map.cmax = 120;

        for(var i = 0; i < data.length; i++)
        {
            var daydata = data[i];
            this.map.z.push(daydata.data);
            this.map.y.push(new Date(daydata.basetime * 1000));
        }

        // scale the y-axis for better viewing
        // an aspect ratio of 1 per 30 days looks quite good (sorry for the magic number)
        // however the value shouldn't go below 1 to keep dates readable
        if(this.map.y.length > 0)
        {
            var my = this.map.y;
            var yar = (my[my.length - 1].getTime() - my[0].getTime()) / 1000 / 86400 / 30;
            yar = Math.max(Math.ceil(yar * 2) / 2, 1);
            this.layout.scene.aspectratio.y = yar;
        }
        
        // fill x axis (time of day). assumint that the length of the data array represents
        // a whole day these values have to be distributed throughout a period of 24 hours
        var epd = data[0].data.length;
        for(var i = 0; i < epd; i++)
        {
            this.map.x.push(new Date(i / epd * 24 * 3600 * 1000));
        }

        if(this.virgin == true)
        {
            Plotly.newPlot(this.containerId, [this.map], this.layout);
            this.virgin = false;
        }
        else
        {
            Plotly.redraw(this.containerId);
        }
    }
}

function ProzedaLCDisplay(manager)
{
    this.manager = manager;
    this.swelems = [];
    var sw_prefix = "lcd_status_sw"
    var el = d.ebi(sw_prefix);
    this.setElementActive(el, false);
    this.swelems.push(el);
    for(let i = 0; i < 8; i++)
    {
        el = d.ebi(sw_prefix + (i+1));
        this.setElementActive(el, false);
        this.swelems.push(el);
    }

    var symbols = ["lcd_menu_info", "lcd_menu_settings", "lcd_menu_manual", "lcd_menu_specialfunc", "lcd_status_error", "lcd_status_confirmok"];
    for (i = 0; i < symbols.length; i++) 
    {
        var s = symbols[i];
        this.setElementActive(d.ebi(s), false);
    }

    this.pumpelems = [];
    var foo = ["lcd_pump_in", "lcd_pump_dn", "lcd_pump_up"];
    for(i = 0; i < foo.length; i++)
    {
        var s = foo[i];
        var el = d.ebi(s);
        this.setElementActive(el, false);
        this.pumpelems.push(el);
    }

    this.textelems = [];
    this.textelems.push(d.ac(d.ebi("lcd_text0"), d.ctn()));
    this.textelems.push(d.ac(d.ebi("lcd_text1"), d.ctn()));
    this.textelems.push(d.ac(d.ebi("lcd_text2"), d.ctn()));
}

ProzedaLCDisplay.prototype = 
{
    setElementActive : function(element, active)
    {
        element.style.opacity = (active == true) ? 1 : 0.2;
    },

    setPumpStatus : function(status)
    {
        // 0: off, 1: down, 2: up
        this.setElementActive(this.pumpelems[0], status != 0);
        this.setElementActive(this.pumpelems[1], status == 1);
        this.setElementActive(this.pumpelems[2], status == 2);
    },

    update : function(data)
    {
        // I'm not quite happy about this...
        var foo = ["menu_info", "menu_settings", "menu_manual", "menu_specialfunc", "status_error", "status_confirmok"];
        for (var i = 0; i < foo.length; i++) 
        {
            var item = foo[i];
            this.setElementActive(d.ebi("lcd_" + item), data[item]);
        }
        
        // not worth a 'for'
        this.textelems[0].textContent = data.text[0];
        this.textelems[1].textContent = data.text[1];
        this.textelems[2].textContent = data.text[2];

        this.setPumpStatus(data.status_pump);
        for (let i = 0; i < 9; i++) 
        {
            this.setElementActive(this.swelems[i], data.status_outputs.indexOf(i) != -1);
        }
    }
}