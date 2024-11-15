/* insert custom javascript here */
odoo.define('rlm_x1.js_name', function (require) {
	'use strict';

	// assign the variable EditMenuDialog of website module's contentModule
	// js in a variable
	var EditMenuDialog = require('website.contentMenu').EditMenuDialog;

	// for modifying use the .include function
	EditMenuDialog.include({
		start: function () {
			this.$('.oe_menu_editor').nestedSortable({
				listType: 'ul',
				handle: 'div',
				items: 'li',
				maxLevels: 5, // changed maxLevels from 2 to 3
				toleranceElement: '> div',
				forcePlaceholderSize: true,
				opacity: 0.6,
				placeholder: 'oe_menu_placeholder',
				tolerance: 'pointer',
				attribute: 'data-menu-id',
				expression: '()(.+)'
			});
		}
	});
});