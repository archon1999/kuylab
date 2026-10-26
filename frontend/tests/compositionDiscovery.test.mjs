import assert from 'node:assert/strict';
import test from 'node:test';
import { compositionPage, emptyCompositionFilter, filterCompositions, libraryVariant } from '../src/modules/studio/domain/compositionLibrary.ts';
import { selectResumeStudy } from '../src/modules/studio/domain/resumeStudy.ts';

const piece = (id, title, difficulty, collection = '') => ({id,title,difficulty,collection,composer:'',subtitle:'',duration_seconds:id*30,lesson_ids:[],score_id:id,slug:title});
const pieces = [piece(1,'Clair de Lune',4,'Classics'), {...piece(2,'All in',2,'Soundtrack'),default_variant_id:'easy',variants:[{id:'easy',difficulty:2},{id:'hard',difficulty:4}]}, piece(3,'Memories',2), {...piece(4,'Für Elise',3,'Classics'),composer:'Ludwig van Beethoven'}];
const filter = (changes = {}) => ({...emptyCompositionFilter,...changes});
const lesson = (id, stages) => ({id,kind:'theory',stages:stages?.map((id) => ({id}))});

test('search matches all words across names, composer and collection, including accents', () => {
  assert.deepEqual(filterCompositions(pieces,filter({query:'fur beethoven'}),[]).map(p=>p.id),[4]);
  assert.deepEqual(filterCompositions(pieces,filter({query:'CLAIR classics'}),[]).map(p=>p.id),[1]);
  assert.equal(filterCompositions(pieces,filter({query:'unknown'}),[]).length,0);
});
test('difficulty, collection and favorites combine without changing the source order', () => {
  const before = [...pieces];
  assert.deepEqual(filterCompositions(pieces,filter({difficulty:4,collection:'Soundtrack',favoritesOnly:true}),['composition:2']).map(p=>p.id),[2]);
  assert.equal(filterCompositions(pieces,filter({difficulty:4,collection:'Soundtrack',favoritesOnly:true}),[]).length,0);
  assert.deepEqual(filterCompositions(pieces,filter({collection:'__other__'}),[]).map(p=>p.id),[3]);
  filterCompositions(pieces,filter({sort:'difficulty'}),[]);
  assert.deepEqual(pieces,before);
});
test('a hard difficulty match opens and previews the hard variant, otherwise the default', () => {
  assert.equal(libraryVariant(pieces[1],4).id,'hard');
  assert.equal(libraryVariant(pieces[1],2).id,'easy');
  assert.equal(libraryVariant(pieces[1]).id,'easy');
  assert.equal(libraryVariant(pieces[0]),undefined);
});
test('sorting uses the actual selected data and keeps the curated order by default', () => {
  assert.deepEqual(filterCompositions(pieces,filter(),[]).map(p=>p.id),[1,2,3,4]);
  assert.deepEqual(filterCompositions(pieces,filter({sort:'difficulty'}),[]).map(p=>p.id),[2,3,4,1]);
  assert.deepEqual(filterCompositions(pieces,filter({sort:'duration'}),[]).map(p=>p.id),[1,2,3,4]);
  assert.equal(filterCompositions(pieces,filter({sort:'title'}),[])[0].id,2);
});
test('pagination is bounded, retains all 38 future repertoire entries and handles empty filters', () => {
  const all = Array.from({length:38},(_,id)=>piece(id+1,'Piece '+id,3));
  const visited = [];
  for(let p=1;p<=7;p++) visited.push(...compositionPage(all,p,6).items.map(item=>item.id));
  assert.deepEqual(visited,all.map(item=>item.id));
  const last = compositionPage(all,100,6);
  assert.equal(last.page,7); assert.equal(last.from,37); assert.equal(last.to,38);
  assert.equal(compositionPage([],7,6).page,1);
  assert.equal(compositionPage(all,NaN,0).pageSize,6);
  assert.equal(compositionPage(all,-2,12).items.length,12);
});
test('resume skips the most recent mastered lesson and composition entries', () => {
  const items = [lesson('done'),lesson('ongoing')];
  const recents = [{id:'composition:1'},{id:'done'},{id:'missing'},{id:'ongoing'}];
  assert.equal(selectResumeStudy(items,recents,{done:'mastered',ongoing:'learning'},{}).item.id,'ongoing');
  assert.equal(selectResumeStudy(items,recents,{done:'mastered',ongoing:'mastered'},{}),null);
});
test('resume moves away from a remembered mastered stage and keeps unfinished remembered work', () => {
  const item = lesson('course',['one','two','three']);
  const recents = [{id:'course'}];
  const progress = {one:'mastered',two:'struggling'};
  assert.equal(selectResumeStudy([item],recents,progress,{course:'one'}).stage.id,'two');
  assert.equal(selectResumeStudy([item],recents,progress,{course:'three'}).stage.id,'three');
  assert.equal(selectResumeStudy([item],recents,{one:'mastered',two:'mastered',three:'mastered'},{course:'three'}),null);
});
test('recent unfinished theory stays eligible without forcing a new study schedule', () => {
  assert.equal(selectResumeStudy([lesson('new')],[{id:'new'}],{},{}).item.id,'new');
  assert.equal(selectResumeStudy([lesson('new')],[],{},{}),null);
});
