import assert from 'node:assert/strict';
import test from 'node:test';
import { parseRoute, routePath } from '../src/shared/routing/paths.ts';
import { accountStorage, setAccountScope, scopedKey } from '../src/shared/lib/accountScope.ts';
test('route identity round trips through clean shareable URLs', () => {
  for(const [page,values] of [['dashboard',{}],['detail',{composition:8}],['practice',{composition:8}],['study',{item:'lesson:still:opening-listen',stage:'lesson:still:opening-listen:1'}],['study',{item:'theory:legato',example:'theory:legato:connected'}],['exercises',{}],['statistics',{}]]) {
    const url = routePath(page,values), route = parseRoute(url);
    assert.equal(route.page,page); assert.equal(url.includes('?'),false);
    for(const [key,value] of Object.entries(values)) assert.equal(route.params.get(key),String(value));
  }
});
test('unknown and malformed paths show 404 instead of silently opening dashboard', () => {
  for(const url of ['/missing','/study','/practice/8/extra','/study/%E0%A4%A']) assert.equal(parseRoute(url).page,'notFound');
});
test('old composition and stage links keep their identity', () => {
  const route = parseRoute('/','?page=study&item=lesson%3Astill%3Aopening-listen&stage=easy');
  assert.equal(routePath(route.page,route.params),'/study/lesson%3Astill%3Aopening-listen/stages/easy');
  const redirected = parseRoute('/studio','?page=practice&composition=8');
  assert.equal(routePath(redirected.page,redirected.params),'/practice/8');
  assert.equal(routePath('dashboard'), '/studio');
});
test('browser persistence isolates accounts and never reads legacy unscoped values', () => {
  const map = new Map([['kuylab-profile','private legacy']]);
  globalThis.localStorage = {getItem:key => map.get(key)||null,setItem:(key,value)=>map.set(key,value)};
  setAccountScope(1); assert.equal(accountStorage.getItem('kuylab-profile'),null);
  accountStorage.setItem('kuylab-profile','owner-one');
  setAccountScope(2); assert.equal(accountStorage.getItem('kuylab-profile'),null);
  accountStorage.setItem('kuylab-profile','owner-two');
  setAccountScope(1); assert.equal(accountStorage.getItem('kuylab-profile'),'owner-one');
  assert.equal(scopedKey('x'),'user:1:x'); setAccountScope(null);
});
