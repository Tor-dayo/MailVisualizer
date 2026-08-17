import json


def _safe_json(data) -> str:
    return (
        json.dumps(data, ensure_ascii=False)
        .replace("&", "\\u0026")
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
    )


def export_html(mails, filename):
    data = [
        {
            "no": mail.no,
            "date": mail.date,
            "sender": mail.sender,
            "to": mail.to,
            "subject": mail.subject,
            "body": mail.body,
            "message_id": mail.message_id,
        }
        for mail in mails
    ]

    html = """<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Mail Visualizer</title>
<style>
:root{--navy:#17324d;--blue:#27628f;--line:#d7e0e8;--muted:#64788a}*{box-sizing:border-box}
body{margin:0;color:#18232d;background:#eef2f5;font-family:"Yu Gothic UI","Meiryo",sans-serif}
header{padding:24px 30px;color:white;background:var(--navy)}header h1{margin:0}header p{margin:5px 0 0;color:#d9e6f0}
.workspace{display:grid;grid-template-columns:minmax(320px,380px) 1fr;gap:18px;padding:18px}
.panel,.mail{background:white;border:1px solid var(--line);border-radius:10px}.panel{position:sticky;top:18px;align-self:start;padding:18px;max-height:calc(100vh - 36px);overflow:auto}
.section{padding:15px 0;border-top:1px solid var(--line)}.section:first-child{padding-top:0;border:0}
.section-title,.result-bar{display:flex;align-items:center;justify-content:space-between;gap:8px}.section-title strong{font-size:13px}
.note{margin:5px 0 10px;color:var(--muted);font-size:12px;line-height:1.5}button,select,input{font:inherit}
button{border:1px solid #aab9c6;border-radius:6px;padding:6px 10px;background:white;color:var(--navy);cursor:pointer}button:hover{background:#edf5fa}
.condition{display:grid;grid-template-columns:1fr 1fr 1.2fr auto;gap:6px;margin-top:7px}.sort-condition{grid-template-columns:1fr .8fr auto}
select,input{min-width:0;width:100%;border:1px solid #b9c6d1;border-radius:5px;padding:7px;background:white}.remove{width:32px;color:#9a2935}
.actions{display:flex;gap:8px}.primary{border-color:var(--blue);color:white;background:var(--blue)}.result-bar{margin-bottom:10px}.count{color:var(--muted);font-size:13px}
.mail-list{display:grid;gap:12px}.mail{overflow:hidden}.mail summary{list-style:none;cursor:pointer;padding:15px 18px}.mail summary:hover{background:#f6f9fb}
.title{display:flex;justify-content:space-between;gap:14px}.title h3{margin:0;font-size:16px}.number{flex:none;color:var(--muted);font-size:12px}
.meta{display:grid;grid-template-columns:1fr 1fr .8fr;gap:6px 18px;margin-top:9px;color:#526778;font-size:12px}
.body{padding:17px 18px 20px;border-top:1px solid var(--line)}dl{display:grid;grid-template-columns:92px 1fr;margin:0 0 16px;font-size:12px}dt,dd{margin:0;padding:4px 0;overflow-wrap:anywhere}dt{color:var(--muted);font-weight:bold}
pre{margin:0;white-space:pre-wrap;overflow-wrap:anywhere;word-break:break-word;font:14px/1.75 "Yu Gothic UI","Meiryo",sans-serif}.empty{padding:50px;text-align:center;color:var(--muted);background:white;border-radius:10px}
@media(max-width:900px){.workspace{grid-template-columns:1fr}.panel{position:static;max-height:none}.meta{grid-template-columns:1fr}}
@media print{header,.panel,.result-bar{display:none}.workspace{display:block;padding:0}.mail{break-after:page;border:0}.body{display:block}}
</style></head><body>
<header><h1>Mail Visualizer</h1><p>複数条件で絞り込み・並べ替えができます</p></header>
<main class="workspace"><aside class="panel">
<section class="section"><div class="section-title"><strong>絞り込み条件（AND）</strong><button id="add-filter" type="button">＋ 条件追加</button></div><p class="note">すべての条件に一致するメールを表示します。</p><div id="filters"></div></section>
<section class="section"><div class="section-title"><strong>並べ替え条件</strong><button id="add-sort" type="button">＋ 条件追加</button></div><p class="note">上の条件から順に優先されます。</p><div id="sorts"></div></section>
<section class="section actions"><button id="apply" class="primary" type="button">条件を適用</button><button id="reset" type="button">リセット</button></section>
</aside><section><div class="result-bar"><strong>検索結果</strong><span id="result-count" class="count"></span></div><div id="mail-list" class="mail-list"></div></section></main>
<script id="mail-data" type="application/json">__MAIL_DATA__</script>
<script>
const mails=JSON.parse(document.getElementById("mail-data").textContent);
const fields=[["no","管理No."],["date","送信日時"],["sender","差出人"],["to","宛先"],["subject","件名"],["body","本文"],["message_id","Message-ID"]];
const operators=[["contains","含む"],["not_contains","含まない"],["equals","等しい"],["starts","で始まる"],["ends","で終わる"]];
const filters=document.getElementById("filters"),sorts=document.getElementById("sorts"),list=document.getElementById("mail-list");
const options=items=>items.map(([v,l])=>`<option value="${v}">${l}</option>`).join("");
function addFilter(field="subject",operator="contains",query=""){
 const row=document.createElement("div");row.className="condition filter-condition";
 row.innerHTML=`<select class="field">${options(fields)}</select><select class="operator">${options(operators)}</select><input class="query" placeholder="文字を入力"><button class="remove" type="button">×</button>`;
 row.querySelector(".field").value=field;row.querySelector(".operator").value=operator;row.querySelector(".query").value=query;
 row.querySelector(".remove").onclick=()=>row.remove();row.querySelector("input").onkeydown=e=>{if(e.key==="Enter")applyConditions()};filters.append(row);
}
function addSort(field="date",direction="asc"){
 const row=document.createElement("div");row.className="condition sort-condition";
 row.innerHTML=`<select class="field">${options(fields.filter(([v])=>v!=="body"))}</select><select class="direction"><option value="asc">昇順</option><option value="desc">降順</option></select><button class="remove" type="button">×</button>`;
 row.querySelector(".field").value=field;row.querySelector(".direction").value=direction;row.querySelector(".remove").onclick=()=>row.remove();sorts.append(row);
}
const norm=value=>String(value??"").normalize("NFKC").toLocaleLowerCase("ja");
function matches(mail,c){const v=norm(mail[c.field]),q=norm(c.query);if(!q)return true;if(c.operator==="not_contains")return !v.includes(q);if(c.operator==="equals")return v===q;if(c.operator==="starts")return v.startsWith(q);if(c.operator==="ends")return v.endsWith(q);return v.includes(q)}
function compare(a,b,field){if(field==="no")return Number(a||0)-Number(b||0);if(field==="date"){const left=Date.parse(a),right=Date.parse(b);if(!Number.isNaN(left)&&!Number.isNaN(right))return left-right}return norm(a).localeCompare(norm(b),"ja",{numeric:true,sensitivity:"base"})}
function element(tag,text,className=""){const e=document.createElement(tag);e.textContent=text||"";if(className)e.className=className;return e}
function render(items){list.replaceChildren();document.getElementById("result-count").textContent=`${items.length} / ${mails.length}件`;if(!items.length){list.append(element("div","条件に一致するメールはありません。","empty"));return}
 for(const mail of items){const details=document.createElement("details");details.className="mail";const summary=document.createElement("summary"),title=document.createElement("div");title.className="title";title.append(element("h3",mail.subject||`件名なし ${mail.no}`),element("span",`No. ${mail.no}`,"number"));const meta=document.createElement("div");meta.className="meta";meta.append(element("span",`From: ${mail.sender||"―"}`),element("span",`To: ${mail.to||"―"}`),element("span",mail.date||"日時なし"));summary.append(title,meta);const body=document.createElement("div");body.className="body";const dl=document.createElement("dl");[["差出人",mail.sender],["宛先",mail.to],["送信日時",mail.date],["Message-ID",mail.message_id]].forEach(([k,v])=>dl.append(element("dt",k),element("dd",v||"―")));body.append(dl,element("pre",mail.body||"本文なし"));details.append(summary,body);list.append(details)}}
function applyConditions(){const filterConditions=[...document.querySelectorAll(".filter-condition")].map(r=>({field:r.querySelector(".field").value,operator:r.querySelector(".operator").value,query:r.querySelector(".query").value}));const sortConditions=[...document.querySelectorAll(".sort-condition")].map(r=>({field:r.querySelector(".field").value,direction:r.querySelector(".direction").value}));const result=mails.filter(mail=>filterConditions.every(c=>matches(mail,c)));result.sort((a,b)=>{for(const c of sortConditions){const compared=compare(a[c.field],b[c.field],c.field);if(compared)return c.direction==="desc"?-compared:compared}return Number(a.no)-Number(b.no)});render(result)}
document.getElementById("add-filter").onclick=()=>addFilter();document.getElementById("add-sort").onclick=()=>addSort();document.getElementById("apply").onclick=applyConditions;
document.getElementById("reset").onclick=()=>{filters.replaceChildren();sorts.replaceChildren();addFilter();addSort();applyConditions()};addFilter();addSort();applyConditions();
</script></body></html>
""".replace("__MAIL_DATA__", _safe_json(data))

    with open(filename, "w", encoding="utf-8") as file:
        file.write(html)
