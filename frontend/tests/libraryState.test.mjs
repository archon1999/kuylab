import assert from 'node:assert/strict';
import test from 'node:test';
import { hasLibraryQuery, readLibraryQuery, libraryQuery, normalizeLibraryState } from '../src/modules/studio/domain/compositionLibraryState.ts';
import { createLibraryStateRepository } from '../src/modules/studio/data-access/repository/library-state.repository.ts';
import { setAccountScope } from '../src/shared/lib/accountScope.ts';
import { parseRoute, routePath } from '../src/shared/routing/paths.ts';
import { isPlainLinkClick } from '../src/shared/routing/linkIntent.ts';
import { canonicalEntryState, isCanonicalEntry } from '../src/shared/routing/historyState.ts';

test('search, filters, order, page and page size round-trip through a canonical library URL',()=>{
  const state=normalizeLibraryState({filter:{query:'Für Elise & C♯',difficulty:4,collection:'Romeo & Juliet · 1968',favoritesOnly:true,sort:'duration'},page:3,size:12});
  const path=routePath('library',libraryQuery(state));
  const parsed=parseRoute('/compositions',path.slice(path.indexOf('?')));
  assert.equal(parsed.page,'library'); assert.equal(hasLibraryQuery(parsed.params),true);
  assert.deepEqual(readLibraryQuery(parsed.params),state);
  assert.equal(routePath('library',parsed.params),path);
});

test('invalid URL values cannot create unbounded pages, unsafe sizes or unknown sort modes',()=>{
  const state=readLibraryQuery(new URLSearchParams('p=Infinity&size=999&difficulty=9&sort=script&favorites=true&q=abc%00def'));
  assert.deepEqual(state,{filter:{query:'abcdef',difficulty:0,group:'',collection:'',favoritesOnly:false,sort:'curated'},page:1,size:6,view:'list'});
  assert.equal(readLibraryQuery(new URLSearchParams('p=-2&size=24')).page,1);
  assert.equal(readLibraryQuery(new URLSearchParams('p=999999999')).page,100000);
  assert.equal(hasLibraryQuery(new URLSearchParams('utm_source=example')),false);
});

test('default filters and pagination stay out of URLs; only changed values are shareable',()=>{
  assert.equal(routePath('library',libraryQuery(normalizeLibraryState(null))),'/compositions');
  assert.equal(routePath('library',libraryQuery(normalizeLibraryState({filter:{query:'Yiruma'}}))),'/compositions?q=Yiruma');
  assert.equal(routePath('library',libraryQuery(normalizeLibraryState({page:2}))),'/compositions?p=2');
  assert.equal(routePath('library',libraryQuery(normalizeLibraryState({size:12}))),'/compositions?size=12');
  const defaults=readLibraryQuery(new URLSearchParams('p=1&size=6&sort=curated&difficulty=0&favorites=0'));
  assert.equal(routePath('library',libraryQuery(defaults)),'/compositions');
});

test('clean default history entries override later session filters; fresh visits restore the session',()=>{
  const saved=normalizeLibraryState({filter:{query:'Yiruma'},page:2,size:12});
  const resolve=(params,history=null)=>hasLibraryQuery(params)||isCanonicalEntry(history,'/compositions')?readLibraryQuery(params):saved;
  assert.deepEqual(resolve(new URLSearchParams()),saved);
  assert.deepEqual(resolve(new URLSearchParams('p=1&size=6')),normalizeLibraryState(null));
  const entry=canonicalEntryState({other:'preserved'},'/compositions');
  assert.equal(entry.other,'preserved');
  assert.deepEqual(resolve(new URLSearchParams(),entry),normalizeLibraryState(null));
  assert.equal(isCanonicalEntry(entry,'/exercises'),false);
  assert.equal(isCanonicalEntry(null,'/compositions'),false);
  assert.equal(isCanonicalEntry({kuylabCanonicalPath:42},'/compositions'),false);
});

