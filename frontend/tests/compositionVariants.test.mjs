import assert from 'node:assert/strict';
import test from 'node:test';
import { selectCompositionVariant, compositionPlaybackContext, compositionPositionKeys, compositionResumePosition, compositionNotebookContext, compositionVariantStartPosition, compositionNoteTarget } from '../src/modules/studio/domain/studio.logic.ts';
import { mapStudioCatalog } from '../src/modules/studio/data-access/mappers/studio.mapper.ts';
import { parseRoute, routePath } from '../src/shared/routing/paths.ts';

const piece = {
  id: 8, default_variant_id: 'easy', score_id: 80, lesson_ids: ['lesson:all-in:chord-shapes'],
  variants: [{ id: 'easy', title: 'Easy', description: 'Simpler LH', score_id: 80, duration_seconds: 287.8 },
             { id: 'hard', title: 'Hard', description: 'Complete LH', score_id: 81, duration_seconds: 287.8 }],
};

test('explicit variant wins over remembered choice; defaults and foreign choices are safe', () => {
  assert.equal(selectCompositionVariant(piece, 'hard', 'easy').score_id, 81);
  assert.equal(selectCompositionVariant(piece, null, 'hard').score_id, 81);
  assert.equal(selectCompositionVariant(piece, 'removed', 'removed').score_id, 80);
  assert.equal(selectCompositionVariant({ ...piece, default_variant_id: 'removed' }).score_id, 80);
  assert.equal(selectCompositionVariant({ id: 1, score_id: 5 }), undefined);
  assert.equal(selectCompositionVariant(undefined, 'easy'), undefined);
});

test('playback settings and positions separate variants while old composition contexts stay stable', () => {
  assert.equal(compositionPlaybackContext(piece, 'easy'), 'composition:8:variant:easy');
  assert.equal(compositionPlaybackContext(piece, 'hard'), 'composition:8:variant:hard');
  assert.equal(compositionPlaybackContext({ id: 1, score_id: 5 }, 'hard'), 'composition:1');
  assert.equal(compositionPlaybackContext(piece, 'unknown'), 'composition:8');
});

test('clean variant deep links retain a precise timestamp, including browser back and refresh', () => {
  for (const variant of ['easy', 'hard']) {
    const url = routePath('practice', { composition: 8, variant, at: 67.040048 });
    const parsed = parseRoute(...url.split('?').map((v, i) => i ? '?' + v : v));
    assert.equal(url, `/practice/8/variants/${variant}?t=67.040048`);
    assert.equal(parsed.page, 'practice');
    assert.equal(parsed.params.get('variant'), variant);
    assert.equal(parsed.params.get('at'), '67.040048');
    assert.equal(routePath(parsed.page, parsed.params), url);
  }
  for (const path of ['/practice/8/variants', '/practice/8/variants/hard/extra', '/practice/8/other/hard'])
    assert.equal(parseRoute(path).page, 'notFound');
  assert.equal(routePath('practice', { composition: 1 }), '/practice/1');
  assert.equal(routePath('detail', { composition: 8, variant: 'hard' }), '/compositions/8');
});

test('catalog mapping clones variant metadata and keeps a single shared lesson list', () => {
  const dto = { revision: 'v9', compositions: [piece], lessons: [], exercises: [], theory: [], categories: [], goals: [] };
  const mapped = mapStudioCatalog(dto);
  assert.equal(mapped.compositions.length, 1);
  assert.deepEqual(mapped.compositions[0].variants, piece.variants);
  mapped.compositions[0].variants[0].title = 'Changed';
  mapped.compositions[0].lesson_ids.push('new');
  assert.equal(piece.variants[0].title, 'Easy');
  assert.equal(piece.lesson_ids.length, 1);
});

const revised = {...piece,slug:'all-in',playback_revision:'0123456789abcdef',
  variants:piece.variants.map((variant,index)=>({...variant,playback_revision:index?'fedcba9876543210':'0123456789abcdef'}))};

test('replaced source editions never inherit or overwrite old positions, including single-performance works',()=>{
  const single={id:16,score_id:900,slug:'ode-to-joy',playback_revision:'1122334455667788'};
  const historical=Object.freeze({'composition:16':123,'composition:8':100,'composition:8:variant:hard':80});
  assert.equal(compositionPlaybackContext(single),'composition:16:source:1122334455667788');
  assert.equal(compositionResumePosition(single,historical),0);
  assert.deepEqual(compositionPositionKeys(single),['composition:16:source:1122334455667788']);
  assert.equal(compositionResumePosition(revised,historical,'hard'),0);
  assert.deepEqual(compositionPositionKeys(revised,'hard'),['composition:8:source:fedcba9876543210']);
  const saved={...historical,'composition:8:source:fedcba9876543210':29};
  assert.equal(compositionResumePosition(revised,saved,'hard'),29);
  assert.equal(compositionResumePosition(revised,saved,'easy'),0);
  assert.equal(compositionResumePosition({...revised,playback_revision:'aabbccddeeff0011',variants:undefined},saved),0);
  assert.equal(historical['composition:16'],123);
});

