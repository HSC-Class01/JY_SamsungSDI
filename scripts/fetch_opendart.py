from __future__ import annotations
import argparse, datetime as dt, json, os, pathlib, time
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

ROOT = pathlib.Path(__file__).resolve().parents[1]
CORP_CODE = "00126362"  # Samsung SDI
STOCK_CODE = "006400"
REPORTS = {"11011":"annual","11012":"half_year","11013":"quarterly","11014":"quarterly"}
BASE = "https://opendart.fss.or.kr/api"

def get_key():
    key=os.getenv("DART_API_KEY","").strip()
    if not key and (ROOT/".env").exists():
        for line in (ROOT/".env").read_text(encoding="utf-8").splitlines():
            if line.strip().startswith("DART_API_KEY="):
                key=line.split("=",1)[1].strip()
    if not key:
        raise SystemExit("DART_API_KEY가 없습니다. API_KEY_SETUP.txt를 확인하세요.")
    return key

def get_json(path, params, retries=3):
    for i in range(retries):
        r=requests.get(f"{BASE}/{path}",params=params,timeout=60)
        r.raise_for_status()
        data=r.json()
        if data.get("status") in (None,"000","013"):
            return data
        if data.get("status")=="020" and i<retries-1:
            time.sleep(3*(i+1)); continue
        return data
    return {}

def main(start_year:int):
    key=get_key()
    raw=ROOT/"data"/"raw"; raw.mkdir(parents=True,exist_ok=True)
    source=ROOT/"reports"/"source"; source.mkdir(parents=True,exist_ok=True)
    today=dt.date.today().strftime("%Y%m%d")
    end_year=dt.date.today().year

    # 1) DART disclosure list: 2010-present
    disclosures=[]
    for year in range(start_year,end_year+1):
        data=get_json("list.json",{
            "crtfc_key":key,"corp_code":CORP_CODE,
            "bgn_de":f"{year}0101","end_de":today,
            "pblntf_ty":"A","page_no":1,"page_count":100
        })
        for item in data.get("list",[]):
            name=item.get("report_nm","")
            if any(x in name for x in ("사업보고서","반기보고서","분기보고서")) and "정정" not in name:
                disclosures.append(item)

    # 2) Save source filing ZIPs. This covers 2010+ even though structured
    # financial-statement API values are officially provided from 2015.
    def save_doc(item):
        rcp=item["rcept_no"]; out=source/f"{rcp}.zip"
        if out.exists(): return
        r=requests.get(f"{BASE}/document.xml",params={"crtfc_key":key,"rcept_no":rcp},timeout=90)
        r.raise_for_status()
        if r.content.startswith(b"PK"):
            out.write_bytes(r.content)

    with ThreadPoolExecutor(max_workers=5) as pool:
        list(pool.map(save_doc,disclosures))

    # 3) Structured financial statements: 2015+
    tasks=[]
    for year in range(max(start_year,2015),end_year+1):
        for code,category in REPORTS.items():
            out=raw/f"samsung_sdi_{year}_{code}.json"
            if not out.exists():
                tasks.append((year,code,category,out))

    def fetch_financial(task):
        year,code,category,out=task
        params={"crtfc_key":key,"corp_code":CORP_CODE,"bsns_year":str(year),"reprt_code":code,"fs_div":"CFS"}
        data=get_json("fnlttSinglAcntAll.json",params)
        if data.get("status")!="000" or not data.get("list"):
            params["fs_div"]="OFS"
            data=get_json("fnlttSinglAcntAll.json",params)
        data.update({"year":year,"reprt_code":code,"category":category,"corp_code":CORP_CODE,"stock_code":STOCK_CODE})
        out.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")

    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(fetch_financial,tasks))

    (ROOT/"reports"/"opendart_disclosures.json").write_text(
        json.dumps(disclosures,ensure_ascii=False,indent=2),encoding="utf-8"
    )

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--start-year",type=int,default=2010)
    main(p.parse_args().start_year)