test('tab session state is isolated per account and survives returning to the library',t=>{
  const map=new Map(); const storage={getItem:key=>map.get(key)||null,setItem:(key,value)=>map.set(key,value)};
  const port=createLibraryStateRepository(storage); t.after(()=>setAccountScope(null));
  const state=normalizeLibraryState({filter:{query:'Chopin',group:'classical',collection:'chopin',sort:'title'},page:2,size:12,view:'grid'});
  setAccountScope(10); port.write(state);
  assert.deepEqual(createLibraryStateRepository(storage).read(),state);
  setAccountScope(11); assert.deepEqual(port.read(),normalizeLibraryState(null));
  setAccountScope(10); assert.deepEqual(port.read(),state);
});

test('grid links retain filters and pagination while list remains the clean default',()=>{
  const grid=normalizeLibraryState({filter:{query:'Naruto',difficulty:3},page:2,size:12,view:'grid'});
  const path=routePath('library',libraryQuery(grid));
  assert.equal(path,'/compositions?q=Naruto&difficulty=3&p=2&size=12&view=grid');
  const parsed=parseRoute('/compositions',path.slice(path.indexOf('?')));
  assert.deepEqual(readLibraryQuery(parsed.params),grid);
  assert.equal(hasLibraryQuery(new URLSearchParams('view=grid')),true);
  assert.equal(routePath('library',libraryQuery(normalizeLibraryState({view:'list'}))),'/compositions');
  assert.equal(readLibraryQuery(new URLSearchParams('view=invalid')).view,'list');
  assert.equal(normalizeLibraryState({page:3}).view,'list');
});

test('blocked or corrupted session storage leaves URL-driven filtering usable',()=>{
  const denied=createLibraryStateRepository({getItem(){throw new Error('blocked')},setItem(){throw new Error('blocked')}});
  assert.deepEqual(denied.read(),normalizeLibraryState(null));
  assert.doesNotThrow(()=>denied.write(normalizeLibraryState(null)));
  assert.deepEqual(createLibraryStateRepository({getItem:()=>'{bad',setItem(){}}).read(),normalizeLibraryState(null));
});

test('hierarchy filters share stable IDs across localized URLs while default group stays omitted',()=>{
  const state=normalizeLibraryState({filter:{group:'anime',collection:'naruto'},page:3,view:'grid'});
  const path=routePath('library',libraryQuery(state));
  assert.equal(path,'/compositions?group=anime&collection=naruto&p=3&view=grid');
  assert.deepEqual(readLibraryQuery(new URLSearchParams(path.split('?')[1])),state);
  assert.equal(hasLibraryQuery(new URLSearchParams('group=classical')),true);
  assert.equal(routePath('library',libraryQuery(normalizeLibraryState({filter:{group:''}}))),'/compositions');
  const legacy=readLibraryQuery(new URLSearchParams('collection=Winter%20Sonata'));
  assert.equal(legacy.filter.collection,'Winter Sonata');
  assert.equal(legacy.filter.group,'');
});

test('the former Thomas Bergersen collection migrates in URLs and saved sessions without losing browsing state',()=>{
  const params=new URLSearchParams('group=epic&collection=thomas-bergersen&q=Red&p=2&view=grid');
  const state=readLibraryQuery(params);
  assert.equal(state.filter.collection,'two-steps-from-hell');
  assert.equal(routePath('library',libraryQuery(state)),'/compositions?q=Red&group=epic&collection=two-steps-from-hell&p=2&view=grid');
  const legacySession={...state,filter:{...state.filter,collection:'thomas-bergersen'}};
  assert.deepEqual(normalizeLibraryState(legacySession),state);
});

test('Ctrl/Command/middle/Shift clicks keep browser new-tab behavior',()=>{
  const plain={button:0,ctrlKey:false,metaKey:false,shiftKey:false,altKey:false,defaultPrevented:false};
  assert.equal(isPlainLinkClick(plain),true);
  for(const variant of [{ctrlKey:true},{metaKey:true},{shiftKey:true},{altKey:true},{button:1},{button:2},{defaultPrevented:true}])
    assert.equal(isPlainLinkClick({...plain,...variant}),false);
  assert.equal(routePath('practice',{composition:15,variant:'hard'}),'/practice/15/variants/hard');
});
