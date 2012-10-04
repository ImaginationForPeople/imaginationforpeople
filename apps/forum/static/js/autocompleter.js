var AutoCompleter = function(a) {
	var b = {
		autocompleteMultiple : true,
		multipleSeparator : " ",
		inputClass : "acInput",
		loadingClass : "acLoading",
		resultsClass : "acResults",
		selectClass : "acSelect",
		queryParamName : "q",
		limitParamName : "limit",
		extraParams : {},
		lineSeparator : "\n",
		cellSeparator : "|",
		minChars : 2,
		maxItemsToShow : 10,
		delay : 400,
		useCache : true,
		maxCacheLength : 10,
		matchSubset : true,
		matchCase : false,
		matchInside : true,
		mustMatch : false,
		preloadData : false,
		selectFirst : false,
		stopCharRegex : /\s+/,
		selectOnly : false,
		formatItem : null,
		onItemSelect : false,
		autoFill : false,
		filterResults : true,
		sortResults : true,
		sortFunction : false,
		onNoMatch : false
	};
	this.options = $.extend({}, b, a);
	this.cacheData_ = {};
	this.cacheLength_ = 0;
	this.selectClass_ = "jquery-autocomplete-selected-item";
	this.keyTimeout_ = null;
	this.lastKeyPressed_ = null;
	this.lastProcessedValue_ = null;
	this.lastSelectedValue_ = null;
	this.active_ = false;
	this.finishOnBlur_ = true;
	this.options.minChars = parseInt(this.options.minChars, 10);
	if (isNaN(this.options.minChars) || this.options.minChars < 1) {
		this.options.minChars = 2
	}
	this.options.maxItemsToShow = parseInt(this.options.maxItemsToShow, 10);
	if (isNaN(this.options.maxItemsToShow) || this.options.maxItemsToShow < 1) {
		this.options.maxItemsToShow = 10
	}
	this.options.maxCacheLength = parseInt(this.options.maxCacheLength, 10);
	if (isNaN(this.options.maxCacheLength) || this.options.maxCacheLength < 1) {
		this.options.maxCacheLength = 10
	}
	if (this.options.preloadData === true) {
		this.fetchRemoteData("", function() {
		})
	}
};
inherits(AutoCompleter, WrappedElement);
AutoCompleter.prototype.decorate = function(a) {
	this._element = a;
	this._element.attr("autocomplete", "off");
	this._results = $("<div></div>").hide();
	if (this.options.resultsClass) {
		this._results.addClass(this.options.resultsClass)
	}
	this._results.css({
		position : "absolute"
	});
	$("body").append(this._results);
	this.setEventHandlers()
};
AutoCompleter.prototype.setEventHandlers = function() {
	var a = this;
	a._element.keydown(function(b) {
		a.lastKeyPressed_ = b.keyCode;
		switch (a.lastKeyPressed_) {
		case 38:
			b.preventDefault();
			if (a.active_) {
				a.focusPrev()
			} else {
				a.activate()
			}
			return false;
			break;
		case 40:
			b.preventDefault();
			if (a.active_) {
				a.focusNext()
			} else {
				a.activate()
			}
			return false;
			break;
		case 9:
		case 13:
			if (a.active_) {
				b.preventDefault();
				a.selectCurrent();
				return false
			}
			break;
		case 27:
			if (a.active_) {
				b.preventDefault();
				a.finish();
				return false
			}
			break;
		default:
			a.activate()
		}
	});
	a._element.blur(function() {
		if (a.finishOnBlur_) {
			setTimeout(function() {
				a.finish()
			}, 200)
		}
	})
};
AutoCompleter.prototype.position = function() {
	var a = this._element.offset();
	this._results.css({
		top : a.top + this._element.outerHeight(),
		left : a.left
	})
};
AutoCompleter.prototype.cacheRead = function(d) {
	var f, c, b, a, e;
	if (this.options.useCache) {
		d = String(d);
		f = d.length;
		if (this.options.matchSubset) {
			c = 1
		} else {
			c = f
		}
		while (c <= f) {
			if (this.options.matchInside) {
				a = f - c
			} else {
				a = 0
			}
			e = 0;
			while (e <= a) {
				b = d.substr(0, c);
				if (this.cacheData_[b] !== undefined) {
					return this.cacheData_[b]
				}
				e++
			}
			c++
		}
	}
	return false
};
AutoCompleter.prototype.cacheWrite = function(a, b) {
	if (this.options.useCache) {
		if (this.cacheLength_ >= this.options.maxCacheLength) {
			this.cacheFlush()
		}
		a = String(a);
		if (this.cacheData_[a] !== undefined) {
			this.cacheLength_++
		}
		return this.cacheData_[a] = b
	}
	return false
};
AutoCompleter.prototype.cacheFlush = function() {
	this.cacheData_ = {};
	this.cacheLength_ = 0
};
AutoCompleter.prototype.callHook = function(c, b) {
	var a = this.options[c];
	if (a && $.isFunction(a)) {
		return a(b, this)
	}
	return false
};
AutoCompleter.prototype.activate = function() {
	var b = this;
	var a = function() {
		b.activateNow()
	};
	var c = parseInt(this.options.delay, 10);
	if (isNaN(c) || c <= 0) {
		c = 250
	}
	if (this.keyTimeout_) {
		clearTimeout(this.keyTimeout_)
	}
	this.keyTimeout_ = setTimeout(a, c)
};
AutoCompleter.prototype.activateNow = function() {
	var a = this.getValue();
	if (a !== this.lastProcessedValue_ && a !== this.lastSelectedValue_) {
		if (a.length >= this.options.minChars) {
			this.active_ = true;
			this.lastProcessedValue_ = a;
			this.fetchData(a)
		}
	}
};
AutoCompleter.prototype.fetchData = function(b) {
	if (this.options.data) {
		this.filterAndShowResults(this.options.data, b)
	} else {
		var a = this;
		this.fetchRemoteData(b, function(c) {
			a.filterAndShowResults(c, b)
		})
	}
};
AutoCompleter.prototype.fetchRemoteData = function(c, e) {
	var d = this.cacheRead(c);
	if (d) {
		e(d)
	} else {
		var a = this;
		if (this._element) {
			this._element.addClass(this.options.loadingClass)
		}
		var b = function(g) {
			var f = false;
			if (g !== false) {
				f = a.parseRemoteData(g);
				a.options.data = f;
				a.cacheWrite(c, f)
			}
			if (a._element) {
				a._element.removeClass(a.options.loadingClass)
			}
			e(f)
		};
		$.ajax({
			url : this.makeUrl(c),
			success : b,
			error : function() {
				b(false)
			}
		})
	}
};
AutoCompleter.prototype.setOption = function(a, b) {
	this.options[a] = b
};
AutoCompleter.prototype.setExtraParam = function(b, c) {
	var a = $.trim(String(b));
	if (a) {
		if (!this.options.extraParams) {
			this.options.extraParams = {}
		}
		if (this.options.extraParams[a] !== c) {
			this.options.extraParams[a] = c;
			this.cacheFlush()
		}
	}
};
AutoCompleter.prototype.makeUrl = function(e) {
	var a = this;
	var b = this.options.url;
	var d = $.extend({}, this.options.extraParams);
	if (this.options.queryParamName === false) {
		b += encodeURIComponent(e)
	} else {
		d[this.options.queryParamName] = e
	}
	if (this.options.limitParamName && this.options.maxItemsToShow) {
		d[this.options.limitParamName] = this.options.maxItemsToShow
	}
	var c = [];
	$.each(d, function(f, g) {
		c.push(a.makeUrlParam(f, g))
	});
	if (c.length) {
		b += b.indexOf("?") == -1 ? "?" : "&";
		b += c.join("&")
	}
	return b
};
AutoCompleter.prototype.makeUrlParam = function(a, b) {
	return String(a) + "=" + encodeURIComponent(b)
};
AutoCompleter.prototype.splitText = function(a) {
	return String(a).replace(/(\r\n|\r|\n)/g, "\n").split(
			this.options.lineSeparator)
};
AutoCompleter.prototype.parseRemoteData = function(c) {
	var h, b, f, d, g;
	var e = [];
	var b = this.splitText(c);
	for (f = 0; f < b.length; f++) {
		var a = b[f].split(this.options.cellSeparator);
		g = [];
		for (d = 0; d < a.length; d++) {
			g.push(unescape(a[d]))
		}
		h = g.shift();
		e.push({
			value : unescape(h),
			data : g
		})
	}
	return e
};
AutoCompleter.prototype.filterAndShowResults = function(a, b) {
	this.showResults(this.filterResults(a, b), b)
};
AutoCompleter.prototype.filterResults = function(d, b) {
	var f = [];
	var l, c, e, m, j, a;
	var k, h, g;
	for (e = 0; e < d.length; e++) {
		m = d[e];
		j = typeof m;
		if (j === "string") {
			l = m;
			c = {}
		} else {
			if ($.isArray(m)) {
				l = m[0];
				c = m.slice(1)
			} else {
				if (j === "object") {
					l = m.value;
					c = m.data
				}
			}
		}
		l = String(l);
		if (l > "") {
			if (typeof c !== "object") {
				c = {}
			}
			if (this.options.filterResults) {
				h = String(b);
				g = String(l);
				if (!this.options.matchCase) {
					h = h.toLowerCase();
					g = g.toLowerCase()
				}
				a = g.indexOf(h);
				if (this.options.matchInside) {
					a = a > -1
				} else {
					a = a === 0
				}
			} else {
				a = true
			}
			if (a) {
				f.push({
					value : l,
					data : c
				})
			}
		}
	}
	if (this.options.sortResults) {
		f = this.sortResults(f, b)
	}
	if (this.options.maxItemsToShow > 0
			&& this.options.maxItemsToShow < f.length) {
		f.length = this.options.maxItemsToShow
	}
	return f
};
AutoCompleter.prototype.sortResults = function(c, d) {
	var b = this;
	var a = this.options.sortFunction;
	if (!$.isFunction(a)) {
		a = function(g, e, h) {
			return b.sortValueAlpha(g, e, h)
		}
	}
	c.sort(function(f, e) {
		return a(f, e, d)
	});
	return c
};
AutoCompleter.prototype.sortValueAlpha = function(d, c, e) {
	d = String(d.value);
	c = String(c.value);
	if (!this.options.matchCase) {
		d = d.toLowerCase();
		c = c.toLowerCase()
	}
	if (d > c) {
		return 1
	}
	if (d < c) {
		return -1
	}
	return 0
};
AutoCompleter.prototype.showResults = function(e, b) {
	var k = this;
	var g = $("<ul></ul>");
	var f, l, j, a, h = false, d = false;
	var c = e.length;
	for (f = 0; f < c; f++) {
		l = e[f];
		j = $("<li>" + this.showResult(l.value, l.data) + "</li>");
		j.data("value", l.value);
		j.data("data", l.data);
		j.click(function() {
			var i = $(this);
			k.selectItem(i)
		}).mousedown(function() {
			k.finishOnBlur_ = false
		}).mouseup(function() {
			k.finishOnBlur_ = true
		});
		g.append(j);
		if (h === false) {
			h = String(l.value);
			d = j;
			j.addClass(this.options.firstItemClass)
		}
		if (f == c - 1) {
			j.addClass(this.options.lastItemClass)
		}
	}
	this.position();
	this._results.html(g).show();
	a = this._results.outerWidth() - this._results.width();
	this._results.width(this._element.outerWidth() - a);
	$("li", this._results).hover(function() {
		k.focusItem(this)
	}, function() {
	});
	if (this.autoFill(h, b)) {
		this.focusItem(d)
	}
};
AutoCompleter.prototype.showResult = function(b, a) {
	if ($.isFunction(this.options.showResult)) {
		return this.options.showResult(b, a)
	} else {
		return b
	}
};
AutoCompleter.prototype.autoFill = function(e, c) {
	var b, a, d, f;
	if (this.options.autoFill && this.lastKeyPressed_ != 8) {
		b = String(e).toLowerCase();
		a = String(c).toLowerCase();
		d = e.length;
		f = c.length;
		if (b.substr(0, f) === a) {
			this._element.val(e);
			this.selectRange(f, d);
			return true
		}
	}
	return false
};
AutoCompleter.prototype.focusNext = function() {
	this.focusMove(+1)
};
AutoCompleter.prototype.focusPrev = function() {
	this.focusMove(-1)
};
AutoCompleter.prototype.focusMove = function(a) {
	var b, c = $("li", this._results);
	a = parseInt(a, 10);
	for ( var b = 0; b < c.length; b++) {
		if ($(c[b]).hasClass(this.selectClass_)) {
			this.focusItem(b + a);
			return
		}
	}
	this.focusItem(0)
};
AutoCompleter.prototype.focusItem = function(b) {
	var a, c = $("li", this._results);
	if (c.length) {
		c.removeClass(this.selectClass_).removeClass(this.options.selectClass);
		if (typeof b === "number") {
			b = parseInt(b, 10);
			if (b < 0) {
				b = 0
			} else {
				if (b >= c.length) {
					b = c.length - 1
				}
			}
			a = $(c[b])
		} else {
			a = $(b)
		}
		if (a) {
			a.addClass(this.selectClass_).addClass(this.options.selectClass)
		}
	}
};
AutoCompleter.prototype.selectCurrent = function() {
	var a = $("li." + this.selectClass_, this._results);
	if (a.length == 1) {
		this.selectItem(a)
	} else {
		this.finish()
	}
};
AutoCompleter.prototype.selectItem = function(d) {
	var c = d.data("value");
	var b = d.data("data");
	var a = this.displayValue(c, b);
	this.lastProcessedValue_ = a;
	this.lastSelectedValue_ = a;
	this.setValue(a);
	this.setCaret(a.length);
	this.callHook("onItemSelect", {
		value : c,
		data : b
	});
	this.finish()
};
AutoCompleter.prototype.isContentChar = function(a) {
	if (a.match(this.options.stopCharRegex)) {
		return false
	} else {
		if (a === this.options.multipleSeparator) {
			return false
		} else {
			return true
		}
	}
};
AutoCompleter.prototype.getValue = function() {
	var c = this._element.getSelection();
	var d = this._element.val();
	var f = c.start;
	var e = f;
	for (cpos = f; cpos >= 0; cpos = cpos - 1) {
		if (cpos === d.length) {
			continue
		}
		var b = d.charAt(cpos);
		if (!this.isContentChar(b)) {
			break
		}
		e = cpos
	}
	var a = f;
	for (cpos = f; cpos < d.length; cpos = cpos + 1) {
		if (cpos === 0) {
			continue
		}
		var b = d.charAt(cpos);
		if (!this.isContentChar(b)) {
			break
		}
		a = cpos
	}
	this._selection_start = e;
	this._selection_end = a;
	return d.substring(e, a)
};
AutoCompleter.prototype.setValue = function(b) {
	var a = this._element.val().substring(0, this._selection_start);
	var c = this._element.val().substring(this._selection_end + 1);
	this._element.val(a + b + c)
};
AutoCompleter.prototype.displayValue = function(b, a) {
	if ($.isFunction(this.options.displayValue)) {
		return this.options.displayValue(b, a)
	} else {
		return b
	}
};
AutoCompleter.prototype.finish = function() {
	if (this.keyTimeout_) {
		clearTimeout(this.keyTimeout_)
	}
	if (this._element.val() !== this.lastSelectedValue_) {
		if (this.options.mustMatch) {
			this._element.val("")
		}
		this.callHook("onNoMatch")
	}
	this._results.hide();
	this.lastKeyPressed_ = null;
	this.lastProcessedValue_ = null;
	if (this.active_) {
		this.callHook("onFinish")
	}
	this.active_ = false
};
AutoCompleter.prototype.selectRange = function(d, a) {
	var c = this._element.get(0);
	if (c.setSelectionRange) {
		c.focus();
		c.setSelectionRange(d, a)
	} else {
		if (this.createTextRange) {
			var b = this.createTextRange();
			b.collapse(true);
			b.moveEnd("character", a);
			b.moveStart("character", d);
			b.select()
		}
	}
};
AutoCompleter.prototype.setCaret = function(a) {
	this.selectRange(a, a)
};
