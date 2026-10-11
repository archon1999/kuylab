import assert from 'node:assert/strict';
import test from 'node:test';
import { analyzeArchitecture } from '../scripts/check-architecture.mjs';

const root = '/architecture-fixture';
const inspect = (files) => analyzeArchitecture(files, { root });
const rules = (result) => new Set(result.violations.map((item) => item.rule));

test('valid UI -> application -> domain ports with injected adapters and lazy public pages', () => {
  const result = inspect({
    'src/main.tsx': "import './app/router';",
    'src/app/router.ts':
      "import { createRepository } from '@modules/learning'; export const page = () => import('@modules/learning/pages/Lesson'); createRepository();",
    'src/modules/learning/index.ts': "export { createRepository } from './data-access/repository';",
    'src/modules/learning/data-access/repository.ts':
      "import type { Port } from '../domain'; export const createRepository = (): Port => ({ load: async () => fetch('/api').then(r => r.json()) });",
    'src/modules/learning/domain/index.ts': 'export interface Port { load(): Promise<unknown> }',
    'src/modules/learning/application/useLesson.ts':
      "import type { Port } from '../domain'; export const run = (port: Port) => port.load();",
    'src/modules/learning/pages/Lesson.ts': "export { Lesson } from '../ui/Lesson';",
    'src/modules/learning/ui/Lesson.ts':
      "import { run } from '../application/useLesson'; export const Lesson = run;",
  });
  assert.deepEqual(result.violations, []);
});

test('relative, aliased, re-export and dynamic deep cross-module imports are all checked', () => {
  const result = inspect({
    'src/modules/a/ui/Panel.ts':
      "import { x } from '../../b/domain/internal'; export { x as other } from '@modules/b/domain/internal'; const load=()=>import('@modules/b/ui/Private');",
    'src/modules/b/domain/internal.ts': 'export const x = 1;',
    'src/modules/b/ui/Private.ts': 'export default 1;',
  });
  assert.equal(result.violations.filter((item) => item.rule === 'module-public-entry').length, 3);
  assert.ok(result.edges.some((edge) => edge.kind === 'dynamic-import'));
});

test('shared and feature modules cannot reach app composition', () => {
  const result = inspect({
    'src/shared/ui/Button.ts': "import '@modules/a'; import '@app/router';",
    'src/modules/a/index.ts': 'export const value = 1;',
    'src/modules/a/application/run.ts': "import '@app/router';",
    'src/app/router.ts': 'export const route = 1;',
  });
  assert.equal(result.violations.filter((item) => item.rule === 'shared-dependency').length, 2);
  assert.ok(rules(result).has('module-app-dependency'));
});

test('domain remains free of frameworks, transport adapters and browser globals', () => {
  const result = inspect({
    'src/modules/a/domain/model.ts':
      "import type { ReactNode } from 'react'; import '@shared/lib/api'; import '../application/run'; export const result = navigator.userAgent; const transport = globalThis.fetch;",
    'src/shared/lib/api.ts': 'export const api = fetch;',
    'src/modules/a/application/run.ts': 'export const run = 1;',
  });
  assert.ok(rules(result).has('domain-platform-dependency'));
  assert.ok(rules(result).has('domain-browser-global'));
  assert.ok(rules(result).has('direct-network'));
});

test('UI/application cannot bypass domain ports with fetch or data-access imports', () => {
  const result = inspect({
    'src/modules/a/ui/Page.ts':
      "import { load } from '../data-access/repository'; export const open=()=>window.fetch('/api');",
    'src/modules/a/application/run.ts':
      "import { load } from '../data-access/repository'; export const run=()=>fetch('/api');",
    'src/modules/a/data-access/repository.ts': "export const load=()=>fetch('/api');",
  });
  assert.equal(
    result.violations.filter((item) => item.rule === 'transport-layer-dependency').length,
    2,
  );
  assert.equal(result.violations.filter((item) => item.rule === 'direct-network').length, 2);
});

test('domain properties and locally named functions do not become fake browser calls', () => {
  const result = inspect({
    'src/modules/a/domain/model.ts':
      'interface Model { fetch: number; window: string } function fetch(value: number) { return value; } export const result=fetch(1);',
  });
  assert.deepEqual(result.violations, []);
});

test('public domain entries are allowed but UI entries are only app route boundaries', () => {
  const result = inspect({
    'src/modules/a/domain/model.ts':
      "import type { Value } from '@modules/b/domain'; export type Copy=Value;",
    'src/modules/a/ui/Panel.ts': "import '@modules/b/publicpages/Page';",
    'src/modules/b/domain/index.ts': 'export interface Value { id:number }',
    'src/modules/b/publicpages/Page.ts': 'export default 1;',
  });
  assert.equal(result.violations.filter((item) => item.rule === 'module-public-entry').length, 1);
});

test('unresolved internal paths and computed lazy routes cannot silently evade boundaries', () => {
  const result = inspect({
    'src/app/router.ts':
      "import '@modules/missing/domain'; const target='./unknown'; export const page=()=>import(target);",
  });
  assert.ok(rules(result).has('unresolved-internal-import'));
  assert.ok(rules(result).has('dynamic-import-literal'));
});

test('flat production source is reported instead of passing an unmigrated graph', () => {
  const result = inspect({ 'src/App.tsx': 'export default function App(){ return null; }' });
  assert.ok(rules(result).has('unlayered-source'));
});

test('type imports, require and computed global network access cannot bypass the same boundaries', () => {
  const result = inspect({
    'src/modules/a/application/run.ts':
      "type Hidden=import('@modules/b/domain/private').Value; const hidden=require('@modules/b/domain/private'); const download=globalThis['fetch'];",
    'src/modules/b/domain/private.ts': 'export interface Value { id:number }',
  });
  assert.equal(result.violations.filter((item) => item.rule === 'module-public-entry').length, 2);
  assert.ok(rules(result).has('direct-network'));
});

test('Deenly-style page barrels are app route boundaries, not cross-feature internals', () => {
  const result = inspect({
    'src/app/routes/index.ts':
      "export const page=()=>import('@modules/studio/ui/pages/StudyPage');",
    'src/modules/studio/ui/pages/StudyPage/index.ts': "export { default } from './StudyPage';",
    'src/modules/studio/ui/pages/StudyPage/StudyPage.ts': 'export default 1;',
    'src/modules/other/ui/Panel.ts': "import '@modules/studio/ui/pages/StudyPage';",
  });
  assert.equal(result.violations.filter((item) => item.rule === 'module-public-entry').length, 1);
  assert.equal(result.violations[0].file, 'src/modules/other/ui/Panel.ts');
});

test('shared API directory remains transport-only after the architecture move', () => {
  const result = inspect({
    'src/shared/api/transport.ts': 'export const request = 1;',
    'src/modules/a/domain/entities/model.ts': "import '@shared/api/transport';",
    'src/modules/a/application/queries.ts': "import '@shared/api/transport';",
    'src/modules/a/ui/pages/Page/Page.ts': "import '@shared/api/transport';",
    'src/modules/a/data-access/repository/a.repository.impl.ts': "import '@shared/api/transport';",
  });
  assert.equal(
    result.violations.filter((item) => item.rule === 'transport-layer-dependency').length,
    2,
  );
  assert.equal(
    result.violations.filter((item) => item.rule === 'domain-platform-dependency').length,
    1,
  );
});
