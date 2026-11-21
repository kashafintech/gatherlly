const API = "/api/v1";
const state = {token: sessionStorage.getItem("gatherly_token"), user: null, events: [], registrations: [], activeEvent: null};
const $ = (selector, scope=document) => scope.querySelector(selector);
const $$ = (selector, scope=document) => [...scope.querySelectorAll(selector)];
const escapeHTML = value => String(value ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const dateValue = value => new Date(value);
const dateText = value => dateValue(value).toLocaleString([], {month:"short",day:"numeric",year:"numeric",hour:"numeric",minute:"2-digit"});
const initials = name => (name || "U").split(/\s+/).slice(0,2).map(x=>x[0]).join("").toUpperCase();
let toastTimer;

function notify(message, error=false) {
  const el=$("#toast"); el.textContent=message; el.classList.toggle("error",error); el.classList.add("show");
  clearTimeout(toastTimer); toastTimer=setTimeout(()=>el.classList.remove("show"),3600);
}
async function api(path, options={}) {
  const headers={"Content-Type":"application/json", ...(options.headers||{})};
  if(state.token) headers.Authorization=`Bearer ${state.token}`;
  let response;
  try { response=await fetch(`${API}${path}`, {...options,headers}); }
  catch { throw new Error("Cannot reach the API. Check your deployment and database configuration."); }
  if(response.status===204) return null;
  const data=await response.json().catch(()=>({}));
  if(!response.ok) {
    const detail=data.detail;
    const message=Array.isArray(detail) ? detail.map(x=>x.msg).join(", ") : (detail || `Request failed (${response.status})`);
    if(response.status===401 && state.token) logout(false);
    throw new Error(message);
  }
  return data;
}
function setAuthTab(tab) {
  const register=tab==="register";
  $("#login-form").classList.toggle("hidden",register);
  $("#register-form").classList.toggle("hidden",!register);
  $$("[data-auth-tab]").forEach(b=>b.classList.toggle("active",b.dataset.authTab===tab));
  $("#auth-eyebrow").textContent=register?"GET STARTED":"WELCOME BACK";
  $("#auth-title").textContent=register?"Create your company workspace":"Sign in to your workspace";
  $("#auth-subtitle").textContent=register?"Set up your organization and administrator account.":"Enter your organization details to continue.";
}
function showAuth() { $("#auth-view").classList.remove("hidden"); $("#app-view").classList.add("hidden"); }
function showApp() { $("#auth-view").classList.add("hidden"); $("#app-view").classList.remove("hidden"); }
function logout(showMessage=true) {
  state.token=null; state.user=null; sessionStorage.removeItem("gatherly_token"); showAuth();
  if(showMessage) notify("You have been signed out.");
}
async function loadProfile() {
  state.user=await api("/auth/me");
  $("#org-name").textContent=state.user.organization_name;
  $("#user-role").textContent=state.user.role==="admin"?"Administrator workspace":"Employee workspace";
  $("#user-name").textContent=state.user.full_name;
  $("#user-email").textContent=state.user.email;
  $("#user-avatar").textContent=initials(state.user.full_name);
  $$(".admin-only").forEach(el=>el.classList.toggle("hidden",state.user.role!=="admin"));
  $("#registration-heading").textContent=state.user.role==="admin"?"Event registrations":"My registrations";
  $("#registration-subheading").textContent=state.user.role==="admin"?"Review attendee lists for your organization's events.":"Your event commitments, all in one place.";
}
async function boot() {
  $("#year").textContent=new Date().getFullYear();
  $("#today-label").textContent=new Date().toLocaleDateString([], {weekday:"short",month:"short",day:"numeric"});
  if(!state.token){showAuth();return;}
  try { await loadProfile(); showApp(); await refresh(); }
  catch(err){logout(false);notify(err.message,true);}
}
async function refresh() {
  const result=await api("/events?limit=100&offset=0");
  state.events=result.items||[];
  renderDashboard(); renderEvents(); await loadRegistrations();
}
function eventCard(event) {
  const date=dateValue(event.starts_at), month=date.toLocaleDateString([],{month:"short"}).toUpperCase(), day=date.getDate();
  const remaining=Math.max(0,event.capacity-event.active_registrations);
  const canManage=state.user?.role==="admin";
  const isRegistered=state.registrations.some(r=>r.event_id===event.id && r.status==="active");
  return `<article class="event-card">
    <div class="event-card-top"><div class="date-tile"><strong>${day}</strong><small>${month}</small></div><span class="status-pill">${date>=new Date()?"Upcoming":"Past event"}</span></div>
    <h3>${escapeHTML(event.title)}</h3><p>${escapeHTML(event.description||"A company event. Open for more details.")}</p>
    <div class="event-meta"><span>◷ ${escapeHTML(dateText(event.starts_at))}</span><span>⌖ ${escapeHTML(event.location)}</span></div>
    <div class="event-card-foot"><span class="capacity">${event.active_registrations}/${event.capacity} registered · ${remaining} spots</span>
    <div class="card-actions"><button class="mini-btn" data-detail="${event.id}">Details</button>
    ${canManage?`<button class="mini-btn" data-edit="${event.id}">Edit</button><button class="mini-btn danger" data-delete="${event.id}">Delete</button>`:(!isRegistered && remaining>0 && date>=new Date()?`<button class="mini-btn" data-register="${event.id}">Join</button>`:"")}</div></div>
  </article>`;
}
function emptyState(title,desc) { return `<div class="empty-state"><strong>${escapeHTML(title)}</strong>${escapeHTML(desc)}</div>`; }
function renderDashboard() {
  const now=new Date(), upcoming=state.events.filter(e=>dateValue(e.starts_at)>=now);
  $("#stat-events").textContent=state.events.length;
  $("#stat-registrations").textContent=state.events.reduce((n,e)=>n+e.active_registrations,0);
  $("#stat-upcoming").textContent=upcoming.length;
  $("#dashboard-events").innerHTML=upcoming.length?upcoming.slice(0,3).map(eventCard).join(""):emptyState("No upcoming events yet","New company events will appear here.");
}
function renderEvents() {
  const term=($("#event-search")?.value||"").trim().toLowerCase();
  const list=state.events.filter(e=>e.title.toLowerCase().includes(term)||e.location.toLowerCase().includes(term));
  $("#event-count").textContent=`${list.length} event${list.length===1?"":"s"}`;
  $("#all-events").innerHTML=list.length?list.map(eventCard).join(""):emptyState("No events found","Try another search or create a new event.");
}
async function loadRegistrations() {
  try {
    if(state.user.role==="employee") {
      state.registrations=await api("/registrations/mine");
      renderEmployeeRegistrations();
    } else {
      const groups=await Promise.all(state.events.map(e=>api(`/events/${e.id}/registrations`).then(rows=>rows.map(r=>({...r,event_title:e.title,event_starts_at:e.starts_at,event_location:e.location})))));
      state.registrations=groups.flat();
      renderAdminRegistrations();
    }
    renderDashboard(); renderEvents();
  } catch(err) { $("#registration-list").innerHTML=emptyState("Could not load registrations",err.message); }
}
function renderEmployeeRegistrations() {
  const rows=state.registrations;
  $("#registration-list").innerHTML=rows.length?`<table class="data-table"><thead><tr><th>EVENT</th><th>DATE</th><th>LOCATION</th><th>STATUS</th><th>ACTION</th></tr></thead><tbody>${rows.map(r=>`<tr><td><strong>${escapeHTML(r.event_title)}</strong></td><td>${escapeHTML(dateText(r.event_starts_at))}</td><td>${escapeHTML(r.event_location)}</td><td>${escapeHTML(r.status)}</td><td>${r.status==="active"?`<button class="mini-btn danger" data-cancel="${r.id}">Cancel</button>`:"—"}</td></tr>`).join("")}</tbody></table>`:emptyState("No registrations yet","Explore events and register for the ones you like.");
}
function renderAdminRegistrations() {
  const rows=state.registrations;
  $("#registration-list").innerHTML=rows.length?`<table class="data-table"><thead><tr><th>EVENT</th><th>ATTENDEE ID</th><th>REGISTERED</th><th>STATUS</th></tr></thead><tbody>${rows.map(r=>`<tr><td><strong>${escapeHTML(r.event_title)}</strong></td><td>${escapeHTML(r.employee_id.slice(0,8))}…</td><td>${escapeHTML(dateText(r.created_at))}</td><td>${escapeHTML(r.status)}</td></tr>`).join("")}</tbody></table>`:emptyState("No registrations yet","Employee registrations will appear here.");
}
function switchView(view) {
  $$(".page-view").forEach(el=>el.classList.toggle("hidden",el.id!==`${view}-view`));
  $$(".nav-link[data-view]").forEach(el=>el.classList.toggle("active",el.dataset.view===view));
  $("#page-title").textContent=({dashboard:"Dashboard",events:"All events",registrations:"Registrations"})[view]||"Dashboard";
  if(view==="registrations")loadRegistrations();
}
function openEventDialog(event=null) {
  const form=$("#event-form"); form.reset(); form.elements.event_id.value=event?.id||"";
  $("#event-modal-title").textContent=event?"Edit event":"Create an event";
  if(event) {
    form.elements.title.value=event.title; form.elements.description.value=event.description||"";
    const d=dateValue(event.starts_at); form.elements.starts_at.value=new Date(d.getTime()-d.getTimezoneOffset()*60000).toISOString().slice(0,16);
    form.elements.capacity.value=event.capacity; form.elements.location.value=event.location;
  }
  $("#event-dialog").showModal();
}
async function openDetail(id) {
  const event=state.events.find(e=>e.id===id); if(!event)return;
  state.activeEvent=event;
  $("#detail-title").textContent=event.title;
  $("#detail-content").innerHTML=`<p class="detail-copy">${escapeHTML(event.description||"No description provided.")}</p><p class="detail-copy">◷ ${escapeHTML(dateText(event.starts_at))}<br>⌖ ${escapeHTML(event.location)}<br>✓ ${event.active_registrations} of ${event.capacity} registrations</p>`;
  const registered=state.registrations.some(r=>r.event_id===id&&r.status==="active");
  const btn=$("#detail-register");
  btn.classList.toggle("hidden",state.user.role==="admin"||registered||event.active_registrations>=event.capacity||dateValue(event.starts_at)<new Date());
  btn.textContent="Register for event"; btn.dataset.register=id;
  $("#detail-dialog").showModal();
}
async function registerForEvent(id) {
  await api(`/events/${id}/registrations`,{method:"POST"});
  notify("You're registered for this event."); if($("#detail-dialog").open)$("#detail-dialog").close(); await refresh();
}
async function cancelRegistration(id) {
  if(!confirm("Cancel this event registration?"))return;
  await api(`/registrations/${id}`,{method:"DELETE"}); notify("Registration cancelled."); await refresh();
}
function handleAction(target) {
  const action=target.closest("[data-action]")?.dataset.action;
  if(action==="create-event")openEventDialog();
  if(action==="add-employee")$("#employee-dialog").showModal();
}
document.addEventListener("click",async e=>{
  const tab=e.target.closest("[data-auth-tab]"); if(tab){setAuthTab(tab.dataset.authTab);return;}
  const close=e.target.closest("[data-close]"); if(close){document.getElementById(close.dataset.close).close();return;}
  const view=e.target.closest("[data-view]"); if(view){switchView(view.dataset.view);return;}
  const action=e.target.closest("[data-action]"); if(action){handleAction(action);return;}
  const detail=e.target.closest("[data-detail]"); if(detail){openDetail(detail.dataset.detail);return;}
  const edit=e.target.closest("[data-edit]"); if(edit){openEventDialog(state.events.find(x=>x.id===edit.dataset.edit));return;}
  const remove=e.target.closest("[data-delete]"); if(remove){const event=state.events.find(x=>x.id===remove.dataset.delete);if(!confirm(`Delete "${event?.title||"this event"}"? Events with registration history cannot be deleted.`))return;try{await api(`/events/${remove.dataset.delete}`,{method:"DELETE"});notify("Event deleted.");await refresh();}catch(err){notify(err.message,true);}return;}
  const register=e.target.closest("[data-register]"); if(register){try{await registerForEvent(register.dataset.register);}catch(err){notify(err.message,true);}return;}
  const cancel=e.target.closest("[data-cancel]"); if(cancel){try{await cancelRegistration(cancel.dataset.cancel);}catch(err){notify(err.message,true);}return;}
});
$("#login-form").addEventListener("submit",async e=>{
  e.preventDefault(); const data=Object.fromEntries(new FormData(e.currentTarget));
  const button=$("button[type=submit]",e.currentTarget); button.disabled=true; button.textContent="Signing in…";
  try {const result=await fetch(`${API}/auth/login`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(data)});const body=await result.json();if(!result.ok)throw new Error(body.detail||"Sign in failed.");state.token=body.access_token;sessionStorage.setItem("gatherly_token",state.token);await loadProfile();showApp();await refresh();notify("Welcome to Gatherly.");}
  catch(err){notify(err.message,true);}finally{button.disabled=false;button.innerHTML='Sign in <span>→</span>';}
});
$("#register-form").addEventListener("submit",async e=>{
  e.preventDefault();const data=Object.fromEntries(new FormData(e.currentTarget));
  try{const user=await api("/auth/register-organization",{method:"POST",body:JSON.stringify(data)});setAuthTab("login");$("#login-form").elements.organization_id.value=user.organization_id;$("#login-form").elements.email.value=user.email;notify(`Workspace created! Save this Organization ID: ${user.organization_id}`);alert(`Your organization was created. Save this Organization ID:\n\n${user.organization_id}\n\nYou will need it to sign in.`);}
  catch(err){notify(err.message,true);}
});
$("#event-form").addEventListener("submit",async e=>{
  e.preventDefault();const f=e.currentTarget,id=f.elements.event_id.value;
  const payload={title:f.elements.title.value.trim(),description:f.elements.description.value.trim()||null,starts_at:new Date(f.elements.starts_at.value).toISOString(),location:f.elements.location.value.trim(),capacity:Number(f.elements.capacity.value)};
  try{await api(id?`/events/${id}`:"/events",{method:id?"PATCH":"POST",body:JSON.stringify(payload)});$("#event-dialog").close();notify(id?"Event updated.":"Event created.");await refresh();}
  catch(err){notify(err.message,true);}
});
$("#employee-form").addEventListener("submit",async e=>{
  e.preventDefault();const payload=Object.fromEntries(new FormData(e.currentTarget));
  try{const user=await api("/auth/employees",{method:"POST",body:JSON.stringify(payload)});$("#employee-dialog").close();e.currentTarget.reset();notify(`Employee account created for ${user.full_name}.`);}
  catch(err){notify(err.message,true);}
});
$("#event-search").addEventListener("input",renderEvents);
$("#logout-btn").addEventListener("click",()=>logout());
boot();
