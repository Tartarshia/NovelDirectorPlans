"""Export, validate and archive source-free director plans. Python standard library only."""
import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'books' / 'yishizhizun'

def dump(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((json.dumps(data, ensure_ascii=False, indent=2)+'\n').encode('utf-8'))

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def export(source):
    book = json.loads((source/'book.json').read_text(encoding='utf-8'))
    selected = [source/n for n in ('wiki.md','progress.json','identity-events.json','source-issues.json','inventory.json')]
    for folder, pattern in [('volumes','*.md'),('batches','*.md'),('chapter_direction','*.json'),('reading_receipts','*.json'),('characters','*.md'),('reviews','*.md'),('reviews','*.json')]:
        selected.extend(sorted((source/folder).glob(pattern)))
    payload = {}
    for p in selected:
        text = p.read_text(encoding='utf-8')
        # Fail before writing or publishing anything containing local paths or common secrets.
        if re.search(r'(?i)([a-z]:[\\/]|/Users/|/home/|gh[pousr]_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9_-]{20,}|BEGIN .*PRIVATE KEY)', text):
            raise ValueError('Privacy check failed: '+p.name)
        payload[p.relative_to(source)] = text
    combined = '\n'.join(payload.values())
    for c in book['chapters']:
        for paragraph in c['paragraphs']:
            if len(paragraph) >= 100 and paragraph in combined:
                raise ValueError('Long verbatim source paragraph in export: '+c['id'])
    DATA.mkdir(parents=True, exist_ok=True)
    for rel, text in payload.items():
        target = DATA/rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(text.encode('utf-8'))
    attribution_ids = {json.loads(t)['chapter_id'] for rel,t in payload.items()
                       if rel.parts[0]=='chapter_direction' and json.loads(t).get('attribution')}
    index = {k:book[k] for k in ('schema_version','source_sha256','volumes')}
    index['chapters'] = [{**{k:c[k] for k in ('id','volume_id','title','kind','character_count','text_sha256')},
                          'paragraph_count':len(c['paragraphs']),
                          **({'paragraph_lengths':[len(p) for p in c['paragraphs']]} if c['id'] in attribution_ids else {}),
                          'separator_paragraphs':[i for i,p in enumerate(c['paragraphs'],1) if re.fullmatch(r'[.…\s]+',p)]}
                         for c in book['chapters']]
    dump(DATA/'evidence-index.json', index)
    files = sorted(p for p in DATA.rglob('*') if p.is_file())
    progress = json.loads((DATA/'progress.json').read_text(encoding='utf-8'))
    dump(ROOT/'manifest.json', {'schema_version':1,'package':'novel-director-plans',
        'status':'in_progress','source_included':False,'through_chapter':progress['close_read_chapter_ids'][-1],
        'read_entries':progress['close_read_count'],'source_sha256':book['source_sha256'],
        'files':{p.relative_to(ROOT).as_posix():digest(p) for p in files}})
    validate()

def validate():
    manifest=json.loads((ROOT/'manifest.json').read_text(encoding='utf-8'))
    actual={p.relative_to(ROOT).as_posix() for p in DATA.rglob('*') if p.is_file()}
    assert actual==set(manifest['files']), 'Unexpected or missing package data'
    for rel, sha in manifest['files'].items():
        assert digest(ROOT/rel)==sha, rel
    index=json.loads((DATA/'evidence-index.json').read_text(encoding='utf-8'))
    chapters={c['id']:c for c in index['chapters']}
    progress=json.loads((DATA/'progress.json').read_text(encoding='utf-8'))
    read=progress['close_read_chapter_ids']
    assert read==list(chapters)[:len(read)]
    assert len(read)==progress['close_read_count']==manifest['read_entries']
    assert progress['next_chapter_id']==list(chapters)[len(read)] if len(read)<len(chapters) else True
    assert progress['source_sha256']==index['source_sha256']==manifest['source_sha256']
    assert sum(chapters[c]['character_count'] for c in read)==progress['close_read_characters']
    plans=list((DATA/'chapter_direction').glob('*.json'))
    assert len(plans)==len(read)==progress['chapter_scene_drafts']
    seen=set()
    for path in plans:
        plan=json.loads(path.read_text(encoding='utf-8')); cid=plan['chapter_id']; c=chapters[cid]
        assert cid in read and cid not in seen
        seen.add(cid)
        assert plan['chapter_sha256']==c['text_sha256'] and plan['source_sha256']==index['source_sha256']
        covered=set();last=0
        for scene in plan['scenes']:
            start,end=scene['paragraph_start'],scene['paragraph_end']
            assert last<start<=end<=c['paragraph_count'];last=end
            covered.update(range(start,end+1))
            for ref in scene['evidence']:
                assert ref.startswith(cid+':p') and start<=int(ref.split(':p')[1])<=end
        assert covered | set(c['separator_paragraphs'])==set(range(1,c['paragraph_count']+1))
    for p in DATA.rglob('*'):
        if not p.is_file(): continue
        text=p.read_text(encoding='utf-8')
        for cid,para in re.findall(r'(v\d{2}-c\d{4}):p(\d{4})',text):
            assert cid in read and 1<=int(para)<=chapters[cid]['paragraph_count'], (p.name,cid,para)
    for p in (DATA/'reading_receipts').glob('*.json'):
        receipt=json.loads(p.read_text(encoding='utf-8'))
        assert receipt['source_sha256']==index['source_sha256']
        for c in receipt['chapters']:
            assert c['id'] in read and c['sha256']==chapters[c['id']]['text_sha256']
            assert c['paragraph_count']==chapters[c['id']]['paragraph_count']
    if (DATA/'reviews/attribution-summary.json').exists():
        from validate_attribution import validate as validate_attribution
        validate_attribution()
    print(json.dumps({'status':'ok','read_entries':len(read),'plans':len(plans),'data_files':len(actual),
                      'scope':'source_free_integrity_not_semantic_review'}))

def archive():
    validate()
    manifest=json.loads((ROOT/'manifest.json').read_text(encoding='utf-8'))
    dest=ROOT/'dist'/('novel-director-plans-'+manifest['through_chapter']+'.zip')
    dest.parent.mkdir(exist_ok=True)
    names=list(manifest['files'])+['manifest.json','README.md','WORKFLOW.md','HANDOFF.md','scripts/package.py','scripts/validate_attribution.py']
    with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as z:
        for name in sorted(names): z.write(ROOT/name,name)
    with zipfile.ZipFile(dest) as z:
        assert set(z.namelist())==set(names)
        assert z.testzip() is None
        for name in manifest['files']:
            assert hashlib.sha256(z.read(name)).hexdigest()==manifest['files'][name]
    print(dest.name, digest(dest))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['export','validate','archive'])
    parser.add_argument('--source',type=Path)
    args=parser.parse_args()
    if args.command=='export':
        if not args.source: parser.error('export requires --source')
        export(args.source.resolve())
    elif args.command=='validate': validate()
    else: archive()
