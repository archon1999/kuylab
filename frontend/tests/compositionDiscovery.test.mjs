import assert from 'node:assert/strict';
import test from 'node:test';
import { compositionPage, emptyCompositionFilter, filterCompositions, libraryVariant, compositionGroups, compositionCollections, inferCompositionGroup, collectionForGroup, compositionCollectionLabel, compositionAttribution } from '../src/modules/studio/domain/compositionLibrary.ts';
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

test('another performance title and performer find the existing work without duplicating it', () => {
  const work={...piece(9,'What Is a Youth',4,'Romeo & Juliet'),variants:[
    {id:'original',title:'Lesson edition'},
    {id:'fabrizio-caligaris',title:'A Time for Us · Fabrizio Caligaris',description:'The Romeo & Juliet love theme'},
  ]};
  assert.deepEqual(filterCompositions([work],filter({query:'a time for us'}),[]).map(p=>p.id),[9]);
  assert.deepEqual(filterCompositions([work],filter({query:'fabrizio caligaris'}),[]).map(p=>p.id),[9]);
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

const classified=[
  {...piece(1,'Moonlight',4,'Sonata Op.27'),library_group:{id:'classical',label:'Classics'},library_collection:{id:'beethoven',label:'Beethoven'}},
  {...piece(2,'Ode to Joy',2,'Symphony No.9'),library_group:{id:'classical',label:'Classics'},library_collection:{id:'beethoven',label:'Beethoven'}},
  {...piece(3,'Senya',4,'Naruto Shippuden OST'),library_group:{id:'anime',label:'Anime'},library_collection:{id:'naruto',label:'Naruto'}},
  {...piece(4,'Epitaph',3,'Shiki OST'),library_group:{id:'anime',label:'Anime'},library_collection:{id:'shiki',label:'Shiki'}},
  {...piece(5,'Halo',3),library_group:{id:'songs',label:'Songs'},library_collection:{id:'beyonce',label:'Beyoncé'}},
];

test('two-level options collapse album/opus metadata and never expose a flat collection list by default',()=>{
  assert.deepEqual(compositionGroups(classified).map(v=>v.id),['anime','classical','songs']);
  assert.deepEqual(compositionCollections(classified,'classical'),[{id:'beethoven',label:'Beethoven'}]);
  assert.deepEqual(compositionCollections(classified,'anime').map(v=>v.id),['naruto','shiki']);
  assert.deepEqual(compositionCollections(classified,''),[]);
  assert.equal(collectionForGroup(classified,'anime','naruto'),'naruto');
  assert.equal(collectionForGroup(classified,'classical','naruto'),'');
  assert.equal(collectionForGroup(classified,'','naruto'),'');
});

test('canonical collection IDs and exact legacy album URLs both filter correctly and infer a display parent',()=>{
  assert.deepEqual(filterCompositions(classified,filter({group:'classical',collection:'beethoven'}),[]).map(p=>p.id),[1,2]);
  assert.deepEqual(filterCompositions(classified,filter({collection:'Symphony No.9'}),[]).map(p=>p.id),[2]);
  assert.equal(inferCompositionGroup(classified,'Symphony No.9'),'classical');
  assert.equal(inferCompositionGroup(classified,'beethoven'),'classical');
  assert.equal(inferCompositionGroup(classified,'unknown'),'');
  assert.equal(compositionCollectionLabel(classified,'Symphony No.9'),'Beethoven');
  assert.equal(collectionForGroup(classified,'classical','Symphony No.9'),'Symphony No.9');
});

test('taxonomy combines with difficulty/favorites and localized artist names remain searchable with a blank composer',()=>{
  assert.deepEqual(filterCompositions(classified,filter({group:'anime',collection:'naruto',difficulty:4,favoritesOnly:true}),['composition:3']).map(p=>p.id),[3]);
  assert.equal(filterCompositions(classified,filter({group:'classical',collection:'naruto'}),[]).length,0);
  assert.deepEqual(filterCompositions(classified,filter({query:'beyonce'}),[]).map(p=>p.id),[5]);
  assert.deepEqual(filterCompositions(classified,filter({query:'classics Beethoven'}),[]).map(p=>p.id),[1,2]);
});

const epic = [
  {...piece(1,'Lion Heart',4),composer:'Ivan Torrent',library_group:{id:'epic',label:'Epic music'},library_collection:{id:'ivan-torrent',label:'Ivan Torrent'}},
  {...piece(2,'Red',4,'Humanity — Chapter II'),composer:'Thomas Bergersen',library_group:{id:'epic',label:'Epic music'},library_collection:{id:'two-steps-from-hell',label:'Two Steps From Hell'}},
  {...piece(3,'Victory',4,'Battlecry'),composer:'Thomas Bergersen',library_group:{id:'epic',label:'Epic music'},library_collection:{id:'two-steps-from-hell',label:'Two Steps From Hell'}},
];

test('card and detail attribution lead with the curated artist and retain only distinct composer credits',()=>{
  const before = structuredClone(epic);
  assert.deepEqual(compositionAttribution(epic[0]),{category:'Ivan Torrent',composer:''});
  assert.deepEqual(compositionAttribution(epic[1]),{category:'Two Steps From Hell',composer:'Thomas Bergersen'});
  assert.deepEqual(compositionAttribution({...piece(4,'Untyped',2,'Original collection'),composer:'Original composer'}),{category:'Original collection',composer:'Original composer'});
  assert.deepEqual(compositionAttribution({...piece(5,'Unclassified',2),composer:' Artist '}),{category:'Artist',composer:''});
  assert.deepEqual(compositionAttribution(piece(6,'Unknown',2)),{category:'',composer:''});
  assert.deepEqual(epic,before);
});

test('Thomas Bergersen works use a single Two Steps From Hell collection while composer search and old links keep working',()=>{
  assert.deepEqual(compositionCollections(epic,'epic'),[{id:'ivan-torrent',label:'Ivan Torrent'},{id:'two-steps-from-hell',label:'Two Steps From Hell'}]);
  assert.deepEqual(filterCompositions(epic,filter({group:'epic',collection:'two-steps-from-hell'}),[]).map(p=>p.id),[2,3]);
  assert.deepEqual(filterCompositions(epic,filter({query:'Thomas Bergersen'}),[]).map(p=>p.id),[2,3]);
  assert.deepEqual(filterCompositions(epic,filter({collection:'thomas-bergersen'}),[]).map(p=>p.id),[2,3]);
  assert.equal(compositionCollectionLabel(epic,'thomas-bergersen'),'Two Steps From Hell');
  assert.equal(inferCompositionGroup(epic,'thomas-bergersen'),'epic');
  assert.equal(collectionForGroup(epic,'epic','thomas-bergersen'),'thomas-bergersen');
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
