/*
    Copyright (c) 2013 
    Parillo, Marc (http://www.marcparillo.com)  
    
    Permission is hereby granted, free of charge, to any person obtaining
    a copy of this software and associated documentation files (the
    "Software"), to deal in the Software without restriction, including
    without limitation the rights to use, copy, modify, merge, publish,
    distribute, sublicense, and/or sell copies of the Software, and to
    permit persons to whom the Software is furnished to do so, subject to
    the following conditions:
    
    The above copyright notice and this permission notice shall be
    included in all copies or substantial portions of the Software.
    
    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
    EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
    MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
    NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
    LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
    OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
    WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
    
    
    feedBackBox: A small feedback box realized as jQuery Plugin.
    @author: Parillo, Marc
    @url: https://github.com/marcoder/custom-combo-box
    @version: 1.0.0
*/

(function($) {

    $.fn.customComboBox = function(options) {

        var defaults = {

            /* accepts regular expression of ALLOWABLE
             * characters that the user can enter into the combo box.
             */
            'allowed' : /[A-Za-z0-9_\/\.\:\-\s]/,

            /* accepts regular expression of ILLEGAL
             * characters that the user SHOULD NOT be
             * allowed to enter into the combo box.
             */
            'notallowed' : '//',

            /* tipText is the words that appear in the combo box
             * and tipClass is any unique style to give the
             * tipText combo box entry
             */
            'tipText' : 'Enter Custom Value',
            'tipClass' : '',

            /* position of the Enter Custom Value option.
             * it can be a number [0-9] indicating the
             * placement of the option among the list or the words
             * "first" or "last"
             */
            'index' : 'last',

            /* what words, if any, you want the combo box
             * to show as the user is entering their custom value
             */
            'prefix' : 'Your Value: ',

            /* whether or not the Enter Custom Value is initially selected
             */
            'selected' : false,

            /* callback indicating when the user has changed their
             * selection in the combo box.
             *
             * Return values:
             * 1. the combo box
             * 2. the editing status (true or false)
             * 3. value of the currently selected item
             */
            'isEditing' : function(el, status, selected) {
            },
            /* callback indicating when the user is typing text
             * into the combo box
             *
             * Return values:
             * 1. the combo box
             * 2. character that was entered
             * 3. text of the combo box entry
             */
            'onKeyDown' : function(el, character, currentText) {
            },
            /* callback indicating when the user has deleted
             * a portion of their custom entry in the combo box
             *
             * Return values:
             * 1. the combo box
             * 2. text of the combo box entry
             */
            'onDelete' : function(el, currentText) {
            }
        };

        var config = $.extend({}, defaults, options);

        var editing = false;

        var el;

        var character;

        var op = {

            /**
             * Logic for when the user clicks the Delete key
             *
             * @param {Object} el Reference to the option being edited
             *
             */
            deleteEntry : function(el) {

                var el = el.find('option:selected');

                if (el.text() == config.tipText) {
                    return false;
                }

                var text = el.text().substr(config.prefix.length).split('').slice(0, -1).join('');
                el.text(config.prefix + text);
                el.attr('value', text);

                config.onDelete.call(this, el.parent('select'), text);

                if (text.length == 0) {
                    el.text(config.tipText);
                    el.attr('value', '');
                    return false;
                }

            },

            /**
             * Logic for when the user enters any keystroke
             *
             * @param {Object} el Reference to the option being edited
             *
             */

            editEntry : function(el) {

                if ( typeof character != 'undefined' 
                        && character.match(config.allowed) 
                        && !character.match(config.notallowed)) {

                    if (el.text() == config.tipText) {
                        el.text('');
                    }

                    var text = ( typeof character != 'undefined') ? el.text().substr(config.prefix.length) + character : '';

                    el.text(config.prefix + text);

                    el.attr('value', text);

                    config.onKeyDown.call(this, el.parent('select'), character, text);

                    character = '';

                }
            },

            getIndex : function(el) {
                if (config.index == ':first') {
                    return 0;
                } else if (config.index == ':last') {
                    return el.find('option').length - 1;
                } else {
                    return config.index;
                }

            },

            getNextIndex : function(d, i, el) {

                if (d == 38) {
                    return i <= 0 ? 0 : i - 1;
                }
                if (d == 40) {
                    return i >= el.find('option').length ? el.find('option').length - 1 : i + 1;
                }

            },

            changeIndex : function(e, d, i, el) {

                var index = op.getNextIndex(d, i, el);
                var opt = $(e.currentTarget).find('option:eq(' + (index) + ')');
                opt.prop('selected', true);

            },

            isEditing : function(el) {

                editing = el.find('option:selected').hasClass('cbEdit') ? true : false;

            },

            init : function(el) {

                var option = $('<option></option>');
                option.text(config.tipText);
                option.attr('value', '');
                option.addClass('cbEdit');

                if ( typeof config.index == 'string') {

                    switch(config.index) {

                        case 'first':
                        el.find('option:first').before(option);
                        break;

                        case 'last':
                        default:
                        el.find('option:last').after(option);
                        break;

                    }
                } else if ( typeof config.index == 'number' || typeof config.index == 'object') {
                   
                    if (config.index > el.find('option').length) { 
                        if (typeof window.console == 'object') {
                            console.info("Edit Combo Box Message: "+config.index+" is out of range. Try using 'first' or 'last' instead.");
                            config.index=0;
                    }
                    }     
                
                    el.find('option:eq(' + config.index + ')').before(option);
                }

                if (config.tipClass) {
                    option.addClass(config.tipClass);
                }

                if (config.selected) {
                    el.find('option').each(function() {
                        $(this).prop('selected', false);
                    });
                    option.prop('selected', true);
                    editing = true;
                }

            }
        };

        /**
         * Iterate through each combobox to be initialized
         * and attach behavior
         *
         */

        return this.each(function() {

            var el = $(this);

            //var origBgColor = el.css('background-color') ?
            // el.css('background-color') : '#FFF';
            //config.bgColor = origBgColor;

            op.init(el);

            /**
             * Captures keystrokes in case the user uses non-character
             * keys such as delete and the up and down arrows
             * @param {Object} e jQuery event object
             * Reference: http://api.jquery.com/category/events/event-object/
             *
             */
            el.bind('keydown', function(e) {

                var charCode = (e.which) ? e.which : e.keyCode;
                var sel = $(this);
                var index = sel.find(':selected').index();

                // charCode(8) == "Delete Key"
                if (editing && charCode == 8) {
                    op.deleteEntry(sel);
                    e.preventDefault();
                }

                /*
                 * Monitoring the up and down arrows when the
                 * user is focused on the combo box.
                 * This is necessary to keep track of what the
                 * user is doing -- so we can determine if the user
                 * has elected to add their own value
                 *
                 * charCode(38) == "Up Arrow"
                 * charCode(40) == "Down Arrow"
                 */
                if (charCode == 40 || charCode == 38) {
                    op.changeIndex(e, charCode, index, el);
                    op.isEditing(el);
                }

            });

            /**
             * Captures keystrokes as user enters custom text
             * @param {Object} e jQuery event object
             * Reference: http://api.jquery.com/category/events/event-object/
             *
             */
            el.bind('keypress', function(e) {

                var sel = $(e.currentTarget).find('option.cbEdit');
                var charCode = (e.which) ? e.which : e.keyCode;
                character = String.fromCharCode(charCode);
                
                if (charCode==13) { return; }

                if (editing) {
                    sel.prop('selected', true);
                    e.preventDefault();
                    op.editEntry(sel);
                }

            });

            /**
             * Captures when user selects an item in the combobox
             * @param {Object} e jQuery event object
             * Reference: http://api.jquery.com/category/events/event-object/
             *
             * Callback isEditing returns whether or not the combobox is
             * in editing mode and the selected value
             */
            el.bind('change', function(e) {

                var el = $(e.currentTarget);
                var selected = el.find('option:selected').val();
                op.isEditing(el);
                config.isEditing.call(this, el, editing, selected);

            });

        });

    };

})(jQuery);
