'use strict';
'require view';
'require fs';
'require ui';

return view.extend({
	render: function() {
		var btn = E('button', { 'class': 'btn cbi-button cbi-button-apply' }, _('Free memory'));
		btn.addEventListener('click', function() {
			return fs.exec('/usr/libexec/ramfree').then(function() {
				ui.addNotification(null, E('p', _('Memory cache has been dropped.')));
			});
		});
		return E('div', { 'class': 'cbi-map' }, [
			E('h2', _('Free Memory')),
			E('div', { 'class': 'cbi-map-descr' }, _('Drop Linux filesystem caches.')),
			E('div', { 'class': 'cbi-section' }, [btn])
		]);
	}
});
