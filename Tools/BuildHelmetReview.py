from pathlib import Path
import json, html
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'ArtSource/StyleReference/MEL17'
d=json.loads((OUT/'latest-helmet.json').read_text());folder=d['candidate']
score=f"{d['score']}/10" if d.get('score') is not None else 'Review pending'
page=f'''<!doctype html><html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Helmet proof · {html.escape(folder)}</title>
<style>*{{box-sizing:border-box}}body{{margin:0;background:#111a20;color:#e7e7e1;font:16px/1.5 'Segoe UI',sans-serif}}main{{max-width:1680px;margin:auto;padding:28px}}h1{{font-size:32px;margin:5px 0}}p{{max-width:1050px;color:#bac7cd}}a{{color:#a8d9e5}}.views{{display:grid;grid-template-columns:1.25fr .75fr .5fr;gap:18px}}article{{min-width:0}}img,svg{{display:block;width:100%;height:650px;object-fit:contain;background:#222c31}}h2{{font-size:17px}}.status{{padding:12px 16px;border-left:3px solid #b9a570;background:#1e2e36}}@media(max-width:900px){{.views{{grid-template-columns:1fr 1fr}}article:first-child{{grid-column:1/-1}}img,svg{{height:480px}}}}</style>
<main><small>MELEE COMBAT LAB · {html.escape(folder)}</small><h1>Helmet proof</h1><p>Smooth steel, a narrow eye slit, and a continuous central ridge. Geometry follows the approved knight; the smoother material follows the accepted v025 study.</p>
<div class="status"><b>Independent critic: {score}</b> · {html.escape(d['summary'])}</div>
<section class="views"><article><h2>Three-quarter</h2><a href="{folder}/helmet.png"><img src="{folder}/helmet.png" alt="Actual three-quarter helmet render"></a></article><article><h2>Front</h2><a href="{folder}/front.png"><img src="{folder}/front.png" alt="Actual front helmet render"></a></article><article><h2>Original reference detail</h2><svg viewBox="417 170 155 220" role="img" aria-label="Helmet detail from unchanged original reference"><image href="06-riot-inspired.png" width="1024" height="1536"/></svg></article></section>
<p><a href="{folder}/{folder}.blend">Editable Blender source</a> · <a href="{folder}/CRITIC.md">Critic notes</a> · <a href="HELMET_ITERATIONS.md">Iteration history</a></p><p>Static helmet proof. Rear construction is inferred. This review does not establish animation or gameplay acceptance.</p></main></html>'''
(OUT/'helmet-review.html').write_text(page,encoding='utf-8');print(folder,score)
