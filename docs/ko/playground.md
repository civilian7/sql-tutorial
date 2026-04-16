# SQL 플레이그라운드

브라우저에서 직접 SQL을 실행할 수 있습니다. 서버 연결이 필요 없습니다.

!!! info "사용 데이터"
    튜토리얼 데이터베이스의 축소 버전(테이블당 ~200행)을 사용합니다.
    전체 데이터(75만 건)로 실습하려면 [데이터베이스 생성](setup/03-generate.md)을 참고하세요.

<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.18/codemirror.min.css">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.18/theme/material-darker.min.css">

<style>
#playground { font-family: var(--md-text-font-family, sans-serif); }

/* Table list (collapsible) */
.pg-tables { border: 1px solid var(--md-default-fg-color--lightest, #ddd); border-radius: 4px 4px 0 0; }
.pg-tables summary {
  padding: 6px 12px; cursor: pointer; font-size: 0.8rem; font-weight: 600;
  color: var(--md-default-fg-color--light, #666);
  background: var(--md-code-bg-color, #f5f5f5); user-select: none;
}
.pg-tables summary:hover { color: var(--md-accent-fg-color, #5c6bc0); }
.pg-tables-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 2px; padding: 6px; background: var(--md-code-bg-color, #f5f5f5);
}
.pg-table-chip {
  padding: 3px 8px; font-size: 0.73rem;
  font-family: var(--md-code-font-family, monospace);
  color: var(--md-default-fg-color, #333);
  cursor: pointer; border-radius: 3px;
}
.pg-table-chip:hover {
  background: var(--md-accent-fg-color--transparent, rgba(92,107,192,0.1));
  color: var(--md-accent-fg-color, #5c6bc0);
}
.pg-table-chip .pg-chip-rows {
  font-size: 0.65rem; color: var(--md-default-fg-color--lighter, #aaa); margin-left: 4px;
}

/* Toolbar */
.pg-toolbar {
  display: flex; gap: 8px; align-items: center;
  padding: 6px 8px;
  border: 1px solid var(--md-default-fg-color--lightest, #ddd); border-top: none;
  background: var(--md-code-bg-color, #f5f5f5);
}
.pg-btn {
  padding: 5px 14px; border: none; border-radius: 3px;
  font-size: 0.82rem; font-weight: 600; cursor: pointer;
}
.pg-btn-run { background: var(--md-accent-fg-color, #5c6bc0); color: #fff; }
.pg-btn-run:hover { opacity: 0.85; }
.pg-btn-reset { background: var(--md-default-fg-color--lightest, #ddd); color: var(--md-default-fg-color, #333); }
.pg-btn-reset:hover { opacity: 0.7; }
.pg-shortcut { font-size: 0.72rem; color: var(--md-default-fg-color--light, #999); }

/* Editor */
#pg-editor-wrap { border: 1px solid var(--md-default-fg-color--lightest, #ddd); border-top: none; }
#pg-editor-wrap .CodeMirror {
  height: 200px; font-size: 0.88rem;
}
#pg-editor-wrap .CodeMirror-vscrollbar { display: block !important; }
#pg-editor-wrap .CodeMirror-scroll { overflow-y: scroll !important; }

/* Result */
.pg-result {
  border: 1px solid var(--md-default-fg-color--lightest, #ddd); border-top: none;
  border-radius: 0 0 4px 4px;
  min-height: 60px; max-height: 400px; overflow-y: auto;
}
.pg-result-table-wrap { overflow-x: auto; }
.pg-result-table {
  width: 100%; border-collapse: collapse;
  font-size: 0.82rem; font-family: var(--md-code-font-family, monospace);
  white-space: nowrap;
}
.pg-result-table th {
  background: var(--md-primary-fg-color, #37474f); color: #fff;
  padding: 6px 12px; text-align: left; font-weight: 600;
  position: sticky; top: 0;
}
.pg-result-table td {
  padding: 5px 12px;
  border-bottom: 1px solid var(--md-default-fg-color--lightest, #eee);
}
.pg-result-table tr:hover td {
  background: var(--md-accent-fg-color--transparent, rgba(92,107,192,0.05));
}
.pg-result-table .null-val { color: var(--md-default-fg-color--lighter, #aaa); font-style: italic; }
.pg-status { font-size: 0.78rem; color: var(--md-default-fg-color--light, #666); padding: 8px 12px; }
.pg-error {
  background: #fdecea; color: #b71c1c; border: 1px solid #f5c6cb;
  padding: 10px 14px; font-size: 0.85rem;
  font-family: var(--md-code-font-family, monospace);
}
[data-md-color-scheme="slate"] .pg-error { background: #4e1a1a; color: #ffcdd2; border-color: #6e2a2a; }
.pg-loading { display: flex; align-items: center; gap: 12px; padding: 24px; color: var(--md-default-fg-color--light, #666); }
.pg-spinner {
  width: 24px; height: 24px;
  border: 3px solid var(--md-default-fg-color--lightest, #ddd);
  border-top-color: var(--md-accent-fg-color, #5c6bc0);
  border-radius: 50%; animation: pg-spin 0.8s linear infinite;
}
@keyframes pg-spin { to { transform: rotate(360deg); } }
</style>

<div id="playground">
  <div class="pg-loading" id="pg-loading">
    <div class="pg-spinner"></div>
    <span>데이터베이스를 불러오는 중...</span>
  </div>

  <div id="pg-app" style="display:none;">
    <details class="pg-tables" id="pg-tables">
      <summary>테이블 목록 (클릭하면 SELECT 쿼리 삽입)</summary>
      <div class="pg-tables-grid" id="pg-tables-grid"></div>
    </details>
    <div class="pg-toolbar">
      <button class="pg-btn pg-btn-run" id="pg-run">실행</button>
      <button class="pg-btn pg-btn-reset" id="pg-reset">초기화</button>
      <span class="pg-shortcut">Ctrl+Enter</span>
    </div>
    <div id="pg-editor-wrap"></div>
    <div class="pg-result" id="pg-result"></div>
  </div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.18/codemirror.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.18/mode/sql/sql.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/sql.js/1.10.3/sql-wasm.js"></script>
<script>
(function() {
  let db = null, editor = null;
  function esc(s) { const d = document.createElement('div'); d.appendChild(document.createTextNode(s)); return d.innerHTML; }

  async function initDB() {
    try {
      const SQL = await initSqlJs({ locateFile: f => 'https://cdnjs.cloudflare.com/ajax/libs/sql.js/1.10.3/' + f });
      const resp = await fetch(new URL('../playground/ecommerce-playground.db', document.baseURI).href);
      if (!resp.ok) throw new Error('DB 파일을 찾을 수 없습니다 (HTTP ' + resp.status + ')');
      db = new SQL.Database(new Uint8Array(await resp.arrayBuffer()));
      document.getElementById('pg-loading').style.display = 'none';
      document.getElementById('pg-app').style.display = '';
      initEditor();
      loadTables();
    } catch (e) {
      document.getElementById('pg-loading').innerHTML = '<div class="pg-error">로드 실패: ' + esc(e.message) + '</div>';
    }
  }

  function initEditor() {
    const isDark = document.body.getAttribute('data-md-color-scheme') === 'slate';
    editor = CodeMirror(document.getElementById('pg-editor-wrap'), {
      value: 'SELECT * FROM customers LIMIT 10;',
      mode: 'text/x-sql',
      theme: isDark ? 'material-darker' : 'default',
      lineNumbers: true,
      indentWithTabs: false,
      tabSize: 2,
      scrollbarStyle: 'native',
      autofocus: true,
      extraKeys: { 'Ctrl-Enter': run }
    });
  }

  function loadTables() {
    const grid = document.getElementById('pg-tables-grid');
    const res = db.exec("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name != '_sc_metadata' ORDER BY name");
    if (!res.length) return;
    res[0].values.forEach(row => {
      const name = row[0];
      const cnt = db.exec("SELECT COUNT(*) FROM " + name);
      const rows = cnt.length ? cnt[0].values[0][0] : 0;
      const chip = document.createElement('span');
      chip.className = 'pg-table-chip';
      chip.innerHTML = name + '<span class="pg-chip-rows">(' + rows + ')</span>';
      chip.addEventListener('click', () => {
        editor.setValue('SELECT * FROM ' + name + ' LIMIT 20;');
        run();
        document.getElementById('pg-tables').open = false;
      });
      grid.appendChild(chip);
    });
  }

  function run() {
    const sql = editor.getValue().trim();
    const out = document.getElementById('pg-result');
    if (!sql) return;
    try {
      const t = performance.now();
      const results = db.exec(sql);
      const ms = (performance.now() - t).toFixed(1);
      if (!results.length) { out.innerHTML = '<div class="pg-status">실행 완료. 반환된 행 없음 (' + ms + 'ms)</div>'; return; }
      let h = '';
      results.forEach(r => {
        h += '<div class="pg-result-table-wrap"><table class="pg-result-table"><thead><tr>';
        r.columns.forEach(c => h += '<th>' + esc(c) + '</th>');
        h += '</tr></thead><tbody>';
        r.values.forEach(row => {
          h += '<tr>';
          row.forEach(v => h += v === null ? '<td><span class="null-val">NULL</span></td>' : '<td>' + esc(String(v)) + '</td>');
          h += '</tr>';
        });
        h += '</tbody></table></div>';
      });
      h += '<div class="pg-status">' + results[0].values.length + '행 (' + ms + 'ms)</div>';
      out.innerHTML = h;
    } catch (e) { out.innerHTML = '<div class="pg-error">' + esc(e.message) + '</div>'; }
  }

  document.addEventListener('DOMContentLoaded', function() {
    initDB();
    document.getElementById('pg-run').addEventListener('click', run);
    document.getElementById('pg-reset').addEventListener('click', () => {
      editor.setValue('SELECT * FROM customers LIMIT 10;');
      document.getElementById('pg-result').innerHTML = '';
    });
  });
})();
</script>
