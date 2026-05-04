'use strict';
'require view';
'require form';

return view.extend({
	render: function() {
		var m, s, o;
		m = new form.Map('zerotier', _('ZeroTier'), _('Configure ZeroTier networks.'));
		s = m.section(form.TypedSection, 'zerotier', _('Global'));
		s.anonymous = true;
		o = s.option(form.Flag, 'enabled', _('Enable'));
		o.default = '0';
		s = m.section(form.TypedSection, 'network', _('Networks'));
		s.addremove = true;
		s.anonymous = false;
		o = s.option(form.Value, 'id', _('Network ID'));
		o.datatype = 'and(hexstring,rangelength(16,16))';
		o = s.option(form.Flag, 'allow_managed', _('Allow managed routes'));
		o = s.option(form.Flag, 'allow_global', _('Allow global routes'));
		o = s.option(form.Flag, 'allow_default', _('Allow default route'));
		return m.render();
	}
});
