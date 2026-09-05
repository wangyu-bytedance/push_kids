const tabs = [
  { pagePath: '/pages/today/index', text: '今日', icon: 'today' },
  { pagePath: '/pages/calendar/index', text: '日程', icon: 'calendar' },
  { pagePath: '/pages/records/index', text: '记录', icon: 'records' },
  { pagePath: '/pages/reports/index', text: '报表', icon: 'reports' },
  { pagePath: '/pages/settings/index', text: '设置', icon: 'settings' },
];

Component({
  data: { selected: 0, tabs },
  lifetimes: { attached() { this.syncSelected(); } },
  pageLifetimes: { show() { this.syncSelected(); } },
  methods: {
    syncSelected() {
      const pages = getCurrentPages();
      const current = pages[pages.length - 1];
      const route = `/${current ? current.route : ''}`;
      const selected = tabs.findIndex((item) => item.pagePath === route);
      if (selected >= 0 && selected !== this.data.selected) this.setData({ selected });
    },
    switchTab(event) {
      const selected = Number(event.currentTarget.dataset.index);
      const item = tabs[selected];
      if (!item || selected === this.data.selected) return;
      this.setData({ selected });
      wx.switchTab({ url: item.pagePath });
    },
  },
});
