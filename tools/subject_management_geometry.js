/* Native synthetic-state checks; no business writes. Run once per DevTools viewport. */
const fs = require('node:fs');
const ws = new WebSocket('ws://127.0.0.1:9420');
const pending = new Map();
let sequence = 0;
const deadline = setTimeout(() => { console.error('AUTOMATION_TIMEOUT'); ws.close(); process.exitCode = 1; }, 25000);
function send(method, params) {
  return new Promise((resolve, reject) => {
    const id = String(++sequence);
    const timer = setTimeout(() => { pending.delete(id); reject(Error('timeout: ' + method)); }, 5000);
    pending.set(id, (message) => { clearTimeout(timer); message.error ? reject(Error(JSON.stringify(message.error))) : resolve(message.result); });
    ws.send(JSON.stringify({ id, method, params }));
  });
}
ws.onmessage = (event) => { const message = JSON.parse(event.data); const callback = pending.get(message.id); if (callback) { pending.delete(message.id); callback(message); } };
ws.onerror = () => { clearTimeout(deadline); console.error('CONNECTION_FAILED'); process.exitCode = 1; };
ws.onopen = async () => {
  try {
    await send('App.callWxMethod', { method: 'switchTab', args: [{ url: '/pages/settings/index' }] });
    const results = [];
    for (const state of ['list', 'panel', 'unselected', 'readonly', 'restricted', 'pending', 'error', 'long-name']) {
      await send('App.callFunction', { functionDeclaration: `function(state) {
        const p = getCurrentPages().slice(-1)[0];
        if (!p.resetSubjectManager) throw Error('Current source not compiled');
        if (!p.__subjectOriginal) { p.__subjectOriginal = JSON.parse(JSON.stringify(p.data)); p.__subjectLoad = p.load; }
        p.load = async function() {};
        const A = p.data.children.constructor, O = p.data.constructor;
        const copy = v => { if (v === null || typeof v !== 'object') return v; const result = Array.isArray(v) ? new A() : new O(); Object.keys(v).forEach(k => result[k] = copy(v[k])); return result; };
        const data = { loading: false, error: '', children: [{id:'synthetic',name:'示例',avatar:'示'}], childIndex: 0, canWrite: state !== 'readonly', childId: 'synthetic',
          showDailyTaskForm: false, showDailyTaskCatalog: false, showCatalog: false, showSchedule: false, showTravelEditor: false,
          baseLearning: [{ name: '数学', selected: true }, { name: '英语', selected: false }],
          addedLearning: [{ id: 'synthetic-subject', name: '科学', canRemove: state !== 'restricted' }],
          showSubjectManager: !['list', 'readonly', 'restricted'].includes(state),
          managedSubject: { name: state === 'long-name' ? '用于窄屏验证的中文长名称科目完整换行且不遮挡移出入口' : '数学', selected: state !== 'unselected' },
          subjectBusy: state === 'pending', subjectConfirming: false, subjectError: state === 'error' ? '操作失败，请重试' : '' };
        return new Promise(resolve => p.setData(copy(data), () => resolve(true)));
      }`, args: [state] });
      await new Promise(resolve => setTimeout(resolve, 150));
      const result = await send('App.callFunction', { functionDeclaration: `function() {
        return new Promise(resolve => {
          const p = getCurrentPages().slice(-1)[0], q = wx.createSelectorQuery().in(p);
          ['.subject-list .act-row', '.subject-list .chev', '.subject-sheet', '.subject-name', '.subject-change', '.subject-close', '.subject-manager-body'].forEach(s => q.selectAll(s).fields({rect:true,size:true}));
          q.exec(nodes => { const info = wx.getSystemInfoSync(); resolve({width:info.windowWidth,height:info.windowHeight,nodes}); });
        });
      }`, args: [] });
      const payload = { state, ...result.result, errors: [] };
      if (!payload.nodes || !payload.nodes[0].length) throw Error('native subject nodes missing');
      for (const group of payload.nodes) for (const node of group) {
        if (node.left < -1 || node.right > payload.width + 1) payload.errors.push('horizontal overflow');
      }
      for (const index of [0, 4, 5]) for (const node of payload.nodes[index]) {
        if (node.width < 44 || node.height < 44) payload.errors.push('touch target below44');
      }
      if (['readonly', 'restricted'].includes(state) && payload.nodes[1].length > (state === 'restricted' ? 2 : 0)) payload.errors.push('restricted arrows');
      if (!['list', 'readonly', 'restricted'].includes(state)) {
        if (payload.nodes[4].length !== 1) payload.errors.push('action missing');
        for (const node of payload.nodes[4]) if (node.bottom > payload.height + 1 || node.top < 0) payload.errors.push('action outside viewport');
      }
      const dir = 'docs/quality/evidence/subject-management-20261015';
      fs.mkdirSync(dir, { recursive: true });
      fs.writeFileSync(dir + '/' + state + '-' + payload.width + '.json', JSON.stringify(payload, null, 2));
      results.push({ state, width: payload.width, errors: payload.errors });
    }
    console.log(JSON.stringify(results));
    if (results.some(result => result.errors.length)) process.exitCode = 1;
  } catch (error) { console.error(error.message); process.exitCode = 1; }
  finally {
    await send('App.callFunction', { functionDeclaration: `function() { const p = getCurrentPages().slice(-1)[0]; if (p.__subjectOriginal) { p.setData(p.__subjectOriginal); p.load = p.__subjectLoad; delete p.__subjectOriginal; delete p.__subjectLoad; } return true; }`, args: [] }).catch(() => {});
    clearTimeout(deadline);
    ws.close();
  }
};
