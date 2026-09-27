from __future__ import annotations
import csv, datetime as dt, json, pathlib, re

ROOT=pathlib.Path(__file__).resolve().parents[1]
ACCOUNTS=json.loads((ROOT/"config"/"accounts.json").read_text(encoding="utf-8"))

def num(v):
    if v is None: return None
    s=str(v).replace(",","").strip()
    if s in ("","-","—"): return None
    try: return float(s)
    except ValueError: return None

def pick(rows,candidates):
    norm=lambda x: re.sub(r"\s+","",str(x or "")).lower()
    for c in candidates:
        nc=norm(c)
        for r in rows:
            if norm(r.get("account_id"))==nc or norm(r.get("account_nm"))==nc:
                v=num(r.get("thstrm_amount"))
                if v is not None: return v
    # fallback: exact Korean label containment
    for c in candidates:
        nc=norm(c)
        if not nc: continue
        for r in rows:
            an=norm(r.get("account_nm"))
            if nc in an or an in nc:
                v=num(r.get("thstrm_amount"))
                if v is not None: return v
    return None

def pct(a,b):
    return round(a/b*100,2) if a is not None and b not in (None,0) else None

def safe_sub(a,b):
    return a-b if a is not None and b is not None else None

def main():
    records=[]
    for path in sorted((ROOT/"data/raw").glob("*.json")):
        doc=json.loads(path.read_text(encoding="utf-8"))
        rows=doc.get("list",[])
        if not rows: continue
        r={k:pick(rows,v) for k,v in ACCOUNTS.items()}
        r.update(year=int(doc["year"]),report_code=doc["reprt_code"],category=doc["category"],
                 period=f'{doc["year"]}-{doc["reprt_code"]}',fs_div=doc.get("fs_div"))
        records.append(r)

    records.sort(key=lambda x:(x["year"],x["report_code"]))
    for i,r in enumerate(records):
        prev=next((x for x in records[:i][::-1] if x["report_code"]==r["report_code"]),None)
        prev_rev=(prev or {}).get("revenue")
        r["revenue_growth_pct"]=pct(safe_sub(r["revenue"],prev_rev),prev_rev)
        r["gross_margin_pct"]=pct(r["gross_profit"],r["revenue"])
        r["operating_margin_pct"]=pct(r["operating_income"],r["revenue"])
        r["net_margin_pct"]=pct(r["net_income"],r["revenue"])
        r["roa_pct"]=pct(r["net_income"],r["total_assets"])
        r["roe_pct"]=pct(r["net_income"],r["total_equity"])
        r["current_ratio_pct"]=pct(r["current_assets"],r["current_liabilities"])
        quick=safe_sub(r["current_assets"],r["inventory"])
        r["quick_ratio_pct"]=pct(quick,r["current_liabilities"])
        r["debt_to_equity_pct"]=pct(r["total_liabilities"],r["total_equity"])
        r["inventory_turnover"]=round(r["cost_of_sales"]/r["inventory"],2) if r["cost_of_sales"] is not None and r["inventory"] not in (None,0) else None
        r["dso"]=round(r["receivables"]/r["revenue"]*365,2) if r["receivables"] is not None and r["revenue"] not in (None,0) else None
        r["cfo_conversion_pct"]=pct(r["operating_cash_flow"],r["net_income"])
        r["free_cash_flow"]=safe_sub(r["operating_cash_flow"],abs(r["capex"]) if r["capex"] is not None else None)

    fields=[]
    for r in records:
        for k in r:
            if k not in fields: fields.append(k)
    with (ROOT/"data/financial_summary.csv").open("w",newline="",encoding="utf-8-sig") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(records)
    dashboard={
        "company":"삼성SDI","corp_code":"00126362","stock_code":"006400",
        "updated_at":dt.datetime.now().isoformat(timespec="seconds"),
        "records":records
    }
    (ROOT/"data/dashboard.json").write_text(json.dumps(dashboard,ensure_ascii=False,indent=2),encoding="utf-8")

if __name__=="__main__": main()
