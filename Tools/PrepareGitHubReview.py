"""Prepare a lean review publication without changing the full authoring checkout.

prepare: read the committed project and retain a bounded visual review pack.
commit: use an alternate index and explicit remote parent; never rewrite history,
switch branches, delete native files, or publish automatically.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'Saved/GitHubReview20260913'
sha=lambda data:hashlib.sha256(data).hexdigest()

def git(*args,input=None,env=None):
    return subprocess.check_output(['git',*args],cwd=ROOT,input=input,env=env)

def prepare():
    from PIL import Image
    assert not OUT.exists(),'Preserve the existing review package'
    source=git('rev-parse','HEAD').decode().strip()
    entries={}
    for item in git('ls-tree','-rz',source).split(b'\0'):
        if not item:continue
        meta,path=item.split(b'\t',1);mode,kind,oid=meta.decode().split()
        if kind=='blob':entries[path.decode()]={'mode':mode,'oid':oid}
    roots={'Source','Tests','Tools','Config','Docs','.vscode'}
    text_ext={'.md','.txt','.json','.ini','.py','.ps1','.cpp','.h','.cs','.bat','.cmd','.yml','.yaml','.toml','.html','.css','.js','.xml','.csv','.uproject','.gitignore','.gitattributes'}
    explicit={'.gitattributes','.gitignore','AGENTS.md','PROJECT_SPEC.md','README.md','RECOVERY.md','VALIDATION.md','MeleeCombatLab.uproject'}
    selected={p:e for p,e in entries.items() if p in explicit or
        (p.split('/')[0] in roots and Path(p).suffix.lower() in text_ext)}
    art_paths=[
      'ArtSource/CharacterReset/EX_v002/Export/EX_v002_WeaponMotion.json',
      'ArtSource/CharacterReset/EX_v002/Export/manifest.json',
      'ArtSource/CharacterReset/EX_v002/Export/delivery-status.json',
      'ArtSource/UserMaleBody/MB_v005_SurfaceRepair/CHECKPOINT.md',
      'ArtSource/HunyuanHound/Hound_v001/CHECKPOINT.md',
      'ArtSource/HunyuanHound/Hound_v001/manifest.json',
      'ArtSource/HunyuanHound/Hound_v001/palette.json',
      'ArtSource/Cascadeur/MB_FreshRH_20260913/author_mb_rh.py']
    rh='ArtSource/Kimodo/RH_20260913/'
    art_paths += [rh+n for n in ['skeletons.json','reference-pullback-brief.md',
        'author_reference_pullback_v003.py','refine_reference_elbow.py','mark_reference_take.py']]
    art_paths += [rh+'B_reference_extended_v003/'+n for n in ['job.json','constraints.json','landmarks.json',
        'generation.json','transfer.json','B_ArmLoad_v004.json','elbow-change.json']]
    for p in art_paths:
        assert p in entries,p
        selected[p]=entries[p]
    OUT.mkdir(parents=True)
    files=OUT/'files';files.mkdir()
    generated={};media=[]
    def save(path,data):
        target=files/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
        generated[path]={'file':str(target.relative_to(ROOT)),'sha256':sha(data),'bytes':len(data)}
    def text(path,value):save(path,value.encode('utf-8'))
    def picture(src,name,caption,max_edge=2048):
        src=ROOT/src;im=Image.open(src).convert('RGB');im.thumbnail((max_edge,max_edge),Image.Resampling.LANCZOS)
        import io
        data=io.BytesIO();im.save(data,format='JPEG',quality=92,subsampling=0)
        dest='Docs/Review/'+name+'.jpg';save(dest,data.getvalue())
        media.append(dict(file=dest,source=str(src.relative_to(ROOT)),source_sha256=sha(src.read_bytes()),
            sha256=sha(data.getvalue()),dimensions=list(im.size),caption=caption,
            operation='JPEG review derivative; aspect preserved; original image/native source retained locally'))
    hound='ArtSource/HunyuanHound/Hound_v001/'
    for original,name,caption in [
       ('01-style-anatomy','hound-style-anatomy','Selected surface-style exemplar and interpretation; not a runtime character.'),
       ('02-four-views','hound-four-views','Four named views of the Hunyuan style exemplar.'),
       ('03-channel-atlas','hound-channel-atlas','Supplied texture channels; painted lighting is part of the appearance.'),
       ('04-lighting-diagnostic','hound-lighting','Controlled static lighting diagnostics; no engine acceptance.'),
       ('05-sampled-palette','hound-palette','Measured appearance palette; not calibrated reflectance.'),
       ('06-distance-hierarchy','hound-distance','Image-size comparison; not measured runtime LOD performance.')]:
        picture(hound+'Review/'+original+'.png',name,caption)
    picture(hound+'Source/11-hound-bascinet.png','hound-concept','Supporting Hound Bascinet concept; the generated model governs surface style.')
    picture('Saved/WorkingBodyRepair/textured-current-LOD0-sheet.png','working-body','Working MB_v005 rest body, four named views. Deep elbow-flexion findings remain open.')
    take='Saved/Kimodo/RH_20260913/B_reference_extended_v003/B_ArmLoad_v004/'
    picture(take+'inspection.jpg','animation-views','Selected provisional B_ArmLoad_v004: primary/rear-quarter samples and four body views; sampled evidence only.')
    picture(take+'interval-review.jpg','animation-intervals','Ordered selected-take samples, including windup, passage and recovery; not continuous viewing.')
    picture(take+'primary-0030.png','animation-load','Loaded pose at source frame30, 0.9667s. Upright torso and open winding elbow; rough fingers remain.')
    picture('Saved/reference.jpg','arm-load-reference','Daniel supplied this photograph as arm-windup direction; no baseball motion or timing inferred.')
    for view in ['primary','rear-quarter']:
        src=ROOT/take/(view+'.mp4');data=src.read_bytes();dest='Docs/Review/animation-'+view+'.mp4';save(dest,data)
        media.append(dict(file=dest,source=str(src.relative_to(ROOT)),source_sha256=sha(data),sha256=sha(data),
            operation='Unchanged complete1x movie',caption='B_ArmLoad_v004,92 frames at30fps; native500ms release; no human acceptance'))
    for filename,src in [('animation-preview.json',take+'preview.json'),('animation-timing.json',take+'timing.json'),
        ('animation-result.json','Saved/Kimodo/reference-result.json'),('body-source-verification.json','Saved/WorkingBodyRepair/source-verification.json')]:
        save('Docs/Review/'+filename,(ROOT/src).read_bytes())
    text('Docs/Review/manifest.json',json.dumps(dict(snapshot_date='2026-09-13',local_project_commit=source,
        animation_native_sha256='a27fc7b3c2e43072e71711baa5724c4f7c0f21113a64605ea6aa6bea71c35cad',
        body_native_sha256='67eeee22bd652e3ede89942a12621cd4dea103d9ca58309710adb158a1cfc319',media=media,
        limitations='Dated review derivatives. Original native art, archive drafts, raw motion and runtime binary assets remain local; this is not a runnable asset-complete distribution.'),indent=2)+'\n')
    text('Docs/Review/.gitattributes','*.jpg -filter -diff -merge -text\n*.mp4 -filter -diff -merge -text\n')
    gallery='''# Art review snapshot — 13 September 2026

Start with [review context](../GITHUB_REVIEW.md). This gallery pairs selected art with its status; the [manifest](manifest.json) binds source identities and image derivatives. Current work remains owned by [the TP checkpoint](../THIRD_PERSON_CHECKPOINT.md) and [development](../DEVELOPMENT.md).

## Surface-style direction

The Hunyuan Hound model is Daniel's selected surface-style anchor. This is an art direction reference, not an integrated runtime character. See the [surface guide](../Visual/HOUND_SURFACE_STYLE_GUIDE.md).

![Style anatomy](hound-style-anatomy.jpg)
![Four model views](hound-four-views.jpg)

[Supporting concept](hound-concept.jpg) · [Texture channels](hound-channel-atlas.jpg) · [Lighting diagnostics](hound-lighting.jpg) · [Palette](hound-palette.jpg) · [Distance study](hound-distance.jpg)

## Working character

MB_v005_SurfaceRepair is the current AccuRig authoring body. Rest-surface checks and extreme joint-deformation limits are distinct; the [body checkpoint](../../ArtSource/UserMaleBody/MB_v005_SurfaceRepair/CHECKPOINT.md) records the unresolved findings.

![Working body, four views](working-body.jpg)

## Third-person animation draft

B_ArmLoad_v004 is the provisional lead from three fresh Kimodo proposals and one native elbow refinement. It is unaccepted and not integrated. Windup1.30s; native release0.50s;92 samples at30fps; full1x timing. Fingers, lower-body support and carry remain rough. The source blade path has not been shown compatible with gameplay contact.

![Arm-load photograph](arm-load-reference.jpg)
![Current loaded pose](animation-load.jpg)
![Both animation angles and four body views](animation-views.jpg)
![Ordered motion samples](animation-intervals.jpg)

[Complete primary movie](animation-primary.mp4) · [Complete rear-quarter movie](animation-rear-quarter.mp4) · [Timing check](animation-timing.json) · [Detailed result](animation-result.json)

These images establish sampled visible facts only. Do not infer continuous rhythm, playable quality or human acceptance from sheets or technical checks. The videos are retained at source speed for explicit motion review.
'''
    text('Docs/Review/README.md',gallery)
    intro='''# Project review entry point

This GitHub snapshot is prepared for GPT-6 Pro-assisted code, design and art review. It includes current C++ source, tests, configuration, workflow tools, documentation, selected animation controls/receipts, and a small [art gallery](Review/README.md). It intentionally excludes archived animation drafts, native Blender/Cascadeur scenes, FBXs, raw motion arrays, full-resolution texture sets, Unreal asset binaries and build caches. The complete authoring checkout and its local commit are preserved separately.

## Read in this order

1. [Project rules](../AGENTS.md), [development](DEVELOPMENT.md), and [documentation ownership](DOCUMENTATION_OWNERSHIP.md).
2. [Project specification](../PROJECT_SPEC.md), [current TP checkpoint](THIRD_PERSON_CHECKPOINT.md), and [Kimodo workflow](KIMODO_ANIMATION_WORKFLOW.md).
3. [Art gallery](Review/README.md) and [surface-style guide](Visual/HOUND_SURFACE_STYLE_GUIDE.md).
4. The relevant implementation in [Source](../Source), [Tests](../Tests), [Config](../Config), and [Tools](../Tools); follow [validation](../VALIDATION.md).

Accepted EX_v002 first-person source/native playback remains protected. C++ owns legal input, attack timing, actor movement, blade contact and damage. TP art is provisional. Do not change gameplay to fit a visual draft silently. Older documents, diagnostics and linked local files are historical context, not new execution instructions or proof of acceptance.

## Useful review request

Read the rules, current checkpoint and relevant source. Identify the highest-impact remaining risks in TP readability, native500ms phase timing, two-hand authoring and source/contact compatibility. Separate code findings, sampled visual observations and uncertain hypotheses. Give file references and one small next experiment for each actionable issue. Preserve accepted FP behavior; do not infer playable acceptance from technical checks.

## Art access and evidence limits

The gallery contains ordinary JPEGs and small MP4s, not Git LFS pointers. GitHub/app access to repository text alone does not establish that a model viewed the images. If an image has not actually been retrieved visually, leave that judgment unscored and attach the relevant JPEG directly to the chat. Official [image-input guidance](https://learn.chatgpt.com/docs/image-inputs) recommends attaching visual context and stating what should be inspected. This package does not claim specific GPT-6 Pro GitHub-image or video support.

Historical links to omitted native files and Saved evidence intentionally remain as local provenance; use this gallery for portable review media. Unreal play/export commands elsewhere describe the asset-complete local workspace. This lean snapshot is not a runnable game package. See [publication policy](GITHUB_WORKSPACE.md).
'''
    text('Docs/GITHUB_REVIEW.md',intro)
    old_readme=git('show',source+':README.md').decode('utf-8-sig')
    old_readme=old_readme.replace('KN_v002 is the default draft/test-scene body; CF_v001 remains a preserved foundation.',
        'MB_v005_SurfaceRepair on the AccuRig skeleton is the current authoring body; Config/WorkingCharacter.json owns selection. KN_v002 and CF_v001 remain preserved earlier foundations.')
    note='> **GitHub review edition:** start with [the review entry point](Docs/GITHUB_REVIEW.md) and [art gallery](Docs/Review/README.md). Native art archives and runtime asset binaries remain in the full local project; this checkout is for source/design review.\n\n'
    text('README.md',old_readme.replace('# MeleeCombatLab\n','# MeleeCombatLab\n\n'+note,1))
    guide=git('show',source+':Docs/Visual/HOUND_SURFACE_STYLE_GUIDE.md').decode('utf-8-sig')
    for old,new in [('01-style-anatomy','hound-style-anatomy'),('02-four-views','hound-four-views'),('03-channel-atlas','hound-channel-atlas'),('04-lighting-diagnostic','hound-lighting'),('05-sampled-palette','hound-palette'),('06-distance-hierarchy','hound-distance')]:
        guide=guide.replace('../../ArtSource/HunyuanHound/Hound_v001/Review/'+old+'.png','../Review/'+new+'.jpg')
    text('Docs/Visual/HOUND_SURFACE_STYLE_GUIDE.md',guide)
    checkpoint=git('show',source+':Docs/THIRD_PERSON_CHECKPOINT.md').decode('utf-8-sig')
    text('Docs/THIRD_PERSON_CHECKPOINT.md','> GitHub readers: [portable current art and animation review media](Review/README.md). Native/Saved links below identify retained local evidence and may be absent from this lean snapshot.\n\n'+checkpoint)
    policy='''# GitHub publication policy

13 September 2026. Daniel uses this repository for GPT-6 Pro-assisted development and art review. Publish current source, configuration, tests, tools, design/technical documents, selected small authoring controls/receipts, and curated ordinary-image review media. Exclude archived animation drafts and large native/binary assets from the current GitHub tree. Preserve all of them in the complete local workspace.

The [review entry point](GITHUB_REVIEW.md) explains scope and the [art gallery](Review/README.md) identifies selected visible evidence. Historical source paths and tests still refer to the full authoring workspace. Their absence here is a publication decision, not deletion of local source or proof that the game can run without assets.

`Tools/PrepareGitHubReview.py prepare` creates a reviewable snapshot under ignored Saved. Its explicit `commit` step creates a separate publication branch using an alternate index and the verified current remote parent. It does not switch the authoring branch, overwrite its index, remove local files, push, or rewrite remote history. Review the manifest, then push that publication branch to main without force. Never push the full local archive commit as its parent: that would make the binary archive reachable again.

The first interrupted upload may have transferred unreferenced LFS objects; no asset-bearing commit was published. Existing remote history is retained, so this policy concerns the current tree and future publication, not a purge of already-published historical objects.
'''
    text('Docs/GITHUB_WORKSPACE.md',policy)
    ignore=git('show',source+':.gitignore').decode('utf-8-sig')
    ignore+='\n# Review publication: native assets stay in the full local authoring workspace.\nContent/\n*.blend\n*.fbx\n*.casc\n*.qrigcasc\n*.bvh\n*.npz\n*.uasset\n*.umap\n*.zip\n*.7z\n'
    text('.gitignore',ignore)
    save('Tools/PrepareGitHubReview.py',Path(__file__).read_bytes())
    for p in generated:selected.pop(p,None)
    sizes={}
    payload=('\n'.join(e['oid'] for e in selected.values())+'\n').encode()
    for line in git('cat-file','--batch-check=%(objectname) %(objectsize)',input=payload).decode().splitlines():
        oid,size=line.split();sizes[oid]=int(size)
    total=sum(sizes[e['oid']] for e in selected.values())+sum(e['bytes'] for e in generated.values())
    assert total<25_000_000,total
    assert not any(Path(p).suffix.lower() in {'.blend','.fbx','.casc','.bvh','.npz','.uasset','.umap'} for p in selected)
    plan=dict(source_commit=source,entries=selected,generated=generated,total_bytes=total,
        files=len(selected)+len(generated),omitted_source_paths=[p for p in entries if p not in selected and p not in generated])
    (OUT/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
    print(json.dumps(dict(source_commit=source,files=plan['files'],total_MB=round(total/1e6,2),media_files=len(media),
        omitted_paths=len(plan['omitted_source_paths']),review_entry=str(files/'Docs/GITHUB_REVIEW.md')),indent=2))

def commit(parent,branch):
    plan=json.loads((OUT/'plan.json').read_text())
    assert git('rev-parse','HEAD').decode().strip()==plan['source_commit'],'Authoring branch moved'
    git('cat-file','-e',parent+'^{commit}')
    assert branch=='github-review-20260913'
    check=subprocess.run(['git','show-ref','--verify','--quiet','refs/heads/'+branch],cwd=ROOT)
    assert check.returncode==1,'Preserve existing publication branch'
    entries=dict(plan['entries'])
    for p,e in plan['generated'].items():
        data=(ROOT/e['file']).read_bytes();assert sha(data)==e['sha256']
        oid=git('hash-object','-w','--no-filters','--stdin',input=data).decode().strip()
        entries[p]={'mode':'100644','oid':oid}
    env=os.environ.copy();env['GIT_INDEX_FILE']=str(OUT/'publication.index')
    git('read-tree','--empty',env=env)
    data=b''.join((e['mode']+' '+e['oid']+'\t'+p+'\0').encode() for p,e in sorted(entries.items()))
    git('update-index','-z','--index-info',input=data,env=env)
    tree=git('write-tree',env=env).decode().strip()
    message='Publish current project source and curated art review\n\nExclude native art archives and runtime binaries from the review tree. Preserve the complete authoring checkout locally. Include current combat, character and Kimodo workflow code, documentation, selected controls and bounded visual evidence.\n'
    new=git('commit-tree',tree,'-p',parent,input=message.encode()).decode().strip()
    git('update-ref','refs/heads/'+branch,new,'0'*40)
    result=dict(commit=new,branch=branch,parent=parent,source_commit=plan['source_commit'],files=plan['files'],total_bytes=plan['total_bytes'])
    (OUT/'commit.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=['prepare','commit'])
    parser.add_argument('--parent');parser.add_argument('--branch',default='github-review-20260913');args=parser.parse_args()
    if args.command=='prepare':prepare()
    else:
        assert args.parent
        commit(args.parent,args.branch)
