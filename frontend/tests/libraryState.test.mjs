import assert from 'node:assert/strict';
import test from 'node:test';
import { hasLibraryQuery, readLibraryQuery, libraryQuery, normalizeLibraryState } from '../src/modules/studio/domain/compositionLibraryState.ts';
import { createLibraryStateRepository } from '../src/modules/studio/data-access/repository/library-state.repository.ts';
import { setAccountScope } from '../src/shared/lib/accountScope.ts';
import { parseRoute, routePath } from '../src/shared/routing/paths.ts';
import { isPlainLinkClick } from '../src/shared/routing/linkIntent.ts';

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
  assert.deepEqual(state,{filter:{query:'abcdef',difficulty:0,collection:'',favoritesOnly:false,sort:'curated'},page:1,size:6});
  assert.equal(readLibraryQuery(new URLSearchParams('p=-2&size=24')).page,1);
  assert.equal(readLibraryQuery(new URLSearchParams('p=999999999')).page,100000);
  assert.equal(hasLibraryQuery(new URLSearchParams('utm_source=example')),false);
});

test('an explicit default URL overrides old session filters; fresh visits can restore the session',()=>{
  const saved=normalizeLibraryState({filter:{query:'Yiruma'},page:2,size:12});
  const resolve=params=>hasLibraryQuery(params)?readLibraryQuery(params):saved;
  assert.deepEqual(resolve(new URLSearchParams()),saved);
  assert.deepEqual(resolve(new URLSearchParams('p=1&size=6')),normalizeLibraryState(null));
});

test('tab session state is isolated per account and survives returning to the library',t=>{
  const map=new Map(); const storage={getItem:key=>map.get(key)||null,setItem:(key,value)=>map.set(key,value)};
  const port=createLibraryStateRepository(storage); t.after(()=>setAccountScope(null));
  const state=normalizeLibraryState({filter:{query:'Chopin',sort:'title'},page:2,size:12});
  setAccountScope(10); port.write(state);
  assert.deepEqual(createLibraryStateRepository(storage).read(),state);
  setAccountScope(11); assert.deepEqual(port.read(),normalizeLibraryState(null));
  setAccountScope(10); assert.deepEqual(port.read(),state);
});

test('blocked or corrupted session storage leaves URL-driven filtering usable',()=>{
  const denied=createLibraryStateRepository({getItem(){throw new Error('blocked')},setItem(){throw new Error('blocked')}});
  assert.deepEqual(denied.read(),normalizeLibraryState(null));
  assert.doesNotThrow(()=>denied.write(normalizeLibraryState(null)));
  assert.deepEqual(createLibraryStateRepository({getItem:()=>'{bad',setItem(){}}).read(),normalizeLibraryState(null));
});

test('Ctrl/Command/middle/Shift clicks keep browser new-tab behavior',()=>{
  const plain={button:0,ctrlKey:false,metaKey:false,shiftKey:false,altKey:false,defaultPrevented:false};
  assert.equal(isPlainLinkClick(plain),true);
  for(const variant of [{ctrlKey:true},{metaKey:true},{shiftKey:true},{altKey:true},{button:1},{button:2},{defaultPrevented:true}])
    assert.equal(isPlainLinkClick({...plain,...variant}),false);
  assert.equal(routePath('practice',{composition:15,variant:'hard'}),'/practice/15/variants/hard');
});
