# Saudi Jobs — SEO Dynamic (JSON / Google Sheet)

## What you get
- صفحة رئيسية مع بحث وفلاتر (RTL) — `index.html`
- صفحات SEO ثابتة:
  - /cities/ (وصفحات لكل مدينة)
  - /specialties/ (وصفحات لكل تخصص/تصنيف)
  - /qualifications/ (وصفحات لكل مؤهل)
- أرشيف وظائف + صفحة تفاصيل لكل وظيفة مع Schema.org JobPosting
- sitemap.xml + robots.txt
- build.py لتحديث الصفحات والـ sitemap من:
  - data/jobs.json (افتراضي)
  - أو Google Sheet (CSV منشور)

## 1) Use JSON
- عدّل `data/jobs.json` وأضف وظائفك
- شغّل: `python3 build.py` (اختياري لتحديث sitemap/slug)

## 2) Use Google Sheet
- أنشئ Sheet بأعمدة مثل:
  id,title_ar,title_en,company,city,region,country,employment_type,work_mode,category,specialty,qualification,experience,openings,posted_date,apply_url,details_url,description
- File -> Share -> Publish to web -> CSV
- ضع رابط CSV في `config.json` وغيّر mode إلى "google_sheet_csv"
- شغّل: `python3 build.py`

## Important SEO notes
- غيّر `site.base_url` في config.json إلى دومينك الفعلي قبل النشر
- ارفع الموقع كما هو على أي استضافة Static (أو داخل ووردبريس عبر صفحة مخصصة)
