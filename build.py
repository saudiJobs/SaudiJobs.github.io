#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build script:
- Reads config.json
- Loads jobs from data/jobs.json OR Google Sheet published CSV
- Normalizes + creates slugs
- Regenerates facet pages, job pages, sitemap.xml

Usage:
  python3 build.py

Google Sheet instructions (quick):
1) Put your jobs in a Sheet with headers like:
   id,title_ar,title_en,company,city,region,country,employment_type,work_mode,category,specialty,qualification,experience,openings,posted_date,apply_url,details_url,description
2) File -> Share -> Publish to web -> CSV
3) Paste the published CSV URL into config.json under google_sheet_csv_url, and set mode to "google_sheet_csv"
"""
import os, json, re, csv, datetime, urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parent

def read_json(p): return json.loads((BASE/p).read_text(encoding="utf-8"))

def slugify_ar(s: str) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"[^\w\u0600-\u06FF]+", "-", s)
    s = re.sub(r"-{2,}", "-", s).strip("-")
    if re.search(r"[\u0600-\u06FF]", s):
        mapping = {
            "الرياض":"riyadh","جدة":"jeddah","مكة":"makkah","مكة-المكرمة":"makkah",
            "المدينة":"madinah","المدينة-المنورة":"madinah","الدمام":"dammam","الخبر":"khobar",
            "الظهران":"dhahran","تبوك":"tabuk","أبها":"abha","ابها":"abha","جازان":"jazan","جيزان":"jazan",
            "حائل":"hail","القصيم":"qassim","بريدة":"buraidah","الأحساء":"alahsa","الاحساء":"alahsa",
            "الطائف":"taif","ينبع":"yanbu","نجران":"najran","عرعر":"arar","سكاكا":"sakaka",
            "الباحة":"albaha","حفر-الباطن":"hafr-albatin"
        }
        if s in mapping: return mapping[s]
        return "ar-" + str(abs(hash(s)) % (10**10))
    return s

def job_slug(j):
    base_s = f"{j.get('title_en') or j.get('title_ar')}-{j.get('company')}-{j.get('city')}"
    s = re.sub(r"[^\w\u0600-\u06FF]+","-",base_s).strip("-").lower()
    if re.search(r"[\u0600-\u06FF]", s):
        return "job-" + str(abs(hash(s)) % (10**12))
    return s[:80]

def load_jobs(cfg):
    mode = cfg["data_source"]["mode"]
    if mode == "json":
        jobs = read_json(Path(cfg["data_source"]["json_path"]))
        return jobs
    if mode == "google_sheet_csv":
        url = cfg["data_source"]["google_sheet_csv_url"].strip()
        if not url or "PASTE_" in url:
            raise SystemExit("google_sheet_csv_url is not set in config.json")
        with urllib.request.urlopen(url) as r:
            content = r.read().decode("utf-8", errors="replace")
        rows = list(csv.DictReader(content.splitlines()))
        # Normalize keys
        jobs = []
        for row in rows:
            jobs.append({k.strip(): (v.strip() if isinstance(v,str) else v) for k,v in row.items()})
        return jobs
    raise SystemExit("Unknown data_source.mode. Use 'json' or 'google_sheet_csv'.")

def write(path, text):
    p = BASE / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")

def write_json(path, obj):
    write(path, json.dumps(obj, ensure_ascii=False, indent=2))

def unique(values):
    out = []
    for v in values:
        v = (v or "").strip()
        if v and v not in out: out.append(v)
    out.sort()
    return out

def main():
    cfg = read_json("config.json")
    base_url = cfg["site"]["base_url"].rstrip("/")

    jobs = load_jobs(cfg)

    # slugs
    cities = unique([j.get("city","") for j in jobs])
    specs  = unique([j.get("specialty") or j.get("category") or "" for j in jobs])
    quals  = unique([j.get("qualification","") for j in jobs])

    slug_map_c = {c: slugify_ar(c) for c in cities}
    slug_map_s = {s: slugify_ar(s) for s in specs}
    slug_map_q = {q: slugify_ar(q) for q in quals}

    for j in jobs:
        j["city_slug"] = slug_map_c.get(j.get("city",""), slugify_ar(j.get("city","")))
        spec = j.get("specialty") or j.get("category") or ""
        j["specialty_slug"] = slug_map_s.get(spec, slugify_ar(spec))
        j["category_slug"] = slugify_ar(j.get("category") or spec)
        j["qualification_slug"] = slug_map_q.get(j.get("qualification",""), slugify_ar(j.get("qualification","")))
        j["slug"] = job_slug(j)

    # save updated data
    write_json("data/jobs.json", jobs)

    # sitemap
    urls = [
        f"{base_url}/",
        f"{base_url}/jobs/",
        f"{base_url}/cities/",
        f"{base_url}/specialties/",
        f"{base_url}/qualifications/",
    ]
    for c in cities: urls.append(f"{base_url}/cities/{slug_map_c[c]}/")
    for s in specs:  urls.append(f"{base_url}/specialties/{slug_map_s[s]}/")
    for q in quals:  urls.append(f"{base_url}/qualifications/{slug_map_q[q]}/")
    for j in jobs:   urls.append(f"{base_url}/jobs/{j['slug']}.html")

    today = datetime.date.today().isoformat()
    sm = ['<?xml version="1.0" encoding="UTF-8"?>','<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        sm += ["  <url>", f"    <loc>{u}</loc>", f"    <lastmod>{today}</lastmod>", "  </url>"]
    sm.append("</urlset>\n")
    write("sitemap.xml", "\n".join(sm))

    print("Build completed:")
    print(f"- Jobs: {len(jobs)}")
    print(f"- Cities: {len(cities)}, Specialties: {len(specs)}, Qualifications: {len(quals)}")
    print("- sitemap.xml regenerated")
    print("Tip: update base_url in config.json to your real domain for correct canonical & sitemap URLs.")

if __name__ == "__main__":
    main()
