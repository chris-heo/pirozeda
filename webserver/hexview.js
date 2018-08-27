function HexView(container, width)
{
    this.container = container;
    this.width = width || 16;
    this.data = "";
    this.addresswidth = 3;

    this._scar = "␀␁␂␃␄␅␆␇␈␉␊␋␌␍␎␏␐␑␒␓␔␕␖␗␘␙␚␛␜␝␞␟";
    this.möp = "................................ !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~.€.‚ƒ„…†‡ˆ‰Š‹Œ.Ž..‘’“”•–—˜™š›œ.žŸ ¡¢£¤¥¦§¨©ª«¬.®¯°±²³´µ¶·¸¹º»¼½¾¿ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖ×ØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþÿ";
}

HexView.prototype =
{
    renderAscii : function(data)
    {
        result = "";
        // first line
        // padding for offset
        result += d.s.repeat(" ", this.addresswidth * 2 + 1);
        for(var i = 0; i < this.width; i++)
        {
            result += d.s.b2h(i) + " ";
        }
        result += "\n";

        // now, let's get to the meat
        var offset = 0;
        for(var y = 0; y < Math.ceil(data.length / this.width); y++)
        {
            
            var part = data.substr(offset, this.width);
            result += d.s.b2h(offset, this.addresswidth*2) + // base address
                " " + d.s.padr(d.s.s2hs(part), this.width * 3) +
                this.printableString(part) + "\n";
            offset += this.width;
        }
        return result;
    },

    fixedhex : function(num, len)
    {
        //num must be int
        len = len || 1;
        return d.s.padl(num.toString(16).toUpperCase(), len*2, "0")
    },
    printableString : function(s)
    {
        var result = "";
        for(var i = 0; i < s.length; i++)
        {
            var c = s.charCodeAt(i);
            result += this.möp[c];
        }
        return result;
    },
    _printableString : function(s)
    {
        var result = "";
        // strings in javascript are immutable, yuck.
        for(var i = 0; i < s.length; i++)
        {
            var c = s.charCodeAt(i);
            /*if(c < 0x20)
            {
                // control characters
                result += this._scar[c];
            }
            else if(c == 0x7F)
            {
                result += "␡";
            }
            else*/ if(c >= 0x20 && c <= 0xFF)
            {
                // printable latin characters
                result += s[i];
            }
            else 
            {
                // all other characters, shouldn't be possible
                result += ".";
            }
        }
        return result;
    }
}