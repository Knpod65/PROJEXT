// ══════════════════════════════════════════
// EMS Frontend — Complete Role-Based Script
// ══════════════════════════════════════════
const API = '/api';

// ── Security: HTML escaping ───────────────
// ALWAYS use esc() when interpolating user/server data into innerHTML.
// NEVER interpolate raw server/user data without esc().
function esc(str) {
  if (str === null || str === undefined) return '—';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#x27;');
}

// Safe text node setter — use instead of innerHTML for plain text
function setText(id, value) {
  const el = document.getElementById(id);
  if (el) el.textContent = value ?? '—';
}

// ── Auth state ────────────────────────────
// SECURITY: Token is stored in HttpOnly cookie set by the server.
// We do NOT store it in localStorage or JS variables.
// fetch() sends cookies automatically with credentials: 'include'.
let currentUser = null;
let activePage = '';

// ── API helpers ───────────────────────────
async function api(method, path, body) {
  const opts = {
    method,
    credentials: 'include',  // send HttpOnly session cookie automatically
    headers: {'Content-Type': 'application/json'},
  };
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch(API + path, opts);
  if (res.status === 401) { doLogout(); return null; }
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || 'เกิดข้อผิดพลาด');
  return data;
}

async function apiUpload(path, formData) {
  const res = await fetch(API + path, {
    method: 'POST',
    credentials: 'include',
    body: formData,  // no Content-Type header — browser sets multipart boundary
  });
  if (res.status === 401) { doLogout(); return null; }
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || 'เกิดข้อผิดพลาด');
  return data;
}
const get  = p    => api('GET',p);
const post = (p,b)=> api('POST',p,b);
const put  = (p,b)=> api('PUT',p,b);
const del  = p    => api('DELETE',p);

// ── Auth ──────────────────────────────────
// SECURITY: No token handling in JS — cookies are set/cleared by the server.
async function doLogin() {
  const u = document.getElementById('l-user').value.trim();
  const p = document.getElementById('l-pass').value;
  const errEl = document.getElementById('l-err');
  errEl.style.display = 'none';
  try {
    const data = await post('/auth/login', {username: u, password: p});
    if (!data) return;
    // Server sets HttpOnly cookie — we only use the user object from the response body
    currentUser = data.user;
    initApp();
  } catch(e) {
    errEl.textContent = 'ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง';
    errEl.style.display = 'block';
  }
}
document.addEventListener('keydown', e => {
  const loginPage = document.getElementById('login-page');
  if (e.key === 'Enter' && loginPage && loginPage.style.display !== 'none') doLogin();
});
async function doLogout() {
  try { await post('/auth/logout', {}); } catch(e) { /* best effort */ }
  currentUser = null;
  // No localStorage to clear — server clears the cookie via Set-Cookie: expires=past
  location.reload();
}

// ── Init ──────────────────────────────────
// On page load: try to restore session from the HttpOnly cookie.
// The cookie is sent automatically with fetch (credentials: 'include').
// If the server returns 401, the user sees the login screen.
async function initApp() {
  try {
    if (!currentUser) {
      currentUser = await get('/auth/me');
      if (!currentUser) { showLoginPage(); return; }
    }
    document.getElementById('login-page').style.display = 'none';
    document.getElementById('app').style.display = 'flex';
    updateNavForRole();
    const eff = getEff();
    if (eff === 'staff')   navigate('dashboard');
    else if (eff === 'teacher') navigate('schedule');
    else if (eff === 'student') navigate('student');
    else navigate('dashboard');
  } catch {
    // 401 or network error — show login
    showLoginPage();
  }
}

function showLoginPage() {
  document.getElementById('login-page').style.display = 'flex';
  document.getElementById('app').style.display = 'none';
  currentUser = null;
}

// Auto-initialize on load
window.addEventListener('DOMContentLoaded', () => initApp());

function getEff() {
  return currentUser?.effective_role || currentUser?.role || 'staff';
}

// ── Nav update per role ───────────────────
function updateNavForRole() {
  const u = currentUser;
  if (!u) return;
  document.getElementById('pill-name').textContent = u.full_name || u.username;
  const roleLabel = {admin:'ผู้ดูแลระบบ',staff:'เจ้าหน้าที่',teacher:'อาจารย์',student:'นักศึกษา'};
  const eff = getEff();
  document.getElementById('pill-role').textContent = roleLabel[eff] || eff;

  const banner = document.getElementById('view-as-banner');
  if (u.view_as_role) {
    banner.classList.add('show');
    document.getElementById('vas-label').textContent = roleLabel[u.view_as_role] || u.view_as_role;
  } else {
    banner.classList.remove('show');
  }

  // Show/hide nav by role
  const isAdmin   = u.role === 'admin';
  const isTeacher = eff === 'teacher';
  const isStaff   = eff === 'staff';
  const isStudent = eff === 'student';

  const show = (id, visible) => {
    const el = document.getElementById(id);
    if (el) el.style.display = visible ? 'flex' : 'none';
  };
  const showBlock = (id, visible) => {
    const el = document.getElementById(id);
    if (el) el.style.display = visible ? 'block' : 'none';
  };

  // All roles see dashboard + schedule + student-search
  show('nav-staff-stats', isStaff || isAdmin);
  show('nav-sections', isAdmin || isTeacher);
  show('nav-copy', isAdmin || isStaff);
  show('nav-swap', isStaff || isAdmin || isTeacher);
  show('nav-checkin', isStaff || isAdmin || isTeacher);
  show('nav-submissions', isTeacher || isAdmin);
  show('nav-optimizer', isAdmin);
  showBlock('nav-admin-label', isAdmin);
  show('nav-settings', isAdmin);
  show('nav-users', isAdmin);
  // Student only sees student search
  show('nav-schedule-all', !isStudent);
  show('nav-student-search', true);
  show('nav-sections-nav', isAdmin || isStaff);

  // Waiting count badge
  if (isStaff || isTeacher || isAdmin) loadWaitingCount();
}

async function loadWaitingCount() {
  try {
    const w = await get('/swaps2/waiting');
    const count = (w||[]).length;
    const badge = document.getElementById('swap-badge');
    if (badge) {
      badge.textContent = count;
      badge.style.display = count > 0 ? 'inline-block' : 'none';
    }
  } catch {}
}

// ── View-As ───────────────────────────────
function toggleViewAsPanel() {
  if (!currentUser || currentUser.role !== 'admin') return;
  document.getElementById('viewas-overlay').classList.add('show');
  const chips = document.getElementById('role-chips');
  const eff = currentUser.view_as_role || currentUser.role;
  const labels = {admin:'Admin',staff:'เจ้าหน้าที่',teacher:'อาจารย์',student:'นักศึกษา'};
  chips.innerHTML = `
    <div class="role-chip reset" onclick="resetViewAs()">✖ มุมมองตัวเอง</div>
    ${['staff','teacher','student'].map(r=>`
      <div class="role-chip ${eff===r?'active':''}" onclick="setViewAs('${r}')">${labels[r]}</div>
    `).join('')}
  `;
}
async function setViewAs(role) {
  const d = await post('/auth/view-as',{role});
  currentUser.view_as_role = role;
  currentUser.effective_role = d.effective_role;
  document.getElementById('viewas-overlay').classList.remove('show');
  updateNavForRole();
  navigate('dashboard');
  toast(`ดูในฐานะ: ${role}`,'success');
}
async function resetViewAs() {
  await post('/auth/view-as',{role:null});
  currentUser.view_as_role = null;
  currentUser.effective_role = currentUser.role;
  document.getElementById('viewas-overlay').classList.remove('show');
  updateNavForRole();
  navigate('dashboard');
  toast('รีเซ็ตมุมมองแล้ว');
}

// ── Navigate ──────────────────────────────
const pageTitle = {
  dashboard:'📊 แดชบอร์ด', schedule:'📅 ตารางสอบ', sections:'📚 รายวิชา / Sections',
  copy:'🖨️ คำนวณค่าถ่ายเอกสาร', student:'🎓 ค้นหาตารางสอบ',
  swaps:'🔄 สลับคุมสอบ', checkins:'✅ Check-in',
  submissions:'📋 ข้อสอบของฉัน', optimizer:'⚙️ Optimizer',
  users:'👥 จัดการผู้ใช้', settings:'⚙️ ตั้งค่าระบบ',
};

