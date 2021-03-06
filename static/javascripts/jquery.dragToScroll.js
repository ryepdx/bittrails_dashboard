/*!
 * Based on the
 * jQuery lightweight plugin boilerplate
 * Original author: @ajpiano
 * Further changes, comments: @addyosmani
 * Licensed under the MIT license
 */


// the semi-colon before the function invocation is a safety 
// net against concatenated scripts and/or other plugins 
// that are not closed properly.
;(function ( $, window, document, undefined ) {
    
    // undefined is used here as the undefined global 
    // variable in ECMAScript 3 and is mutable (i.e. it can 
    // be changed by someone else). undefined isn't really 
    // being passed in so we can ensure that its value is 
    // truly undefined. In ES5, undefined can no longer be 
    // modified.
    
    // window and document are passed through as local 
    // variables rather than as globals, because this (slightly) 
    // quickens the resolution process and can be more 
    // efficiently minified (especially when both are 
    // regularly referenced in your plugin).

    // Create the defaults once
    var pluginName = 'dragToScroll',
        defaults = {
        };

    // The actual plugin constructor
    function Plugin( element, options ) {
        this.element = element;

        // jQuery has an extend method that merges the 
        // contents of two or more objects, storing the 
        // result in the first object. The first object 
        // is generally empty because we don't want to alter 
        // the default options for future instances of the plugin
        this.options = $.extend( {}, defaults, options) ;
        
        this._defaults = defaults;
        this._name = pluginName;
        
        this.init();
    }

    Plugin.prototype.init = function () {
        var self = this;
        var $element = $(this.element);
        self.xStart = null;
        self.left = 0;
        self.leftStart = 0;
        
        $element.mousedown(function (event) {
            self.lastX = event.clientX;
            self.down = true;
            return false;
        }).mouseup(function (event) {
            self.down = false;
        }).mousemove(function (event) {
            if (self.down) {
                $element.scrollLeft($element.scrollLeft() + (self.lastX - event.clientX));
                self.lastX = event.clientX;
            }
        }).css({
            'overflow' : 'hidden',
            'cursor' : '-moz-grab'
        });
        
        $(window).mouseout(function (event) {
            if (self.down) {
                try {
                    if (event.originalTarget.nodeName == 'BODY' || event.originalTarget.nodeName == 'HTML') {
                        self.down = false;
                    }                
                } catch (e) {}
            }
        });
    };

    // A really lightweight plugin wrapper around the constructor, 
    // preventing against multiple instantiations
    $.fn[pluginName] = function ( options ) {
        return this.each(function () {
            if (!$.data(this, 'plugin_' + pluginName)) {
                $.data(this, 'plugin_' + pluginName, 
                new Plugin( this, options ));
            }
        });
    }

})( jQuery, window, document );
