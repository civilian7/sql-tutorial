# SQL 플레이그라운드

브라우저에서 직접 SQL을 실행할 수 있습니다. 서버 연결이 필요 없습니다.

!!! info "사용 데이터"
    이 플레이그라운드는 튜토리얼 데이터베이스의 축소 버전(테이블당 ~200행)을 사용합니다.
    전체 데이터(75만 건)로 실습하려면 [데이터베이스 생성](setup/03-generate.md)을 참고하세요.

<style>
#playground {
  font-family: var(--md-text-font-family, sans-serif);
}
#playground *,
#playground *::before,
#playground *::after {
  box-sizing: border-box;
}

/* Layout */
.pg-container {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
}
.pg-sidebar {
  width: 240px;
  flex-shrink: 0;
}
.pg-main {
  flex: 1;
  min-width: 0;
}

/* Sidebar */
.pg-table-list {
  border: 1px solid var(--md-default-fg-color--lightest, #ddd);
  border-radius: 4px;
  background: var(--md-code-bg-color, #f5f5f5);
  max-height: 420px;
  overflow-y: auto;
  padding: 0;
  margin: 0;
  list-style: none;
}
.pg-table-list li {
  padding: 6px 12px;
  cursor: pointer;
  font-size: 0.85rem;
  font-family: var(--md-code-font-family, monospace);
  border-bottom: 1px solid var(--md-default-fg-color--lightest, #eee);
  color: var(--md-default-fg-color, #333);
  transition: background 0.15s;
}
.pg-table-list li:last-child {
  border-bottom: none;
}
.pg-table-list li:hover {
  background: var(--md-accent-fg-color--transparent, rgba(92, 107, 192, 0.1));
}
.pg-table-list li.active {
  background: var(--md-accent-fg-color--transparent, rgba(92, 107, 192, 0.15));
  font-weight: 600;
}
.pg-sidebar-title {
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--md-default-fg-color--light, #666);
  margin-bottom: 8px;
}
.pg-col-info {
  font-size: 0.8rem;
  color: var(--md-default-fg-color--light, #666);
  background: var(--md-code-bg-color, #f5f5f5);
  border: 1px solid var(--md-default-fg-color--lightest, #ddd);
  border-top: none;
  border-radius: 0 0 4px 4px;
  padding: 8px 12px;
  max-height: 180px;
  overflow-y: auto;
}
.pg-col-info table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.78rem;
  font-family: var(--md-code-font-family, monospace);
}
.pg-col-info th,
.pg-col-info td {
  text-align: left;
  padding: 2px 6px;
  border-bottom: 1px solid var(--md-default-fg-color--lightest, #eee);
}
.pg-col-info th {
  font-weight: 600;
  color: var(--md-default-fg-color--light, #666);
}

/* Editor */
.pg-editor {
  width: 100%;
  min-height: 160px;
  padding: 12px;
  font-family: var(--md-code-font-family, monospace);
  font-size: 0.9rem;
  line-height: 1.5;
  border: 1px solid var(--md-default-fg-color--lightest, #ddd);
  border-radius: 4px;
  background: var(--md-code-bg-color, #f5f5f5);
  color: var(--md-code-fg-color, #333);
  resize: vertical;
  tab-size: 2;
}
.pg-editor:focus {
  outline: 2px solid var(--md-accent-fg-color, #5c6bc0);
  outline-offset: -1px;
}

/* Buttons */
.pg-toolbar {
  display: flex;
  gap: 8px;
  margin-top: 8px;
  align-items: center;
}
.pg-btn {
  padding: 8px 20px;
  border: none;
  border-radius: 4px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s, opacity 0.15s;
}
.pg-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.pg-btn-run {
  background: var(--md-accent-fg-color, #5c6bc0);
  color: #fff;
}
.pg-btn-run:hover:not(:disabled) {
  opacity: 0.85;
}
.pg-btn-reset {
  background: var(--md-default-fg-color--lightest, #ddd);
  color: var(--md-default-fg-color, #333);
}
.pg-btn-reset:hover:not(:disabled) {
  opacity: 0.7;
}
.pg-shortcut-hint {
  font-size: 0.78rem;
  color: var(--md-default-fg-color--light, #999);
  margin-left: 8px;
}

/* Sample queries */
.pg-samples {
  margin-top: 12px;
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.pg-sample-btn {
  padding: 4px 10px;
  font-size: 0.75rem;
  font-family: var(--md-code-font-family, monospace);
  background: var(--md-code-bg-color, #f5f5f5);
  border: 1px solid var(--md-default-fg-color--lightest, #ddd);
  border-radius: 3px;
  cursor: pointer;
  color: var(--md-default-fg-color, #333);
  transition: background 0.15s;
  max-width: 100%;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.pg-sample-btn:hover {
  background: var(--md-accent-fg-color--transparent, rgba(92, 107, 192, 0.1));
  border-color: var(--md-accent-fg-color, #5c6bc0);
}

/* Result */
.pg-result {
  margin-top: 16px;
}
.pg-result-table-wrap {
  overflow-x: auto;
  border: 1px solid var(--md-default-fg-color--lightest, #ddd);
  border-radius: 4px;
}
.pg-result-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.83rem;
  font-family: var(--md-code-font-family, monospace);
  white-space: nowrap;
}
.pg-result-table th {
  background: var(--md-primary-fg-color, #37474f);
  color: var(--md-primary-bg-color, #fff);
  padding: 6px 12px;
  text-align: left;
  position: sticky;
  top: 0;
  font-weight: 600;
}
.pg-result-table td {
  padding: 5px 12px;
  border-bottom: 1px solid var(--md-default-fg-color--lightest, #eee);
  color: var(--md-default-fg-color, #333);
}
.pg-result-table tr:hover td {
  background: var(--md-accent-fg-color--transparent, rgba(92, 107, 192, 0.05));
}
.pg-result-table .null-val {
  color: var(--md-default-fg-color--lighter, #aaa);
  font-style: italic;
}
.pg-status {
  font-size: 0.8rem;
  color: var(--md-default-fg-color--light, #666);
  margin-top: 6px;
}
.pg-error {
  background: #fdecea;
  color: #b71c1c;
  border: 1px solid #f5c6cb;
  border-radius: 4px;
  padding: 10px 14px;
  font-size: 0.85rem;
  margin-top: 12px;
  font-family: var(--md-code-font-family, monospace);
}
[data-md-color-scheme="slate"] .pg-error {
  background: #4e1a1a;
  color: #ffcdd2;
  border-color: #6e2a2a;
}

/* Loading */
.pg-loading {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 24px;
  color: var(--md-default-fg-color--light, #666);
}
.pg-spinner {
  width: 24px;
  height: 24px;
  border: 3px solid var(--md-default-fg-color--lightest, #ddd);
  border-top-color: var(--md-accent-fg-color, #5c6bc0);
  border-radius: 50%;
  animation: pg-spin 0.8s linear infinite;
}
@keyframes pg-spin {
  to { transform: rotate(360deg); }
}

/* Responsive */
@media (max-width: 768px) {
  .pg-container {
    flex-direction: column;
  }
  .pg-sidebar {
    width: 100%;
  }
  .pg-table-list {
    max-height: 200px;
  }
}
</style>

<div id="playground">
  <div class="pg-loading" id="pg-loading">
    <div class="pg-spinner"></div>
    <span>데이터베이스를 불러오는 중...</span>
  </div>

  <div id="pg-app" style="display:none;">
    <div class="pg-container">
      <div class="pg-sidebar">
        <div class="pg-sidebar-title">테이블 목록</div>
        <ul class="pg-table-list" id="pg-table-list"></ul>
        <div class="pg-col-info" id="pg-col-info" style="display:none;"></div>
      </div>
      <div class="pg-main">
        <textarea class="pg-editor" id="pg-editor" spellcheck="false"
          placeholder="SQL 쿼리를 입력하세요...">SELECT * FROM customers LIMIT 10;</textarea>
        <div class="pg-toolbar">
          <button class="pg-btn pg-btn-run" id="pg-run">실행</button>
          <button class="pg-btn pg-btn-reset" id="pg-reset">초기화</button>
          <span class="pg-shortcut-hint">Ctrl+Enter로 실행</span>
        </div>
        <div class="pg-samples">
          <span style="font-size:0.78rem; color:var(--md-default-fg-color--light,#999); margin-right:4px;">예제:</span>
          <button class="pg-sample-btn" data-sql="SELECT * FROM customers LIMIT 10;">customers 조회</button>
          <button class="pg-sample-btn" data-sql="SELECT name, price FROM products ORDER BY price DESC LIMIT 5;">비싼 상품 TOP 5</button>
          <button class="pg-sample-btn" data-sql="SELECT grade, COUNT(*) AS cnt FROM customers GROUP BY grade;">등급별 고객 수</button>
          <button class="pg-sample-btn" data-sql="SELECT c.name, COUNT(o.id) AS orders&#10;FROM customers c&#10;JOIN orders o ON c.id = o.customer_id&#10;GROUP BY c.id&#10;ORDER BY orders DESC LIMIT 5;">주문 많은 고객 TOP 5</button>
        </div>
        <div class="pg-result" id="pg-result"></div>
      </div>
    </div>
  </div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/sql.js/1.10.3/sql-wasm.js"></script>
<script>
(function() {
  let db = null;

  async function initDB() {
    const loading = document.getElementById('pg-loading');
    const app = document.getElementById('pg-app');
    try {
      const SQL = await initSqlJs({
        locateFile: f => 'https://cdnjs.cloudflare.com/ajax/libs/sql.js/1.10.3/' + f
      });
      const resp = await fetch(new URL('../playground/ecommerce-playground.db', document.baseURI).href);
      if (!resp.ok) throw new Error('데이터베이스 파일을 찾을 수 없습니다 (HTTP ' + resp.status + ')');
      const buf = await resp.arrayBuffer();
      db = new SQL.Database(new Uint8Array(buf));
      loading.style.display = 'none';
      app.style.display = '';
      loadTableList();
    } catch (e) {
      loading.innerHTML = '<div class="pg-error">데이터베이스 로드 실패: ' + escapeHtml(e.message) + '</div>';
    }
  }

  function loadTableList() {
    const list = document.getElementById('pg-table-list');
    const res = db.exec("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name");
    if (!res.length) return;
    res[0].values.forEach(row => {
      const li = document.createElement('li');
      li.textContent = row[0];
      li.addEventListener('click', () => showTableInfo(row[0], li));
      list.appendChild(li);
    });
  }

  function showTableInfo(tableName, li) {
    // Toggle active
    document.querySelectorAll('.pg-table-list li').forEach(el => el.classList.remove('active'));
    li.classList.add('active');

    const info = document.getElementById('pg-col-info');
    const res = db.exec("PRAGMA table_info('" + tableName.replace(/'/g, "''") + "')");
    if (!res.length) { info.style.display = 'none'; return; }

    let html = '<table><tr><th>컬럼</th><th>타입</th><th>PK</th></tr>';
    res[0].values.forEach(r => {
      html += '<tr><td>' + escapeHtml(r[1]) + '</td><td>' + escapeHtml(r[2] || '-') + '</td><td>' + (r[5] ? 'O' : '') + '</td></tr>';
    });
    html += '</table>';
    info.innerHTML = html;
    info.style.display = '';
  }

  function executeQuery() {
    const editor = document.getElementById('pg-editor');
    const resultDiv = document.getElementById('pg-result');
    const sql = editor.value.trim();
    if (!sql) return;

    try {
      const start = performance.now();
      const results = db.exec(sql);
      const elapsed = (performance.now() - start).toFixed(1);

      if (!results.length) {
        resultDiv.innerHTML = '<div class="pg-status">쿼리가 실행되었습니다. 반환된 행이 없습니다. (' + elapsed + 'ms)</div>';
        return;
      }

      let html = '';
      results.forEach((res, idx) => {
        if (results.length > 1) html += '<div class="pg-status" style="margin-bottom:4px;">결과 ' + (idx + 1) + '</div>';
        html += '<div class="pg-result-table-wrap"><table class="pg-result-table"><thead><tr>';
        res.columns.forEach(col => { html += '<th>' + escapeHtml(col) + '</th>'; });
        html += '</tr></thead><tbody>';
        res.values.forEach(row => {
          html += '<tr>';
          row.forEach(val => {
            if (val === null) {
              html += '<td><span class="null-val">NULL</span></td>';
            } else {
              html += '<td>' + escapeHtml(String(val)) + '</td>';
            }
          });
          html += '</tr>';
        });
        html += '</tbody></table></div>';
      });
      html += '<div class="pg-status">' + results[0].values.length + '개 행 반환 (' + elapsed + 'ms)</div>';
      resultDiv.innerHTML = html;
    } catch (e) {
      resultDiv.innerHTML = '<div class="pg-error">' + escapeHtml(e.message) + '</div>';
    }
  }

  function resetDB() {
    document.getElementById('pg-editor').value = 'SELECT * FROM customers LIMIT 10;';
    document.getElementById('pg-result').innerHTML = '';
  }

  function escapeHtml(s) {
    const d = document.createElement('div');
    d.appendChild(document.createTextNode(s));
    return d.innerHTML;
  }

  // Event bindings
  document.addEventListener('DOMContentLoaded', function() {
    initDB();
    document.getElementById('pg-run').addEventListener('click', executeQuery);
    document.getElementById('pg-reset').addEventListener('click', resetDB);
    document.getElementById('pg-editor').addEventListener('keydown', function(e) {
      if (e.ctrlKey && e.key === 'Enter') { e.preventDefault(); executeQuery(); }
      // Tab indent
      if (e.key === 'Tab') {
        e.preventDefault();
        const s = this.selectionStart, end = this.selectionEnd;
        this.value = this.value.substring(0, s) + '  ' + this.value.substring(end);
        this.selectionStart = this.selectionEnd = s + 2;
      }
    });
    document.querySelectorAll('.pg-sample-btn').forEach(btn => {
      btn.addEventListener('click', function() {
        const sql = this.getAttribute('data-sql').replace(/&#10;/g, '\n');
        document.getElementById('pg-editor').value = sql;
        executeQuery();
      });
    });
  });
})();
</script>
