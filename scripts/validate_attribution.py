"""Validate source-free sentence attribution; optional local source proves offsets."""
import argparse,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def validate(source=None):
 data=ROOT/'books/yishizhizun';index=load(data/'evidence-index.json');chapters={c['id']:c for c in index['chapters']}
 originals={}
 if source:
  book=load(source/'book.json');assert book['source_sha256']==index['source_sha256']
  originals={c['id']:c for c in book['chapters']}
 summary=load(data/'reviews/attribution-summary.json');actual=[]
 reviewed={load(p)['chapter_id'] for p in (data/'chapter_direction').glob('*.json') if load(p).get('attribution')}
 assert reviewed=={e['chapter_id'] for e in summary['chapters']}, 'Attribution summary coverage mismatch'
 kinds={'narration','spoken_dialogue','inner_speech','mental_visualization_voice','telepathic_dialogue'}
 for entry in summary['chapters']:
  cid=entry['chapter_id'];plan=load(data/'chapter_direction'/(cid+'.json'));c=chapters[cid]
  assert plan['chapter_sha256']==c['text_sha256']
  attr=plan['attribution'];assert attr['text_included'] is False
  assert len(attr['paragraphs'])==c['paragraph_count'];count=questions=0
  for i,p in enumerate(attr['paragraphs'],1):
   assert p['reference']==f'{cid}:p{i:04}'
   assert p['length']==c['paragraph_lengths'][i-1]
   if originals:
    text=originals[cid]['paragraphs'][i-1]
    assert p['sha256']==hashlib.sha256(text.encode()).hexdigest()
    assert p['length']==len(text)
   last=0
   for j,u in enumerate(p['units'],1):
    assert u['unit_id']==f'{cid}:p{i:04}:u{j:03}'
    assert u['start']==last and last<u['end']<=p['length'],u['unit_id']
    assert u['kind'] in kinds and u['speaker'] and u['surface_identity']
    assert not any(k in u for k in ('text','source_text','content'))
    last=u['end'];count+=1
   assert last==p['length']
   questions+=int('open_question' in p)
  got={'chapter_id':cid,'paragraphs':len(attr['paragraphs']),'units':count,'open_questions':questions}
  assert got==entry,(got,entry)
  assert plan['line_level_attribution']==('reviewed_with_open_questions' if questions else 'reviewed_source_spans')
  actual.append(got)
 # Editorial regression cases: quoted terminology and visualized voice must not
 # accidentally become speech; a disguised actor must retain the public identity.
 def units(ch,p):return load(data/'chapter_direction'/f'v04-c{ch:04}.json')['attribution']['paragraphs'][p-1]['units']
 assert all(u['kind']=='narration' for u in units(121,2))
 assert any(u['kind']=='mental_visualization_voice' for u in units(124,43))
 assert all(u['kind']!='spoken_dialogue' for u in units(124,43))
 assert any(u['speaker']=='gu_xiaosang' and u['surface_identity']=='shangshui_xianzi' for u in units(125,29))
 assert any(u['speaker']=='gu_xiaosang' and u['surface_identity']=='gu_xiaosang' for u in units(125,93))
 assert any(u['speaker']=='female_voice_unnamed' for u in units(125,69))
 assert any(u['speaker']=='meng_qi' and u['kind']=='inner_speech' for u in units(126,26))
 assert any(u['speaker']=='meng_qi' and u['kind']=='spoken_dialogue' for u in units(126,26))
 assert any(u['kind']=='telepathic_dialogue' for u in units(127,61))
 assert all(u['kind']!='spoken_dialogue' for u in units(127,62))
 assert any(u['speaker']=='liu_shuyu' for u in units(129,45))
 return {'status':'ok','chapters':len(actual),'paragraphs':sum(e['paragraphs'] for e in actual),'units':sum(e['units'] for e in actual),'open_questions':sum(e['open_questions'] for e in actual),'source_offsets_verified':bool(originals),'scope':'coverage_and_selected_editorial_regressions_not_full_semantic_proof'}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--source',type=Path);args=p.parse_args();print(json.dumps(validate(args.source)))