test('unchanged editions retain their legacy resume and notebook contracts',()=>{
  assert.equal(compositionResumePosition(piece,{'composition:8':24},'easy'),24);
  assert.equal(compositionResumePosition(piece,{'composition:8':24,'composition:8:variant:easy':12},'easy'),12);
  assert.deepEqual(compositionPositionKeys(piece,'easy'),['composition:8:variant:easy','composition:8']);
  assert.equal(compositionNotebookContext(piece,'easy'),'composition:8');
  assert.equal(compositionNotebookContext(revised,'easy'),'composition:8:source:0123456789abcdef');
  assert.equal(compositionNotebookContext(revised,'hard'),'composition:8:source:fedcba9876543210');
});

test('switching independent recordings resumes the target rather than transferring another performance timestamp',()=>{
  const position=compositionVariantStartPosition(revised,'hard',67.040049);
  assert.equal(position,null);
  assert.equal(routePath('practice',{composition:revised.id,variant:'hard',at:position}),'/practice/8/variants/hard');
  const saved=Object.freeze({'composition:8:source:fedcba9876543210':29});
  assert.equal(compositionResumePosition(revised,saved,'hard'),29);
  assert.equal(compositionResumePosition(revised,{},'hard'),0);
  assert.equal(compositionVariantStartPosition({...revised,playback_revision:undefined},'hard',67),null);
  const aligned=compositionVariantStartPosition(piece,'hard',67.040049);
  assert.equal(aligned,67.04);
  assert.equal(routePath('practice',{composition:piece.id,variant:'hard',at:aligned}),'/practice/8/variants/hard?t=67.04');
});

test('timestamp notes select the matching current source and variant; older sources link to details safely',()=>{
  const current=compositionNoteTarget([revised],'composition:8:source:fedcba9876543210');
  assert.equal(current.currentSource,true);
  assert.equal(current.variant.id,'hard');
  assert.equal(routePath('practice',{composition:current.composition.id,variant:current.variant.id,at:32}),'/practice/8/variants/hard?t=32');
  for(const old of ['composition:8','composition:8:variant:hard','composition:8:source:aabbccddeeff0011','composition:8:source:unknown']){
    const target=compositionNoteTarget([revised],old);
    assert.equal(target.currentSource,false);
    assert.equal(routePath('detail',{compositionSlug:target.composition.slug}),'/compositions/all-in');
  }
  assert.equal(compositionNoteTarget([piece],'composition:8').currentSource,true);
  assert.equal(compositionNoteTarget([revised],'theory:triads'),undefined);
  assert.equal(compositionNoteTarget([revised],'composition:999:source:fedcba9876543210'),undefined);
});

test('transport mapping preserves reviewed revisions and rejects invalid context tokens',()=>{
  const catalog=(composition)=>({revision:'v10',compositions:[composition],lessons:[],exercises:[],theory:[],categories:[],goals:[]});
  const mapped=mapStudioCatalog(catalog(revised)).compositions[0];
  assert.equal(mapped.playback_revision,'0123456789abcdef');
  assert.equal(mapped.variants[1].playback_revision,'fedcba9876543210');
  const malformed=mapStudioCatalog(catalog({...piece,playback_revision:'invalid',variants:piece.variants.map(v=>({...v,playback_revision:'../unsafe'}))})).compositions[0];
  assert.equal(malformed.playback_revision,undefined);
  assert.equal(malformed.variants[0].playback_revision,undefined);
});

test('a retained lesson edition keeps its positions, notes and timestamp links when a recording is added',()=>{
  const supplemented={id:9,default_variant_id:'original',variants:[
    {id:'original',title:'Lesson edition',score_id:20},
    {id:'fabrizio-caligaris',title:'A Time for Us',score_id:21,playback_revision:'1122334455667788'},
  ]};
  const saved=Object.freeze({'composition:9':24,'composition:9:source:1122334455667788':7});
  assert.equal(compositionPlaybackContext(supplemented,'original'),'composition:9');
  assert.deepEqual(compositionPositionKeys(supplemented,'original'),['composition:9']);
  assert.equal(compositionResumePosition(supplemented,saved,'original'),24);
  assert.equal(compositionResumePosition(supplemented,saved,'fabrizio-caligaris'),7);
  assert.equal(compositionNotebookContext(supplemented,'original'),'composition:9');
  assert.equal(compositionNotebookContext(supplemented,'fabrizio-caligaris'),'composition:9:source:1122334455667788');
  const oldNote=compositionNoteTarget([supplemented],'composition:9');
  assert.equal(oldNote.currentSource,true);
  assert.equal(oldNote.variant.id,'original');
  assert.equal(selectCompositionVariant(supplemented,null,'fabrizio-caligaris',true).id,'original');
  assert.equal(selectCompositionVariant(supplemented,null,'fabrizio-caligaris').id,'fabrizio-caligaris');
  assert.equal(selectCompositionVariant(supplemented,'fabrizio-caligaris','original',true).id,'fabrizio-caligaris');
  assert.equal(compositionVariantStartPosition(supplemented,'original',67),null);
  assert.equal(compositionVariantStartPosition(supplemented,'fabrizio-caligaris',67),null);
});
