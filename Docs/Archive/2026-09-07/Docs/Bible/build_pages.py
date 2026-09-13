from pathlib import Path
import re, json, zipfile
from urllib.parse import quote, unquote

base = Path(__file__).resolve().parent
text = (base / 'MeleeCombatLab.md').read_text(encoding='utf-8')
parts = re.split(r'^## (\d\d — [^\n]+)\n', text, flags=re.M)
intro = parts[0]
sections = [(parts[i], parts[i+1]) for i in range(1, len(parts), 2)]
register = sections[-1][1].split('## Source register and maintenance\n', 1)[1]
sections[-1] = (sections[-1][0], sections[-1][1].split('## Source register and maintenance\n', 1)[0])
root = base / 'Notion' / 'MeleeCombatLab'
root.mkdir(parents=True, exist_ok=True)
def slug(name):
    return name.replace(' / ', ' - ')
def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip()+'\n', encoding='utf-8')
def link(name, path):
    return f'[{name}]({quote(path, safe="/")})'
nav = []
for title, body in sections:
    filename = title+'.md'
    nav.append('- '+link(title, filename))
    if title.startswith('00'):
        write(root/filename, '# '+title+'\n\n'+body+'\n\n'+link('Source register', 'Sources.md'))
        continue
    child_parts = re.split(r'^### ([^\n]+)\n', body, flags=re.M)
    children=[]
    for i in range(1,len(child_parts),2):
        name, content=child_parts[i],child_parts[i+1]
        # Repeatable protocol is part of Findings, not an additional requested child.
        if name.startswith('Repeatable review protocol'):
            continue
        if name=='Findings':
            content += '\n## '+child_parts[i+2]+'\n'+child_parts[i+3]
        filename_child=slug(name)+'.md'
        children.append('- '+link(name,title+'/'+filename_child))
        if name=='Task / Experiment Database':
            content += '\n\n'+link('Task database CSV','Task - Experiment Database.csv')+'\n'
        write(root/title/filename_child, '# '+name+'\n\n'+content+'\n\n'+link('Source register','../Sources.md'))
    write(root/filename,'# '+title+'\n\n'+'\n'.join(children)+'\n\n'+link('Source register','Sources.md'))
write(root/'Sources.md','# Source register and maintenance\n'+register.replace('Sources/Conversation excerpts.md','Conversation excerpts.md'))
write(root/'Conversation excerpts.md',(base/'Sources'/'Conversation excerpts.md').read_text(encoding='utf-8'))
write(base/'Notion'/'MeleeCombatLab.md',intro+'\n## Contents\n\n'+'\n'.join('- '+link(title,'MeleeCombatLab/'+title+'.md') for title,_ in sections)+'\n\n'+link('Source register','MeleeCombatLab/Sources.md'))
rows=[]
for line in text.splitlines():
    if line.startswith('| B-'):
        cells=[c.strip() for c in line.strip('|').split('|')]
        rows.append(cells)
extra=[
('Task','Animation','Latest imported shoulders and camera changes have not been reviewed together.','Capture the exact newest build and assets in first-person and external motion.','','S5; D4'),
('Experiment','Animation','Co-authored hands and weapon curves may produce stronger bodily causality.','Compare a right/left authored pose-curve pair against current motion at identical timings.','B-001','S6'),
('Task','Combat feedback','Contact needs convincing attacker and recipient consequence.','Author carry, resistance, rebound and recovery for four horizontal outcomes.','B-002','S5; S6'),
('Task','Audio','Synthesized impacts remain placeholder quality.','Create a small licensed or original cue set and evaluate in moving exchanges.','B-003','S6'),
('Experiment','Movement','Existing drive and momentum may need adjustment after coherent motion.','Compare drive/carry settings in range-edge approach, withdrawal and reversal fixtures.','B-002','S6; D3'),
('Task','Readability','First-person improvement must preserve clear external telegraphs.','Review opponent-view origin, commitment, feint/morph and outcome without debug labels.','B-002; B-003','S6'),
('Experiment','Balance','The double-parry fixture influenced timing selection.','Review intended initiative and defense rhythm before revising clocks or the fixture.','B-002','S6; D3'),
('Task','Performance','Historical local editor measurements do not certify the target.','Measure packaged representative two/four-combatant fixtures at 1080p on defined target hardware.','','S6; D6'),
('Task','Animation','Each attack family needs anatomical treatment.','Extend the accepted horizontal approach to overheads, underhands and stabs.','B-002; B-003; B-006','S5; S6'),
('Task','Visual direction','Premium grip, deformation and material quality remain unfinished.','Address the largest visible asset gaps after the exchange is convincing.','B-001; B-003','S4; S6; D5'),
('Experiment','Networking','Local quality must survive latency before broader production.','Define and implement a narrow contact/defense prediction experiment after local acceptance.','B-003; B-006','S6'),
('Task','Game structure','Strategic identity exists but match rules remain unspecified.','Compare a small set of objective/team/round proposals and record the chosen prototype.','','S1; S6')]
matrix=[['Name','ID','Type','Area','Priority','Status','Hypothesis / Problem','Next Action','Acceptance Evidence','Depends On','Source','Owner','Result / Decision']]
for row,details in zip(rows,extra):
    id,priority,name,status,evidence=row
    typ,area,problem,action,deps,source=details
    matrix.append([name,id,typ,area,priority,status,problem,action,evidence,deps,source,'',''])
write(base/'task_data.json',json.dumps(matrix,ensure_ascii=False,indent=2))
# Verify the requested 22-page hierarchy, plus two supporting source pages.
expected=22
pages=list((base/'Notion').rglob('*.md'))
assert len(pages)==expected+2, len(pages)
for page in pages:
    content=page.read_text(encoding='utf-8')
    assert not re.search(r'\bfreez\w*\b|\bfrozen\b',content,re.I),page
    # Generated navigation is relative and URI-encoded.
    if page.name!='Conversation excerpts.md':
        for dest in re.findall(r'\]\(([^)]+)\)',content):
            if not re.match(r'https?:|[A-Z]:|<',dest):
                assert (page.parent/unquote(dest)).exists(),(page,dest)
assert len(matrix)==13
print(f'Created and checked {expected} hierarchy pages, 2 source pages, and 12 task records.')
csv_path=root/'03 — Current Development'/'Task - Experiment Database.csv'
if csv_path.exists():
    import csv
    with csv_path.open(encoding='utf-8',newline='') as f:
        records=list(csv.DictReader(f))
    assert len(records)==12
    assert len({r['ID'] for r in records})==12
    assert all(r['Name'] and r['Next Action'] and r['Acceptance Evidence'] for r in records)
    archive=base/'MeleeCombatLab-Notion.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for path in (base/'Notion').rglob('*'):
            if path.is_file():
                z.write(path,path.relative_to(base/'Notion'))
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        assert len(z.namelist())==25
    print('Verified task CSV and ZIP: 24 Markdown pages and 1 CSV.')
