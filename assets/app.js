/* Saudi Jobs SEO Dynamic — client utilities
   - Loads /data/jobs.json (or Google Sheet CSV if configured in config.json by build.py)
   - Renders lists with filters
*/
async function loadJSON(url){
  const res = await fetch(url, {cache:"no-store"});
  if(!res.ok) throw new Error("Failed to load: " + url);
  return await res.json();
}
function esc(s){ return String(s??"").replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m])); }
function getParam(name){
  const u = new URL(location.href);
  return u.searchParams.get(name);
}
function normalize(s){ return String(s||"").trim(); }
function matchText(job, q){
  if(!q) return true;
  q = q.toLowerCase();
  const hay = [
    job.title_ar, job.title_en, job.company, job.city, job.category,
    job.specialty, job.qualification, job.employment_type, job.work_mode
  ].map(x => String(x||"").toLowerCase()).join(" ");
  return hay.includes(q);
}
function cardJob(job){
  const title = esc(job.title_ar || "");
  const en = job.title_en ? ` <span class="badge" title="English title">${esc(job.title_en)}</span>` : "";
  const meta = `${esc(job.city||"")} • ${esc(job.employment_type||"")} • ${esc(job.qualification||"")}`;
  const apply = esc(job.apply_url || "#");
  const details = esc(job.details_url || "#");
  return `
  <article class="job">
    <div>
      <strong>${title}${en}</strong>
      <div class="meta">${meta}</div>
      <div class="meta">الشركة: ${esc(job.company||"")}</div>
    </div>
    <div class="cta">
      <a class="linkBtn" href="${apply}" target="_blank" rel="noopener">قدم الآن</a>
      <a class="linkBtn" href="${details}" target="_blank" rel="noopener">تفاصيل المصدر</a>
      <a class="linkBtn" href="/jobs/${esc(job.slug)}.html">صفحة الوظيفة</a>
    </div>
  </article>`;
}
function facetLink(type, slug, label){
  const href = `/${type}/${encodeURIComponent(slug)}/index.html`;
  return `<a class="linkBtn" href="${href}">${esc(label)}</a>`;
}
function unique(list){
  return [...new Set(list.filter(Boolean).map(x => String(x).trim()))].sort((a,b)=>a.localeCompare(b,'ar'));
}

async function renderIndex(){
  const jobs = await loadJSON("/data/jobs.json");
  const q = normalize(document.querySelector("#q")?.value);
  const city = normalize(document.querySelector("#city")?.value);
  const cat = normalize(document.querySelector("#category")?.value);
  const qual = normalize(document.querySelector("#qualification")?.value);
  const mode = normalize(document.querySelector("#work_mode")?.value);

  const filtered = jobs.filter(j => {
    if(!matchText(j, q)) return false;
    if(city && city !== "الكل" && j.city !== city) return false;
    if(cat && cat !== "الكل" && j.specialty !== cat && j.category !== cat) return false;
    if(qual && qual !== "الكل" && j.qualification !== qual) return false;
    if(mode && mode !== "الكل" && j.work_mode !== mode) return false;
    return true;
  });

  const listEl = document.querySelector("#jobsList");
  listEl.innerHTML = filtered.map(cardJob).join("") || `<div class="note">لا توجد نتائج مطابقة. جرّب كلمات أخرى أو غيّر الفلاتر.</div>`;

  // facets
  const cities = unique(jobs.map(j=>j.city));
  const specs = unique(jobs.map(j=>j.specialty || j.category));
  const quals = unique(jobs.map(j=>j.qualification));

  const citiesEl = document.querySelector("#citiesLinks");
  if(citiesEl) citiesEl.innerHTML = cities.map(c => facetLink("cities", (window.__slugMapCities?.[c]||c), c)).join("");

  const specEl = document.querySelector("#specialtiesLinks");
  if(specEl) specEl.innerHTML = specs.map(s => facetLink("specialties", (window.__slugMapSpecs?.[s]||s), s)).join("");

  const qualEl = document.querySelector("#qualLinks");
  if(qualEl) qualEl.innerHTML = quals.map(qv => facetLink("qualifications", (window.__slugMapQuals?.[qv]||qv), qv)).join("");
}

async function renderFacetPage(kind){
  const jobs = await loadJSON("/data/jobs.json");
  const slug = getParam("slug");
  const label = getParam("label") || "";
  const filterLabel = document.querySelector("#facetLabel");
  if(filterLabel) filterLabel.textContent = label;

  const filtered = jobs.filter(j => {
    if(kind==="cities") return (j.city_slug===slug);
    if(kind==="specialties") return (j.specialty_slug===slug || j.category_slug===slug);
    if(kind==="qualifications") return (j.qualification_slug===slug);
    return true;
  });

  const listEl = document.querySelector("#jobsList");
  listEl.innerHTML = filtered.map(cardJob).join("") || `<div class="note">لا توجد وظائف في هذا القسم حالياً.</div>`;
}

document.addEventListener("DOMContentLoaded", () => {
  const page = document.documentElement.dataset.page;
  if(page === "index"){
    document.querySelector("#searchBtn")?.addEventListener("click", (e)=>{ e.preventDefault(); renderIndex(); });
    renderIndex();
  } else if(page === "facet"){
    const kind = document.documentElement.dataset.kind;
    renderFacetPage(kind);
  }
});