function navigate(page) {
  activePage = page;
  document.getElementById('page-title').textContent = pageTitle[page] || page;
  document.querySelectorAll('.nav-item').forEach(el=>el.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(el=>{
    if(el.getAttribute('onclick')?.includes(`'${page}'`)) el.classList.add('active');
  });
  document.getElementById('topbar-actions').innerHTML = '';
  const c = document.getElementById('content');
  c.innerHTML = '<div style="display:flex;justify-content:center;padding:60px"><div class="loader"></div></div>';

  const eff = getEff();
  const pages = {
    dashboard: () => (eff==='staff' ? loadStaffDashboard() : loadAdminDashboard()),
    schedule:  loadSchedule,
    sections:  loadSections,
    copy:      loadCopyCount,
    student:   loadStudentSearch,
    swaps:     loadSwaps,
    checkins:  loadCheckins,
    submissions: loadSubmissions,
    optimizer: loadOptimizer,
    users:     loadUsers,
    settings:  loadSettings,
  };
  (pages[page] || (()=>{c.innerHTML='<div class="empty"><p>ยังไม่ implement</p></div>';}))();
}

// ─────────────────────────────────────────
// DASHBOARD — ADMIN/STAFF
// ─────────────────────────────────────────
async function loadAdminDashboard() {
  const data = await get('/dashboard/');
  if (!data) return;
  const pct = data.total_sections ? Math.round(data.scheduled_sections/data.total_sections*100) : 0;
  document.getElementById('content').innerHTML = `
    <div class="stat-grid">
      <div class="stat-card">
        <div class="stat-icon" style="background:var(--crimson-lt)">📚</div>
        <div>
          <div class="stat-val">${parseInt(data.total_sections)||0}</div>
          <div class="stat-lbl">Sections ทั้งหมด</div>
          <div class="progress-bar-wrap"><div class="progress-bar-fill" style="width:${pct}%"></div></div>
          <div class="stat-sub">${parseInt(data.scheduled_sections)||0} จัดแล้ว (${pct}%)</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background:rgba(13,110,253,.08)">👨‍🎓</div>
        <div><div class="stat-val">${(parseInt(data.total_students)||0).toLocaleString()}</div><div class="stat-lbl">นักศึกษาทั้งหมด</div><div class="stat-sub">${parseInt(data.total_teachers)||0} อาจารย์</div></div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background:var(--gold-lt)">🖨️</div>
        <div><div class="stat-val">${(parseInt(data.total_sheets)||0).toLocaleString()}</div><div class="stat-lbl">แผ่นถ่ายเอกสารรวม</div><div class="stat-sub">฿${(parseFloat(data.copy_cost)||0).toLocaleString('th',{minimumFractionDigits:2})}</div></div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background:var(--green-lt)">🏫</div>
        <div><div class="stat-val">${parseInt(data.rooms_in_use)||0}</div><div class="stat-lbl">ห้องสอบที่ใช้</div><div class="stat-sub">${parseInt(data.unscheduled_sections)||0} sections ยังไม่ได้จัด</div></div>
      </div>
    </div>
    <div class="card">
      <div class="card-head"><h3>📋 ประวัติการใช้งาน</h3><span class="badge badge-gray">${data.recent_logs.length} รายการ</span></div>
      <div style="max-height:320px;overflow-y:auto">
        ${data.recent_logs.map(l=>`
          <div class="log-item" style="padding:10px 20px">
            <div class="log-time">${l.timestamp?new Date(l.timestamp).toLocaleString('th-TH',{dateStyle:'short',timeStyle:'short'}):'—'}</div>
            <div class="log-body">
              <span class="badge badge-navy log-action" style="margin-right:6px">${l.action}</span>
              <span class="log-actor">${l.actor||'—'}</span>
            </div>
          </div>
        `).join('')}
      </div>
    </div>
  `;
}

// ─────────────────────────────────────────
// STAFF DASHBOARD
// ─────────────────────────────────────────
async function loadStaffDashboard() {
  const [stats, waiting] = await Promise.all([
    get(`/exports/supervision-stats/${currentUser.id}`).catch(()=>null),
    get('/swaps2/waiting').catch(()=>[]),
  ]);
  const wCount = (waiting||[]).length;
  document.getElementById('content').innerHTML = `
    ${wCount>0?`<div style="background:var(--gold-lt);border:1px solid rgba(184,134,11,.3);border-radius:var(--radius);padding:12px 16px;margin-bottom:16px;display:flex;align-items:center;justify-content:space-between">
      <span style="font-size:13px;font-weight:600;color:var(--gold)">🔔 มีคำขอสลับรอตอบ ${wCount} รายการ</span>
      <button class="btn btn-gold btn-sm" onclick="navigate('swaps')">ดูคำขอ</button>
    </div>`:''}
    <div class="stat-grid">
      <div class="stat-card">
        <div class="stat-icon" style="background:var(--crimson-lt)">📋</div>
        <div><div class="stat-val">${stats?.baseline_count||0}</div><div class="stat-lbl">ตารางคุมสอบ (baseline)</div></div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background:var(--green-lt)">✅</div>
        <div><div class="stat-val">${stats?.actual_count||0}</div><div class="stat-lbl">ปัจจุบัน</div></div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background:var(--gold-lt)">🔄</div>
        <div><div class="stat-val">${stats?.swapped_in||0}</div><div class="stat-lbl">รับเพิ่มจาก Swap</div></div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background:rgba(13,110,253,.08)">📤</div>
        <div><div class="stat-val">${stats?.swapped_out||0}</div><div class="stat-lbl">สลับออกไป</div></div>
      </div>
    </div>
    <div class="card">
      <div class="card-head"><h3>📅 ตารางคุมสอบ baseline ของฉัน</h3><span class="badge badge-navy">${stats?.baseline_count||0} ครั้ง</span></div>
      <div class="table-wrap">
        <table>
          <thead><tr><th>วันที่</th><th>เวลา</th><th>วิชา</th><th>ห้อง</th><th>ลำดับ</th></tr></thead>
          <tbody>
            ${(stats?.baseline_sessions||[]).length?(stats.baseline_sessions||[]).map(s=>`<tr>
              <td>${s.date||'—'}</td><td>${s.time||'—'}</td>
              <td class="td-mono">${s.course||'—'}</td><td>${s.room||'—'}</td>
              <td><span class="badge ${s.slot_order===1?'badge-navy':'badge-gray'}">${s.slot_order===1?'หลัก':'รอง'}</span></td>
            </tr>`).join(''):'<tr><td colspan="5" style="text-align:center;padding:30px;color:var(--text-muted)">ยังไม่มี baseline — Admin ต้อง Lock ก่อน</td></tr>'}
          </tbody>
        </table>
      </div>
    </div>
  `;
}

// ─────────────────────────────────────────
// SCHEDULE — role-aware display
// ─────────────────────────────────────────
function isMySupervision(sups) {
  return (sups||[]).some(sv=>sv.user?.id===currentUser?.id && !sv.is_swapped);
}
function isMySwapped(sups) {
  return (sups||[]).some(sv=>sv.user?.id===currentUser?.id && sv.is_swapped);
}

function thDate(d) {
  if (!d) return '—';
  const [y,m,day]=d.split('-');
  const m_th=['','ม.ค.','ก.พ.','มี.ค.','เม.ย.','พ.ค.','มิ.ย.','ก.ค.','ส.ค.','ก.ย.','ต.ค.','พ.ย.','ธ.ค.'];
  return `${parseInt(day)} ${m_th[parseInt(m)]} ${y}`;
}

async function loadSchedule() {
  document.getElementById('topbar-actions').innerHTML = `
    <button class="btn btn-outline btn-sm" onclick="exportSchedulePDF('final')">📄 Export PDF</button>
    ${currentUser?.role==='admin'?`<button class="btn btn-primary btn-sm" onclick="openAddScheduleModal()">➕ เพิ่มตาราง</button>`:''}
  `;
  const data = await get('/schedule/grouped');
  if (!data) return;
  const eff = getEff();
  const showSups = eff !== 'student';
  const showSheets = eff !== 'student';

  if (!data.length) {
    document.getElementById('content').innerHTML='<div class="empty"><div class="ico">📅</div><p>ยังไม่มีตารางสอบ</p></div>';
    return;
  }
  document.getElementById('content').innerHTML = data.map(group=>`
    <div class="day-block">
      <div class="day-header">
        <span class="day-tag">📅 ${thDate(group.date)}</span>
        <span class="day-count">${group.items.length} วิชา</span>
      </div>
      <div class="schedule-cards">
        ${group.items.map(s=>{
          const mine = isMySupervision(s.supervisions);
          const swapped = isMySwapped(s.supervisions);
          return `
          <div class="sch-card ${mine?'my-schedule':''} ${swapped?'swapped-schedule':''}" onclick="openScheduleDetail(${s.id})">
            <div class="course-id">
              ${esc(s.course?.course_id)} Sec ${esc(s.section?.section_no)}
              ${mine?'<span class="badge" style="font-size:10px;background:var(--crimson);color:#fff;margin-left:6px">คุมสอบ</span>':''}
              ${swapped?'<span class="badge badge-gold" style="font-size:10px;margin-left:6px">Swap ↔</span>':''}
            </div>
            <div class="course-name">${esc(s.course?.course_name_th)}</div>
            <div class="info-row">
              <span>⏰ ${esc(s.exam_time)}</span>
              <span>🏫 ${esc(s.room?.room_name)}</span>
              <span>👨‍🎓 ${parseInt(s.section?.num_students)||0} คน</span>
            </div>
            ${showSups?`<div class="sups">
              ${(s.supervisions||[]).map(sv=>`
                <span class="badge ${sv.slot_order===1?'badge-navy':'badge-gray'}" style="${sv.is_swapped?'opacity:.6':''}" title="${sv.is_swapped?'Swapped':''}">
                  ${sv.user?.full_name||'—'}${sv.is_swapped?' ↔':''}${sv.is_emergency?' 🚨':''}
                </span>
              `).join('')}
              ${s.paper_distributor?`<span class="badge badge-gold">📋 ${s.paper_distributor}</span>`:''}
            </div>`:''}
            <div style="margin-top:8px;display:flex;gap:6px">
              <span class="badge ${s.status==='published'?'badge-green':'badge-gray'}">${s.status}</span>
              ${showSheets?`<span class="badge badge-red">📄 ${s.total_sheets} แผ่น</span>`:''}
            </div>
          </div>`;
        }).join('')}
      </div>
    </div>
  `).join('');
}

async function openScheduleDetail(id) {
  const all = await get('/schedule/');
  const s = (all||[]).find(x=>x.id===id);
  if (!s) return;
  const eff = getEff();
  const isAdmin = currentUser?.role==='admin';
  openModal(`📅 ${s.section?.course?.course_id||''} Sec ${s.section?.section_no||''} — รายละเอียด`,`
    <div class="form-row" style="margin-bottom:12px">
      <div class="form-group"><label>วิชา</label><div class="form-control" style="background:var(--surface2)">${s.section?.course?.course_name_th||'—'}</div></div>
      <div class="form-group"><label>อาจารย์</label><div class="form-control" style="background:var(--surface2)">${s.section?.teacher?.full_name||'—'}</div></div>
    </div>
    <div class="form-row" style="margin-bottom:12px">
      <div class="form-group"><label>วันสอบ</label><div class="form-control" style="background:var(--surface2)">${s.exam_date}</div></div>
      <div class="form-group"><label>เวลา</label><div class="form-control" style="background:var(--surface2)">${s.exam_time}</div></div>
    </div>
    <div class="form-row" style="margin-bottom:12px">
      <div class="form-group"><label>ห้อง (จุ ${s.room?.capacity||0})</label><div class="form-control" style="background:var(--surface2)">${s.room?.room_name||'—'}</div></div>
      <div class="form-group"><label>นักศึกษา / แผ่น</label><div class="form-control" style="background:var(--surface2);font-weight:700;color:var(--crimson)">${s.section?.num_students||0} คน × ${s.num_pages} หน้า = ${s.total_sheets} แผ่น</div></div>
    </div>
    <div class="form-group" style="margin-bottom:12px">
      <label>กรรมการคุมสอบ</label>
      <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:6px">
        ${(s.supervisions||[]).map(sv=>`
          <div class="badge ${sv.slot_order===1?'badge-navy':'badge-gray'}" style="font-size:12px;padding:6px 12px;${sv.is_swapped?'opacity:.65':''}">
            ${sv.slot_order===1?'⭐ หลัก: ':'· รอง: '}${sv.user?.full_name||'—'}
            ${sv.is_swapped?' <span style="color:var(--gold)">(Swap)</span>':''}
            ${sv.is_emergency?' <span style="color:var(--crimson)">(แทนฉุกเฉิน)</span>':''}
            ${sv.confirmed?' ✅':''}
          </div>
        `).join('')||'<span style="color:var(--text-muted)">ยังไม่ได้กำหนด</span>'}
      </div>
    </div>
    <div class="form-group">
      <label>ผู้จ่ายข้อสอบ</label>
      <div class="form-control" style="background:var(--surface2)">${s.paper_distributor||'—'}</div>
    </div>
  `,[
    isAdmin ? {label:'✏️ แก้ไข',cls:'btn-outline',action:()=>openEditScheduleModal(s)} : null,
    (eff==='staff'||eff==='teacher') ? {label:'🔄 ขอสลับกะนี้',cls:'btn-gold',action:()=>{closeModal();navigate('swaps');}} : null,
  ].filter(Boolean));
}

async function openAddScheduleModal() {
  const [sections,rooms] = await Promise.all([get('/courses/sections?semester=2&academic_year=2568'),get('/courses/rooms')]);
  const unscheduled = (sections||[]).filter(s=>!s.schedule);
  openModal('➕ เพิ่มตารางสอบ',`
    <div class="form-group" style="margin-bottom:12px"><label>Section *</label>
      <select class="form-control" id="f-section-id">
        <option value="">— เลือก section —</option>
        ${unscheduled.map(s=>`<option value="${s.id}">${s.course?.course_id} Sec${s.section_no} — ${s.course?.course_name_th} (${s.num_students} คน)</option>`).join('')}
      </select>
    </div>
    <div class="form-row" style="margin-bottom:12px">
      <div class="form-group"><label>วันสอบ *</label><input class="form-control" id="f-exam-date" type="date"></div>
      <div class="form-group"><label>เวลา *</label><input class="form-control" id="f-exam-time" placeholder="09.00-12.00"></div>
    </div>
    <div class="form-row" style="margin-bottom:12px">
      <div class="form-group"><label>ห้องสอบ *</label>
        <select class="form-control" id="f-room-id">
          <option value="">— เลือกห้อง —</option>
          ${(rooms||[]).map(r=>`<option value="${r.id}">${r.room_name} (${r.capacity})</option>`).join('')}
        </select>
      </div>
      <div class="form-group"><label>หน้า</label><input class="form-control" id="f-num-pages" type="number" value="1"></div>
    </div>
    <div class="form-group"><label>ผู้จ่ายข้อสอบ</label><input class="form-control" id="f-distributor"></div>
  `,[{label:'บันทึก',cls:'btn-primary',action:saveSchedule}]);
}
async function saveSchedule() {
  try {
    await post('/schedule/',{
      section_id:parseInt(document.getElementById('f-section-id').value),
      room_id:parseInt(document.getElementById('f-room-id').value),
      exam_date:document.getElementById('f-exam-date').value,
      exam_time:document.getElementById('f-exam-time').value,
      num_pages:parseInt(document.getElementById('f-num-pages').value)||1,
      paper_distributor:document.getElementById('f-distributor').value,
    });
    closeModal(); toast('เพิ่มตารางสอบสำเร็จ ✅','success'); loadSchedule();
  } catch(e){toast(e.message,'error');}
}
async function openEditScheduleModal(s) {
  const rooms = await get('/courses/rooms');
  openModal('✏️ แก้ไขตารางสอบ',`
    <div class="form-row" style="margin-bottom:12px">
      <div class="form-group"><label>วันสอบ</label><input class="form-control" id="e-date" type="date" value="${s.exam_date}"></div>
      <div class="form-group"><label>เวลา</label><input class="form-control" id="e-time" value="${s.exam_time}"></div>
    </div>
    <div class="form-row" style="margin-bottom:12px">
      <div class="form-group"><label>ห้อง</label>
        <select class="form-control" id="e-room">
          ${(rooms||[]).map(r=>`<option value="${r.id}" ${r.id===s.room?.id?'selected':''}>${r.room_name}</option>`).join('')}
        </select>
      </div>
      <div class="form-group"><label>หน้า</label><input class="form-control" id="e-pages" type="number" value="${s.num_pages}"></div>
    </div>
    <div class="form-row">
      <div class="form-group"><label>ผู้จ่ายข้อสอบ</label><input class="form-control" id="e-dist" value="${s.paper_distributor||''}"></div>
      <div class="form-group"><label>สถานะ</label>
        <select class="form-control" id="e-status">
          <option value="draft" ${s.status==='draft'?'selected':''}>draft</option>
          <option value="published" ${s.status==='published'?'selected':''}>published</option>
          <option value="locked" ${s.status==='locked'?'selected':''}>locked</option>
        </select>
      </div>
    </div>
  `,[
    {label:'บันทึก',cls:'btn-primary',action:async()=>{
      try{await put(`/schedule/${s.id}`,{room_id:parseInt(document.getElementById('e-room').value),exam_date:document.getElementById('e-date').value,exam_time:document.getElementById('e-time').value,num_pages:parseInt(document.getElementById('e-pages').value),paper_distributor:document.getElementById('e-dist').value,status:document.getElementById('e-status').value});closeModal();toast('แก้ไขสำเร็จ ✅','success');loadSchedule();}catch(e){toast(e.message,'error');}
    }},
    {label:'🗑 ลบ',cls:'btn-danger',action:async()=>{if(!confirm('ยืนยันลบ?'))return;await del(`/schedule/${s.id}`);closeModal();toast('ลบแล้ว','success');loadSchedule();}},
  ]);
}
function exportSchedulePDF(type) {
  window.open(`/api/exports/schedule?semester=2&academic_year=2568&exam_type=${type}`,'_blank');
}

// ─────────────────────────────────────────
// SECTIONS
// ─────────────────────────────────────────
let sectionsCache=[], sectionSearch='';
async function loadSections() {
  document.getElementById('topbar-actions').innerHTML =
    currentUser?.role==='admin'?'<button class="btn btn-primary btn-sm" onclick="openAddSectionModal()">➕ เพิ่ม Section</button>':'';
  const data = await get(`/courses/sections?semester=2&academic_year=2568&search=${encodeURIComponent(sectionSearch)}`);
  if (!data) return; sectionsCache=data;
  document.getElementById('content').innerHTML=`
    <div class="search-row">
      <input class="form-control" id="sec-search" placeholder="🔍 ค้นหา..." value="${sectionSearch}" oninput="sectionSearch=this.value;loadSections()">
    </div>
    <div class="card"><div class="table-wrap"><table>
      <thead><tr><th>รหัสวิชา</th><th>ตอน</th><th>ชื่อวิชา</th><th>อาจารย์</th><th>นศ.</th><th>วันสอบ</th><th>เวลา</th><th>ห้อง</th><th>แผ่น</th><th>สถานะ</th><th></th></tr></thead>
      <tbody>${data.map(s=>`<tr>
        <td class="td-mono">${s.course?.course_id||'—'}</td>
        <td>${s.section_no}</td>
        <td>${s.course?.course_name_th||'—'}</td>
        <td>${s.teacher?.full_name||'<span style="color:var(--text-muted)">—</span>'}</td>
        <td>${s.num_students}</td>
        <td>${s.schedule?.exam_date||'<span style="color:var(--text-muted)">ยังไม่จัด</span>'}</td>
        <td>${s.schedule?.exam_time||'—'}</td>
        <td>${s.schedule?.room?.room_name||'—'}</td>
        <td>${s.schedule?`<span class="badge badge-red">${s.schedule.total_sheets}</span>`:'—'}</td>
        <td><span class="badge ${s.schedule?.status==='published'?'badge-green':'badge-gray'}">${s.schedule?.status||'ยังไม่จัด'}</span></td>
        <td><button class="btn btn-ghost btn-icon btn-sm" onclick="openEditSectionModal(${s.id})">✏️</button></td>
      </tr>`).join()||'<tr><td colspan="11" style="text-align:center;padding:40px;color:var(--text-muted)">ไม่พบข้อมูล</td></tr>'}
      </tbody>
    </table></div></div>`;
}
async function openAddSectionModal(){
  const [courses,teachers]=await Promise.all([get('/courses/'),get('/users/teachers')]);
  openModal('➕ เพิ่ม Section',`
    <div class="form-row" style="margin-bottom:12px">
      <div class="form-group"><label>รายวิชา *</label><select class="form-control" id="ns-course"><option value="">— เลือก —</option>${(courses||[]).map(c=>`<option value="${c.id}">${c.course_id} — ${c.course_name_th}</option>`).join('')}</select></div>
      <div class="form-group"><label>ตอน *</label><input class="form-control" id="ns-sec" placeholder="1, 801"></div>
    </div>
    <div class="form-row">
      <div class="form-group"><label>อาจารย์</label><select class="form-control" id="ns-teacher"><option value="">—</option>${(teachers||[]).map(t=>`<option value="${t.id}">${t.full_name}</option>`).join('')}</select></div>
      <div class="form-group"><label>จำนวน นศ.</label><input class="form-control" id="ns-n" type="number" value="0"></div>
    </div>
  `,[{label:'บันทึก',cls:'btn-primary',action:async()=>{try{await post('/courses/sections',{course_id:parseInt(document.getElementById('ns-course').value),section_no:document.getElementById('ns-sec').value,teacher_id:parseInt(document.getElementById('ns-teacher').value)||null,num_students:parseInt(document.getElementById('ns-n').value)||0,semester:'2',academic_year:'2568'});closeModal();toast('เพิ่มสำเร็จ ✅','success');loadSections();}catch(e){toast(e.message,'error');}}}]);
}
async function openEditSectionModal(id){
  const s=sectionsCache.find(x=>x.id===id);
  const teachers=await get('/users/teachers');
  openModal('✏️ แก้ไข Section',`
    <div class="form-group" style="margin-bottom:12px"><label>วิชา</label><div class="form-control" style="background:var(--surface2)">${s.course?.course_id} — ${s.course?.course_name_th}</div></div>
    <div class="form-row">
      <div class="form-group"><label>อาจารย์</label><select class="form-control" id="es-t"><option value="">—</option>${(teachers||[]).map(t=>`<option value="${t.id}" ${t.id===s.teacher?.id?'selected':''}>${t.full_name}</option>`).join('')}</select></div>
      <div class="form-group"><label>จำนวน นศ.</label><input class="form-control" id="es-n" type="number" value="${s.num_students}"></div>
    </div>
  `,[
    {label:'บันทึก',cls:'btn-primary',action:async()=>{try{await put(`/courses/sections/${id}`,{teacher_id:parseInt(document.getElementById('es-t').value)||null,num_students:parseInt(document.getElementById('es-n').value)});closeModal();toast('บันทึกสำเร็จ ✅','success');loadSections();}catch(e){toast(e.message,'error');}}},
    {label:'🗑 ลบ',cls:'btn-danger',action:async()=>{if(!confirm('ยืนยันลบ?'))return;await del(`/courses/sections/${id}`);closeModal();toast('ลบแล้ว');loadSections();}},
  ]);
}

// ─────────────────────────────────────────
// COPY COUNT
// ─────────────────────────────────────────
async function loadCopyCount() {
  document.getElementById('topbar-actions').innerHTML='<button class="btn btn-outline btn-sm" onclick="exportSchedulePDF(\'final\')">⬇ Export PDF</button>';
  const data=await get('/schedule/copy-count');
  if (!data) return;
  document.getElementById('content').innerHTML=`
    <div class="copy-banner">
      <div><div class="val">${data.grand_total.toLocaleString()}</div><div class="lbl">แผ่นทั้งหมด (รวมแบบฟอร์ม)</div></div>
      <div><div class="val">฿${data.cost.toLocaleString('th',{minimumFractionDigits:2})}</div><div class="lbl">ประมาณค่าใช้จ่าย (0.50 บ./แผ่น)</div></div>
      <div><div class="val">${data.sections_count}</div><div class="lbl">จำนวน Sections</div></div>
    </div>
    <div class="card"><div class="card-head"><h3>รายละเอียด</h3><span class="badge badge-navy">ข้อสอบ ${data.subtotal_exam.toLocaleString()} + แบบฟอร์ม ${data.fraud_forms} = ${data.grand_total.toLocaleString()}</span></div>
    <div class="table-wrap"><table>
      <thead><tr><th>รหัสวิชา</th><th>ตอน</th><th>ชื่อวิชา</th><th>นศ.</th><th>หน้า</th><th>แผ่นรวม</th><th>วันสอบ</th><th>ห้อง</th></tr></thead>
      <tbody>
        ${data.rows.map(r=>`<tr><td class="td-mono">${r.course_id}</td><td>${r.section_no}</td><td>${r.course_name_th}</td><td>${r.num_students}</td><td>${r.num_pages}</td><td><span class="badge badge-red">${r.total_sheets.toLocaleString()}</span></td><td>${r.exam_date}</td><td>${r.room}</td></tr>`).join('')}
        <tr style="background:var(--gold-lt)"><td colspan="2" style="font-weight:700">แบบฟอร์มทุจริต</td><td>—</td><td>—</td><td>1</td><td><span class="badge badge-gold">150</span></td><td colspan="2">—</td></tr>
      </tbody>
    </table></div></div>
  `;
}

// ─────────────────────────────────────────
// STUDENT SEARCH
// ─────────────────────────────────────────
function loadStudentSearch() {
  document.getElementById('content').innerHTML=`
    <div style="max-width:560px;margin:0 auto">
      <div class="card" style="margin-bottom:16px">
        <div class="card-head"><h3>🎓 ค้นหาตารางสอบ</h3></div>
        <div class="card-body">
          <p style="font-size:13px;color:var(--text-muted);margin-bottom:14px">พิมพ์รหัสนักศึกษาเพื่อดูตารางสอบทุกวิชาที่ลงทะเบียน</p>
          <div style="display:flex;gap:10px">
            <input class="form-control" id="stu-id" placeholder="เช่น 650610001" style="font-size:15px;letter-spacing:1px" onkeydown="if(event.key==='Enter')searchStudent()">
            <button class="btn btn-primary" onclick="searchStudent()">🔍 ค้นหา</button>
          </div>
        </div>
      </div>
      <div id="stu-result"></div>
    </div>`;
  setTimeout(()=>document.getElementById('stu-id')?.focus(),100);
}
async function searchStudent() {
  const sid=document.getElementById('stu-id').value.trim();
  if (!sid) return;
  const res=document.getElementById('stu-result');
  res.innerHTML='<div style="text-align:center;padding:20px"><div class="loader"></div></div>';
  try {
    const data=await get('/public/schedule/'+encodeURIComponent(sid));
    if (!data) return;
    res.innerHTML=`
      <div class="card" style="margin-bottom:14px"><div class="card-body" style="display:flex;align-items:center;gap:14px">
        <div style="width:44px;height:44px;background:var(--crimson-lt);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:20px">🎓</div>
        <div>
          <div style="font-size:15px;font-weight:700">${esc(data.full_name)}</div>
          <div style="font-size:12px;color:var(--text-muted)">รหัส: ${esc(data.student_id)} · ${esc(data.major)}</div>
          <div style="font-size:11px;color:var(--text-muted)">${esc(data.faculty)} · ${esc(data.total_courses)} วิชา</div>
        </div>
      </div></div>
      <div class="card"><div class="card-head"><h3>📅 ตารางสอบ</h3></div>
      <div class="table-wrap"><table>
        <thead><tr><th>รหัสวิชา</th><th>ชื่อวิชา</th><th>ตอน</th><th>วันสอบ</th><th>เวลา</th><th>ห้อง</th></tr></thead>
        <tbody>${data.exams.map(e=>`<tr>
          <td class="td-mono" style="font-weight:700;color:var(--crimson)">${esc(e.course_id)}</td>
          <td>${esc(e.course_name)}</td><td>${esc(e.section_no)}</td>
          <td>${e.has_schedule?thDate(e.exam_date):'<span style="color:var(--text-muted)">ยังไม่กำหนด</span>'}</td>
          <td>${esc(e.exam_time)}</td><td>${esc(e.room)}</td>
        </tr>`).join()||'<tr><td colspan="6" style="text-align:center;padding:30px;color:var(--text-muted)">ไม่พบวิชาสอบในคณะนี้</td></tr>'}
        </tbody>
      </table></div></div>`;
  } catch(e) {
    res.innerHTML=`<div class="card"><div class="card-body" style="text-align:center;padding:30px">
      <div style="font-size:36px;margin-bottom:10px">😕</div>
      <p style="color:var(--crimson);font-weight:600">${e.message}</p>
      <p style="color:var(--text-muted);font-size:13px;margin-top:6px">กรุณาตรวจสอบรหัสนักศึกษาอีกครั้ง</p>
    </div></div>`;
  }
}

// ─────────────────────────────────────────
// SWAPS v2 — full workflow
// ─────────────────────────────────────────
let selectedTargetUser=null;
async function loadSwaps() {
  const [mySwaps, waiting]=await Promise.all([
    get('/swaps2/my').catch(()=>[]),
    get('/swaps2/waiting').catch(()=>[]),
  ]);
  const sb={pending:'badge-gold',accepted:'badge-green',rejected:'badge-red',cancelled:'badge-gray'};
  const st={pending:'รอตอบ',accepted:'ตกลงแล้ว',rejected:'ปฏิเสธ',cancelled:'ยกเลิก'};
  document.getElementById('topbar-actions').innerHTML='<button class="btn btn-primary btn-sm" onclick="openNewSwapModal()">➕ ขอสลับ</button>';
  document.getElementById('content').innerHTML=`
    ${waiting.length?`<div class="card" style="margin-bottom:16px;border-left:3px solid var(--gold)">
      <div class="card-head"><h3>🔔 รอการตอบรับจากคุณ</h3><span class="badge badge-gold">${waiting.length}</span></div>
      <div class="table-wrap"><table>
        <thead><tr><th>ผู้ขอ</th><th>กะที่เขาต้องแลก</th><th>กะของคุณ</th><th>ข้อความ</th><th></th></tr></thead>
        <tbody>${waiting.map(w=>`<tr>
          <td><strong>${w.requester_name}</strong></td>
          <td>${w.their_shift?.date||'—'} ${w.their_shift?.time||''}<br><small>${w.their_shift?.course||''}</small></td>
          <td>${w.my_shift?.date||'—'} ${w.my_shift?.time||''}<br><small>${w.my_shift?.course||''}</small></td>
          <td style="font-size:12px;color:var(--text-muted)">${w.message||'—'}</td>
          <td style="display:flex;gap:6px">
            <button class="btn btn-success btn-sm" onclick="respondSwapV2(${w.id},true)">✅</button>
            <button class="btn btn-danger btn-sm" onclick="respondSwapV2(${w.id},false)">✕</button>
          </td>
        </tr>`).join('')}</tbody>
      </table></div>
    </div>`:''}
    <div class="card">
      <div class="card-head"><h3>🔄 คำขอสลับของฉัน</h3></div>
      <div class="table-wrap"><table>
        <thead><tr><th>ฝ่าย</th><th>กะของฉัน</th><th>กะที่แลก</th><th>สถานะ</th><th></th></tr></thead>
        <tbody>${mySwaps.length?mySwaps.map(s=>`<tr>
          <td>${s.is_requester?`→ ${s.target_name}`:`← ${s.requester_name}`}</td>
          <td>${s.my_shift?.date||'—'}<br><small>${s.my_shift?.course||''}</small></td>
          <td>${s.their_shift?.date||'—'}<br><small>${s.their_shift?.course||''}</small></td>
          <td><span class="badge ${sb[s.status]||'badge-gray'}">${st[s.status]||s.status}</span></td>
          <td>${s.status==='pending'&&s.is_requester?`<button class="btn btn-ghost btn-sm" onclick="cancelSwapV2(${s.id})">ยกเลิก</button>`:''}</td>
        </tr>`).join(''):'<tr><td colspan="5" style="text-align:center;padding:40px;color:var(--text-muted)">ไม่มีคำขอสลับ</td></tr>'}
        </tbody>
      </table></div>
    </div>
    <p style="font-size:12px;color:var(--text-muted);margin-top:8px">กะที่ swap ↔ แสดงเป็นสีจางในตารางสอบ — ไม่กระทบ Baseline Stats</p>
  `;
}

async function openNewSwapModal() {
  const schData=await get('/schedule/');
  const myScheds=(schData||[]).filter(s=>isMySupervision(s.supervisions));
  selectedTargetUser=null;
  openModal('🔄 ขอสลับคุมสอบ',`
    <div class="form-group" style="margin-bottom:14px">
      <label>กะของฉันที่ต้องการสลับ *</label>
      <select class="form-control" id="my-sup-sel" style="margin-top:6px" onchange="loadAvailableForSwap()">
        <option value="">— เลือกกะของคุณ —</option>
        ${myScheds.map(s=>{
          const sup=(s.supervisions||[]).find(sv=>sv.user?.id===currentUser?.id);
          return sup?`<option value="${sup.id}">${s.exam_date} ${s.exam_time} — ${s.course?.course_id||''} Sec${s.section?.section_no||''}</option>`:'';
        }).join('')}
      </select>
    </div>
    <div class="form-group" style="margin-bottom:14px">
      <label>เลือกคนที่ต้องการขอสลับ * <small style="color:var(--text-muted)">(แสดงเฉพาะคนที่ว่างในเวลานั้น)</small></label>
      <div id="avail-list" style="margin-top:6px;max-height:180px;overflow-y:auto;border:1px solid var(--border);border-radius:var(--radius);padding:8px">
        <span style="color:var(--text-muted);font-size:13px">เลือกกะของคุณก่อน</span>
      </div>
    </div>
    <div class="form-group">
      <label>ข้อความถึงผู้รับ</label>
      <input class="form-control" id="swap-msg" placeholder="เหตุผล..." style="margin-top:6px">
    </div>
  `,[{label:'ส่งคำขอ',cls:'btn-primary',action:submitSwapV2}]);
}
async function loadAvailableForSwap() {
  const supId=document.getElementById('my-sup-sel')?.value;
  if (!supId) return;
  selectedTargetUser=null;
  const el=document.getElementById('avail-list');
  el.innerHTML='<span style="color:var(--text-muted)">กำลังโหลด...</span>';
  try {
    const users=await get('/swaps2/available-users/'+supId);
    if (!users?.length){el.innerHTML='<span style="color:var(--text-muted)">ไม่พบผู้ที่ว่างในเวลานั้น</span>';return;}
    el.innerHTML=users.map(u=>`
      <div onclick="pickSwapUser(${parseInt(u.id)||0},this)" style="padding:8px 10px;cursor:pointer;border-radius:6px;border:1.5px solid transparent;display:flex;align-items:center;gap:8px;margin-bottom:3px">
        <div style="flex:1"><strong>${esc(u.full_name)}</strong></div>
        <span class="badge badge-gray" style="font-size:10px">${esc(u.role)}</span>
      </div>`).join('');
  } catch(e){el.innerHTML=`<span style="color:var(--crimson)">${esc(e.message)}</span>`;}
}
function pickSwapUser(id,el){
  selectedTargetUser=id;
  document.querySelectorAll('#avail-list div').forEach(x=>{x.style.background='';x.style.borderColor='transparent';});
  el.style.background='var(--crimson-lt)';el.style.borderColor='var(--crimson)';
}
async function submitSwapV2(){
  const supId=document.getElementById('my-sup-sel')?.value;
  if(!supId) return toast('กรุณาเลือกกะของคุณ','error');
  if(!selectedTargetUser) return toast('กรุณาเลือกคนที่ต้องการขอสลับ','error');
  const msg=document.getElementById('swap-msg')?.value;
  try{await post('/swaps2/',{my_supervision_id:parseInt(supId),target_user_id:selectedTargetUser,message:msg||null});toast('ส่งคำขอแล้ว ✅','success');closeModal();loadSwaps();}
  catch(e){toast(e.message,'error');}
}
async function respondSwapV2(id,accept){
  const reason=accept?null:prompt('เหตุผลที่ปฏิเสธ:');
  if(!accept&&!reason) return;
  try{await post(`/swaps2/${id}/respond`,{accept,reason});toast(accept?'ยอมรับแล้ว ✅':'ปฏิเสธแล้ว',accept?'success':'');loadSwaps();}
  catch(e){toast(e.message,'error');}
}
async function cancelSwapV2(id){
  if(!confirm('ยืนยันยกเลิก?')) return;
  try{await del('/swaps/'+id);toast('ยกเลิกแล้ว');loadSwaps();}catch(e){toast(e.message,'error');}
}

// ─────────────────────────────────────────
// CHECK-IN (2 ครั้ง)
// ─────────────────────────────────────────
async function loadCheckins(){
  const schData=await get('/schedule/');
  if(!schData) return;
  document.getElementById('content').innerHTML=`
    <div class="card">
      <div class="card-head"><h3>ตารางสอบที่ต้องดูแล</h3></div>
      <div class="table-wrap"><table>
        <thead><tr><th>วิชา</th><th>ตอน</th><th>วันที่</th><th>เวลา</th><th>ห้อง</th><th>Check-in</th></tr></thead>
        <tbody>${(schData||[]).slice(0,20).map(s=>`<tr>
          <td>${s.section?.course?.course_name_th||'—'}</td>
          <td>${s.section?.section_no||'—'}</td>
          <td>${s.exam_date||'—'}</td>
          <td>${s.exam_time||'—'}</td>
          <td>${s.room?.room_name||'—'}</td>
          <td style="display:flex;gap:6px">
            <button class="btn btn-outline btn-sm" onclick="openCheckin(${s.id},'receive_papers')">📦 รับข้อสอบ</button>
            <button class="btn btn-primary btn-sm" onclick="openCheckin(${s.id},'at_room')">📍 Check-in ห้อง</button>
          </td>
        </tr>`).join('')}</tbody>
      </table></div>
    </div>`;
}
async function openCheckin(scheduleId, type){
  const events=await get(`/checkins/schedule/${scheduleId}`).catch(()=>[]);
  const myEvent=events.find(e=>e.user===currentUser?.full_name&&e.checkin_type===type);
  const typeLabel={receive_papers:'📦 รับข้อสอบ',at_room:'📍 Check-in ห้องสอบ'}[type];
  const teachers=await get('/users/teachers').catch(()=>[]);
  const allStaff=await get('/users/').catch(()=>[]);

  openModal(`${typeLabel}`,`
    ${myEvent?`<div style="background:var(--green-lt);border-radius:6px;padding:10px;margin-bottom:14px;font-size:13px;color:var(--green)">✅ คุณ check-in ประเภทนี้แล้ว — ${new Date(myEvent.checked_in_at).toLocaleString('th-TH')}</div>`:''}
    ${type==='at_room'?`
    <div class="form-row" style="margin-bottom:12px">
      <div class="form-group"><label>นักศึกษาเข้าสอบ</label><input class="form-control" id="ci-present" type="number" min="0" placeholder="0"></div>
      <div class="form-group"><label>เข้าสาย</label><input class="form-control" id="ci-late" type="number" min="0" value="0"></div>
    </div>`:''}
    <div class="form-group" style="margin-bottom:12px">
      <label>📍 GPS Location <small style="color:var(--text-muted)">(จะเพิ่ม 3D coordinates ภายหลัง)</small></label>
      <div style="background:var(--surface2);border:1px solid var(--border);border-radius:var(--radius);padding:10px;font-size:12px;color:var(--text-muted)" id="gps-display">
        กำลังรับ GPS... <button class="btn btn-ghost btn-sm" onclick="getGPS()">รับ GPS</button>
      </div>
    </div>
    <div class="form-group" style="margin-bottom:12px">
      <label>หมายเหตุ</label>
      <input class="form-control" id="ci-notes" placeholder="หมายเหตุ (ถ้ามี)">
    </div>
    <hr style="margin-bottom:12px">
    <div class="form-group">
      <label>🚨 คนแทนฉุกเฉิน (ถ้ามี)</label>
      <select class="form-control" id="ci-emerg" style="margin-top:6px">
        <option value="">— ไม่มีคนแทน —</option>
        ${(allStaff||[]).filter(u=>u.role==='staff'||u.role==='teacher').map(u=>`<option value="${u.id}">${u.full_name}</option>`).join('')}
      </select>
    </div>
    ${events.length?`<div style="margin-top:14px"><p style="font-size:12px;font-weight:600;color:var(--text-mid);margin-bottom:8px">สถานะ Check-in:</p>
      ${events.map(e=>`<div style="display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid var(--border);font-size:12px">
        <span>${e.user} — ${e.checkin_type==='receive_papers'?'📦 รับข้อสอบ':'📍 ห้องสอบ'}</span>
        <span class="badge ${e.confirmed_by_all?'badge-green':'badge-gray'}">${e.confirmed_by_all?'ยืนยันครบ':'รอยืนยัน'}</span>
      </div>`).join('')}
    </div>`:''}
  `,[{label:`บันทึก ${typeLabel}`,cls:'btn-primary',action:async()=>{
    const emergId=document.getElementById('ci-emerg')?.value;
    try{
      const r=await post('/checkins/',{
        schedule_id:scheduleId,checkin_type:type,
        students_present:type==='at_room'?parseInt(document.getElementById('ci-present')?.value)||null:null,
        late_count:type==='at_room'?parseInt(document.getElementById('ci-late')?.value)||0:0,
        notes:document.getElementById('ci-notes')?.value||null,
      });
      if(emergId){
        await post('/swaps2/emergency-sub',{schedule_id:scheduleId,substitute_user_id:parseInt(emergId)}).catch(()=>{});
      }
      toast(`${typeLabel} สำเร็จ ✅`,'success');closeModal();
    }catch(e){toast(e.message,'error');}
  }}]);
}
function getGPS(){
  navigator.geolocation?.getCurrentPosition(p=>{
    document.getElementById('gps-display').textContent=`📍 ${p.coords.latitude.toFixed(6)}, ${p.coords.longitude.toFixed(6)} (±${p.coords.accuracy.toFixed(0)}m)`;
  },err=>{document.getElementById('gps-display').textContent='ไม่สามารถรับ GPS ได้';});
}

// ─────────────────────────────────────────
// SUBMISSIONS
// ─────────────────────────────────────────
async function loadSubmissions(){
  const data=await get('/submissions/').catch(()=>[]);
  const sb={draft:'badge-gray',submitted:'badge-gold',approved:'badge-green',rejected:'badge-red',released:'badge-navy'};
  const st={draft:'ฉบับร่าง',submitted:'รอตรวจสอบ',approved:'อนุมัติแล้ว',rejected:'ปฏิเสธ',released:'Release แล้ว'};
  document.getElementById('content').innerHTML=`
    <div class="card"><div class="table-wrap"><table>
      <thead><tr><th>รหัสวิชา</th><th>ชื่อวิชา</th><th>ตอน</th><th>ประเภทสอบ</th><th>สถานะ</th><th>ส่งเมื่อ</th><th></th></tr></thead>
      <tbody>${data.length?data.map(s=>`<tr>
        <td class="td-mono">${esc(s.course_id)}</td><td>${esc(s.course_name)}</td><td>${esc(s.section_no)}</td>
        <td>${esc(s.exam_type_choice)}</td>
        <td><span class="badge ${sb[s.status]||'badge-gray'}">${esc(st[s.status]||s.status)}</span></td>
        <td>${s.submitted_at?new Date(s.submitted_at).toLocaleDateString('th-TH'):'—'}</td>
        <td><button class="btn btn-outline btn-sm" onclick="openSubmissionWizard(${parseInt(s.section_id)||0})">จัดการ</button></td>
      </tr>`).join(''):'<tr><td colspan="7" style="text-align:center;padding:40px;color:var(--text-muted)">ยังไม่มีข้อสอบ</td></tr>'}
      </tbody>
    </table></div></div>
    ${currentUser?.role==='admin'?`<div class="card" style="margin-top:16px"><div class="card-head"><h3>Admin — รออนุมัติ</h3><button class="btn btn-outline btn-sm" onclick="loadPendingList()">โหลด</button></div><div id="pending-list"></div></div>`:''}
  `;
}
async function loadPendingList(){
  const data=await get('/submissions/?status=submitted').catch(()=>[]);
  document.getElementById('pending-list').innerHTML=`<div class="table-wrap"><table><thead><tr><th>วิชา</th><th>ผู้ส่ง</th><th>ส่งเมื่อ</th><th></th></tr></thead><tbody>
    ${data.map(s=>`<tr><td>${esc(s.course_id)} Sec${esc(s.section_no)}</td><td>${esc(s.submitter)}</td><td>${s.submitted_at?new Date(s.submitted_at).toLocaleDateString('th-TH'):'—'}</td>
    <td style="display:flex;gap:6px"><button class="btn btn-success btn-sm" onclick="approveSubm(${parseInt(s.id)||0},true)">✅ อนุมัติ</button><button class="btn btn-danger btn-sm" onclick="approveSubm(${parseInt(s.id)||0},false)">✕</button></td></tr>`).join('')}
  </tbody></table></div>`;
}
async function approveSubm(id,approve){
  const reason=approve?null:prompt('เหตุผล:');
  if(!approve&&!reason) return;
  try{await post('/submissions/approve',{submission_id:id,approve,reason});toast(approve?'อนุมัติแล้ว ✅':'ปฏิเสธแล้ว',approve?'success':'error');loadSubmissions();}
  catch(e){toast(e.message,'error');}
}
async function openSubmissionWizard(sid){
  const data=await get(`/submissions/section/${sid}`).catch(()=>({exists:false,section_id:sid}));
  const isLocked=data.status==='approved'||data.status==='released';
  const st={draft:'ฉบับร่าง',submitted:'รอตรวจสอบ',approved:'อนุมัติแล้ว',rejected:'ปฏิเสธ',released:'Release'};
  const step=!data.exists||!data.date_confirmed?1:!data.exam_type_choice?2:3;
  openModal(`📋 ${data.course_name||'ข้อสอบ'}`,`
    <div style="display:flex;gap:6px;margin-bottom:16px">${[1,2,3].map(n=>`<div style="flex:1;height:4px;border-radius:2px;background:${n<=step?'var(--crimson)':'var(--border)'}"></div>`).join('')}</div>
    ${isLocked?`<div style="background:var(--green-lt);border-radius:6px;padding:10px;margin-bottom:12px;font-size:13px;color:var(--green)">สถานะ: ${st[data.status]} — ติดต่อ Admin เพื่อแก้ไข</div>`:''}
    ${data.rejected_reason?`<div style="background:var(--crimson-lt);border-radius:6px;padding:10px;margin-bottom:12px;font-size:13px;color:var(--crimson)">⚠️ ${data.rejected_reason}</div>`:''}
    <div class="form-group" style="margin-bottom:12px">
      <label>ขั้น 1 — ยืนยันวันสอบ</label>
      <div style="display:flex;align-items:center;gap:10px;margin-top:6px">
        <span class="badge ${data.date_confirmed?'badge-green':'badge-gray'}">${data.date_confirmed?'✅ ยืนยันแล้ว':'ยังไม่ยืนยัน'}</span>
        ${!data.date_confirmed&&!isLocked?`<button class="btn btn-primary btn-sm" onclick="step1(${sid})">ยืนยัน</button>`:''}
      </div>
    </div>
    <div class="form-group" style="margin-bottom:12px">
      <label>ขั้น 2 — ประเภทการสอบ</label>
      ${data.date_confirmed&&!isLocked?`
        <select class="form-control" id="exam-type-s" style="margin-top:6px">
          <option value="">— เลือก —</option>
          ${['no_exam','online','onsite','outside_sched','in_class'].map(v=>`<option value="${v}" ${data.exam_type_choice===v?'selected':''}>${v}</option>`).join('')}
        </select>
        <button class="btn btn-outline btn-sm" style="margin-top:6px" onclick="step2(${sid})">บันทึก</button>
      `:`<div class="form-control" style="background:var(--surface2);margin-top:6px">${data.exam_type_choice||'ยังไม่เลือก'}</div>`}
    </div>
    <div class="form-group">
      <label>ขั้น 3 — ไฟล์ข้อสอบ</label>
      ${data.exam_type_choice==='onsite'&&!isLocked?`
        <div style="margin-top:6px">
          <label style="display:flex;align-items:center;gap:8px;font-size:13px;cursor:pointer;margin-bottom:8px">
            <input type="checkbox" id="no-cover"> ยืนยัน: ไฟล์ PDF ไม่มีหน้าปก
          </label>
          <input type="file" id="pdf-file" accept=".pdf" class="form-control" style="margin-bottom:8px">
          <button class="btn btn-outline btn-sm" onclick="step3Upload(${sid})">อัปโหลด PDF</button>
        </div>
      `:`<span class="badge ${data.has_uploaded_pdf?'badge-green':data.exam_type_choice!=='onsite'?'badge-gray':'badge-gray'}" style="margin-top:6px;display:inline-block">${data.has_uploaded_pdf?'✅ มีไฟล์':data.exam_type_choice!=='onsite'?'ไม่จำเป็น':'ยังไม่มีไฟล์'}</span>`}
    </div>
  `,[
    !isLocked&&data.date_confirmed&&data.exam_type_choice?{label:'📤 ส่งข้อสอบ',cls:'btn-primary',action:()=>submitExam(sid)}:null,
    data.status==='approved'&&currentUser?.role==='admin'?{label:'🖨️ Release Printshop',cls:'btn-gold',action:()=>releaseExam(data.id)}:null,
  ].filter(Boolean));
}
async function step1(sid){try{await post('/submissions/step1-confirm',{section_id:sid});toast('ยืนยันแล้ว ✅','success');closeModal();openSubmissionWizard(sid);}catch(e){toast(e.message,'error');}}
async function step2(sid){const t=document.getElementById('exam-type-s')?.value;if(!t)return toast('เลือกประเภทก่อน','error');try{await post('/submissions/step2-exam-type',{section_id:sid,exam_type_choice:t});toast('บันทึกแล้ว ✅','success');closeModal();openSubmissionWizard(sid);}catch(e){toast(e.message,'error');}}
async function step3Upload(sid){
  const f=document.getElementById('pdf-file');
  if(!f?.files?.[0]) return toast('เลือกไฟล์ก่อน','error');
  if(!document.getElementById('no-cover')?.checked) return toast('ยืนยันว่าไม่มีหน้าปก','error');
  const form=new FormData();form.append('file',f.files[0]);
  try{const r=await fetch(`/api/submissions/step3-upload/${sid}?no_cover_page_confirmed=true`,{method:'POST',headers:{'Authorization':`Bearer ${token}`},body:form});const d=await r.json();if(!r.ok)throw new Error(d.detail);toast('อัปโหลดสำเร็จ ✅','success');closeModal();openSubmissionWizard(sid);}catch(e){toast(e.message,'error');}
}
async function submitExam(sid){if(!confirm('ยืนยันส่งข้อสอบ?'))return;try{await post('/submissions/submit',{section_id:sid});toast('ส่งแล้ว — รอ Admin ✅','success');closeModal();loadSubmissions();}catch(e){toast(e.message,'error');}}
async function releaseExam(subId){try{const d=await post(`/submissions/${subId}/release`,{});openModal('🖨️ Release สำเร็จ',`<div style="text-align:center;padding:10px 0"><div style="font-size:36px;margin-bottom:10px">✅</div><p style="font-size:13px;color:var(--text-muted);margin-bottom:10px">Token Printshop</p><div class="form-control td-mono" style="word-break:break-all;font-size:11px;background:var(--surface2)">${d.printshop_token}</div><p style="font-size:11px;color:var(--text-muted);margin-top:6px">หมดอายุ: ${d.expires_in}</p></div>`,[]);}catch(e){toast(e.message,'error');}}

// ─────────────────────────────────────────
// OPTIMIZER
// ─────────────────────────────────────────
function loadOptimizer(){
  document.getElementById('content').innerHTML=`
    <div class="optimizer-box">
      <h3>⚙️ CP-SAT Optimizer</h3>
      <p>จัดตารางสอบอัตโนมัติด้วย OR-Tools CP-SAT Solver</p>
      <div style="display:flex;gap:12px;align-items:center">
        <select class="form-control" id="opt-sem" style="width:120px;background:rgba(255,255,255,.1);border-color:rgba(255,255,255,.2);color:#fff"><option value="2">ภาค 2</option><option value="1">ภาค 1</option></select>
        <input class="form-control" id="opt-year" value="2568" style="width:100px;background:rgba(255,255,255,.1);border-color:rgba(255,255,255,.2);color:#fff">
        <button class="btn btn-primary" id="opt-btn" onclick="runOptimizer()">🚀 Run Optimizer</button>
        <button class="btn" style="background:rgba(255,255,255,.1);color:#fff" onclick="lockBaseline()">🔒 Lock Baseline</button>
      </div>
      <div id="opt-result"></div>
    </div>
    <div class="card"><div class="card-head"><h3>ℹ️ เกี่ยวกับ Optimizer</h3></div>
    <div class="card-body"><p style="font-size:13px;color:var(--text-mid);line-height:1.8">
      <strong>Algorithm:</strong> CP-SAT + Greedy fallback<br>
      <strong>Hard Constraints:</strong> ความจุห้อง, ไม่ซ้อนเวลา, อาจารย์ไม่คุมซ้อน<br>
      <strong>Soft Objective:</strong> Minimize fairness gap กรรมการ<br>
      <strong>ติดตั้ง OR-Tools:</strong> <code>pip install ortools</code><br>
      <strong>หลัง Run เสร็จ:</strong> กด Lock Baseline เพื่อเก็บสถิติ
    </p></div></div>`;
}
async function runOptimizer(){
  const btn=document.getElementById('opt-btn');
  const res=document.getElementById('opt-result');
  btn.disabled=true;btn.innerHTML='⏳ กำลังคำนวณ...';
  try{const data=await post('/schedule/optimize',{semester:document.getElementById('opt-sem').value,academic_year:document.getElementById('opt-year').value,exam_type:'final'});
    res.innerHTML=`<div class="opt-result"><div style="font-weight:700;margin-bottom:10px;color:#fff">✅ เสร็จแล้ว</div>
    <div class="opt-grid"><div class="opt-stat"><div class="val">${parseInt(data.sections_assigned)||0}</div><div class="lbl">จัดแล้ว</div></div>
    <div class="opt-stat"><div class="val">${parseInt(data.sections_total)||0}</div><div class="lbl">ทั้งหมด</div></div>
    <div class="opt-stat"><div class="val">${parseFloat(data.fairness_score||0).toFixed(2)}</div><div class="lbl">Fairness SD</div></div></div>
    ${data.violations?.length?`<div style="margin-top:10px;font-size:12px;color:rgba(255,200,0,.8)">⚠️ ${data.violations.map(v=>esc(v)).join('<br>')}</div>`:''}
    </div>`;
    toast('Optimizer เสร็จแล้ว ✅','success');loadSchedule();
  }catch(e){res.innerHTML=`<div class="opt-result">${esc(e.message)}</div>`;toast(e.message,'error');}
  btn.disabled=false;btn.innerHTML='🚀 Run Optimizer';
}
async function lockBaseline(){
  if(!confirm('ยืนยัน Lock Baseline? จะ reset สถิติเดิม')) return;
  try{const d=await post('/swaps2/admin/lock-baseline',{});toast(`Lock แล้ว — ${d.baseline_count} รายการ ✅`,'success');}
  catch(e){toast(e.message,'error');}
}

// ─────────────────────────────────────────
// USERS
// ─────────────────────────────────────────
async function loadUsers(){
  document.getElementById('topbar-actions').innerHTML='<button class="btn btn-primary btn-sm" onclick="openAddUserModal()">➕ เพิ่มผู้ใช้</button>';
  const data=await get('/users/');
  if(!data) return;
  const rb={admin:'badge-red',staff:'badge-navy',teacher:'badge-green',student:'badge-gray'};
  const rl={admin:'Admin',staff:'เจ้าหน้าที่',teacher:'อาจารย์',student:'นักศึกษา'};
  document.getElementById('content').innerHTML=`<div class="card"><div class="table-wrap"><table>
    <thead><tr><th>ชื่อผู้ใช้</th><th>ชื่อ-สกุล</th><th>อีเมล</th><th>Role</th><th>สังกัด</th><th>สถานะ</th><th></th></tr></thead>
    <tbody>${data.map(u=>`<tr>
      <td class="td-mono">${esc(u.username)}</td>
      <td><strong>${esc(u.full_name)}</strong></td>
      <td style="color:var(--text-muted)">${esc(u.email)}</td>
      <td><span class="badge ${rb[u.role]||'badge-gray'}">${esc(rl[u.role]||u.role)}</span></td>
      <td>${esc(u.department)}</td>
      <td><span class="badge ${u.is_active?'badge-green':'badge-gray'}">${u.is_active?'ใช้งาน':'ปิดใช้'}</span></td>
      <td>${u.username!=='admin'?`<button class="btn btn-danger btn-icon btn-sm" onclick="deactivateUser(${parseInt(u.id)||0})">🚫</button>`:''}
      </td>
    </tr>`).join('')}</tbody>
  </table></div></div>`;
}
async function openAddUserModal(){
  openModal('➕ เพิ่มผู้ใช้',`
    <div class="form-row" style="margin-bottom:12px">
      <div class="form-group"><label>ชื่อผู้ใช้ *</label><input class="form-control" id="nu-u" placeholder="username"></div>
      <div class="form-group"><label>รหัสผ่าน *</label><input class="form-control" id="nu-p" type="password"></div>
    </div>
    <div class="form-row" style="margin-bottom:12px">
      <div class="form-group"><label>ชื่อ-นามสกุล</label><input class="form-control" id="nu-n"></div>
      <div class="form-group"><label>อีเมล *</label><input class="form-control" id="nu-e" type="email" placeholder="xxx@pol.cmu.ac.th"></div>
    </div>
    <div class="form-row">
      <div class="form-group"><label>Role</label><select class="form-control" id="nu-r"><option value="staff">เจ้าหน้าที่</option><option value="teacher">อาจารย์</option><option value="admin">Admin</option></select></div>
      <div class="form-group"><label>สังกัด</label><input class="form-control" id="nu-d" placeholder="คณะ/ภาควิชา"></div>
    </div>
  `,[{label:'บันทึก',cls:'btn-primary',action:async()=>{
    try{await post('/users/',{username:document.getElementById('nu-u').value,password:document.getElementById('nu-p').value,full_name:document.getElementById('nu-n').value,email:document.getElementById('nu-e').value,role:document.getElementById('nu-r').value,department:document.getElementById('nu-d').value});closeModal();toast('เพิ่มสำเร็จ ✅','success');loadUsers();}catch(e){toast(e.message,'error');}
  }}]);
}
async function deactivateUser(id){
  // Note: confirm() text is static — no user data interpolated (XSS safe)
  if(!confirm('ยืนยันปิดใช้งานผู้ใช้นี้?')) return;
  try{await del(`/users/${id}`);toast('ปิดใช้งานแล้ว','success');loadUsers();}catch(e){toast(e.message,'error');}
}

// ─────────────────────────────────────────
// SETTINGS (Admin)
// ─────────────────────────────────────────
async function loadSettings(){
  const data=await get('/settings/');
  if(!data) return;
  const labels={
    exam_submission_deadline:'📅 Deadline ส่งข้อสอบ (ISO: 2025-04-01T17:00:00)',
    swap_request_deadline:'📅 Deadline ขอสลับ',
    swap_enabled:'🔄 เปิดระบบสลับ (true/false)',
    current_semester:'📚 ภาคการศึกษา',
    current_academic_year:'📅 ปีการศึกษา (พ.ศ.)',
    printshop_copies_buffer:'🖨️ Buffer สำเนา %',
  };
  document.getElementById('content').innerHTML=`
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px">
      <div>
        <div class="card" style="margin-bottom:16px">
          <div class="card-head"><h3>⚙️ ตั้งค่าระบบ</h3></div>
          <div class="card-body">
            ${Object.entries(data).map(([k,v])=>`<div class="form-group" style="margin-bottom:14px">
              <label style="font-size:12px">${labels[k]||k}</label>
              <div style="display:flex;gap:8px;margin-top:4px">
                <input class="form-control" id="setting-${k}" value="${v.value||''}" style="flex:1">
                <button class="btn btn-outline btn-sm" onclick="saveSetting('${k}')">บันทึก</button>
              </div>
              ${v.updated_at?`<div style="font-size:10px;color:var(--text-muted);margin-top:2px">อัปเดต: ${new Date(v.updated_at).toLocaleString('th-TH')}</div>`:''}
            </div>`).join('')}
          </div>
        </div>
        <div class="card">
          <div class="card-head"><h3>📊 Baseline Stats</h3></div>
          <div class="card-body">
            <p style="font-size:13px;color:var(--text-muted);margin-bottom:12px">Lock หลัง Optimizer + Admin confirm<br>เพื่อเก็บสถิติระยะยาว (ไม่เปลี่ยนแม้มี swap)</p>
            <button class="btn btn-primary btn-sm" onclick="lockBaseline()">🔒 Lock Baseline ตอนนี้</button>
          </div>
        </div>
      </div>
      <div>
        <div class="card" style="margin-bottom:16px">
          <div class="card-head"><h3>📄 Export PDF</h3></div>
          <div class="card-body" style="display:flex;flex-direction:column;gap:10px">
            <button class="btn btn-outline btn-sm" onclick="exportSchedulePDF('final')">⬇ ตารางสอบปลายภาค (PDF)</button>
            <button class="btn btn-outline btn-sm" onclick="exportSchedulePDF('midterm')">⬇ ตารางสอบกลางภาค (PDF)</button>
          </div>
        </div>
        <div class="card" style="margin-bottom:16px">
          <div class="card-head"><h3>📥 นำเข้าข้อมูล</h3></div>
          <div class="card-body">
            <p style="font-size:13px;color:var(--text-muted);margin-bottom:10px">วางไฟล์ใน <code>backend/data/</code> แล้วรันใน Terminal</p>
            <code style="font-size:12px;display:block;background:var(--surface2);padding:8px;border-radius:6px">python import_data.py</code>
          </div>
        </div>
        <div class="card">
          <div class="card-head"><h3>👥 Section Coordinators (4 คน)</h3></div>
          <div class="card-body">
            <p style="font-size:13px;color:var(--text-muted)">4 staff ที่ดูแลอาจารย์ตามสาขา — เห็นข้อสอบอาจารย์ได้</p>
            <p style="font-size:12px;color:var(--text-muted);margin-top:8px">กำหนดได้ผ่าน DB โดยตรง หรือผ่าน <code>/admin/coordinators</code></p>
          </div>
        </div>
      </div>
    </div>`;
}
async function saveSetting(key){
  const val=document.getElementById(`setting-${key}`)?.value;
  try{await fetch(`/api/settings/${key}?value=${encodeURIComponent(val)}`,{method:'PUT',headers:{'Authorization':`Bearer ${token}`}});toast(`บันทึก ${key} ✅`,'success');}
  catch(e){toast(e.message,'error');}
}

// ─────────────────────────────────────────
// MODAL & TOAST
// ─────────────────────────────────────────
function openModal(title,bodyHTML,actions=[]){
  document.getElementById('modal-title').textContent=title;
  document.getElementById('modal-body').innerHTML=bodyHTML;
  document.getElementById('modal-foot').innerHTML=`
    <button class="btn btn-ghost" onclick="closeModal()">ยกเลิก</button>
    ${actions.map((a,i)=>`<button class="btn ${a.cls}" id="ma-${i}">${a.label}</button>`).join('')}`;
  actions.forEach((a,i)=>document.getElementById(`ma-${i}`).addEventListener('click',a.action));
  document.getElementById('modal-overlay').classList.add('show');
}
function closeModal(){document.getElementById('modal-overlay').classList.remove('show');}
document.getElementById('modal-overlay').addEventListener('click',e=>{if(e.target===document.getElementById('modal-overlay'))closeModal();});

let toastTimer;
function toast(msg,type=''){
  const el=document.getElementById('toast');
  el.textContent=msg;el.className=`toast show ${type}`;
  clearTimeout(toastTimer);toastTimer=setTimeout(()=>el.classList.remove('show'),3500);
}

// ─────────────────────────────────────────
// BOOT
// ─────────────────────────────────────────
if (token) initApp();
