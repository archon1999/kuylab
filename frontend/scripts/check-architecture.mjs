import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import ts from 'typescript';

const extensionPattern = /\.(?:tsx?|jsx?|mjs|cjs)$/;
const browserNames = new Set([
  'window',
  'document',
  'navigator',
  'location',
  'history',
  'localStorage',
  'sessionStorage',
  'indexedDB',
  'performance',
  'requestAnimationFrame',
  'cancelAnimationFrame',
  'AudioContext',
  'webkitAudioContext',
]);
const networkNames = new Set(['fetch', 'XMLHttpRequest', 'WebSocket', 'EventSource']);
const platformPackages =
  /^(?:react(?:-dom)?(?:\/|$)|@mui\/|@emotion\/|@tanstack\/|axios(?:\/|$)|node:|https?(?:\/|$)|opensheetmusicdisplay(?:\/|$))/;
const transportPath = /(?:^|\/)(?:api|apiClient|http|storage|browser|midi|audio)(?:\.[^/]+)?$/i;
const slash = (value) => value.replaceAll('\\', '/');

function classification(filename, root) {
  const relative = slash(path.relative(root, filename));
  const parts = relative.split('/');
  if (parts[0] !== 'src') return { relative, area: 'outside' };
  if (parts[1] === 'main.tsx' || parts[1] === 'main.ts')
    return { relative, area: 'app', layer: 'entry' };
  if (parts[1] === 'app' || parts[1] === 'shared')
    return { relative, area: parts[1], layer: parts[2] };
  if (parts[1] === 'modules' && parts[2])
    return { relative, area: 'module', module: parts[2], layer: parts[3] || 'public' };
  return { relative, area: 'unlayered' };
}

function publicEntry(info, importer) {
  const relative = info.relative.split('/').slice(3).join('/');
  if (/^index\.(?:ts|tsx|js)$/.test(relative)) return true;
  if (/^(?:domain|application)\/index\.(?:ts|tsx|js)$/.test(relative)) return true;
  return (
    importer.area === 'app' &&
    (/^routes\.(?:ts|tsx|js)$/.test(relative) ||
      /^(?:pages|publicpages)\/[^/]+\.(?:ts|tsx|js)$/.test(relative) ||
      /^ui\/pages\/[^/]+\/index\.(?:ts|tsx|js)$/.test(relative))
  );
}

function literalValue(node) {
  if (!node) return undefined;
  if (ts.isStringLiteralLike(node)) return node.text;
  if (ts.isBinaryExpression(node) && node.operatorToken.kind === ts.SyntaxKind.PlusToken) {
    const left = literalValue(node.left),
      right = literalValue(node.right);
    return left === undefined || right === undefined ? undefined : left + right;
  }
  return undefined;
}

function referenceIdentifier(node) {
  const parent = node.parent;
  if (!parent) return false;
  if (ts.isPropertyAccessExpression(parent) && parent.name === node) return false;
  if (
    (ts.isPropertyDeclaration(parent) ||
      ts.isPropertySignature(parent) ||
      ts.isMethodDeclaration(parent) ||
      ts.isMethodSignature(parent) ||
      ts.isPropertyAssignment(parent)) &&
    parent.name === node
  )
    return false;
  if (
    (ts.isVariableDeclaration(parent) ||
      ts.isParameter(parent) ||
      ts.isFunctionDeclaration(parent) ||
      ts.isClassDeclaration(parent) ||
      ts.isInterfaceDeclaration(parent) ||
      ts.isTypeAliasDeclaration(parent)) &&
    parent.name === node
  )
    return false;
  return (
    !ts.isImportSpecifier(parent) &&
    !ts.isImportClause(parent) &&
    !ts.isNamespaceImport(parent) &&
    !ts.isExportSpecifier(parent)
  );
}

/** Analyze a real or in-memory source graph. `files` maps paths to source text. */
export function analyzeArchitecture(files, { root = process.cwd(), compilerOptions = {} } = {}) {
  root = path.resolve(root);
  const sources = new Map(
    Object.entries(files).map(([name, source]) => [path.resolve(root, name), source]),
  );
  const options = {
    target: ts.ScriptTarget.ES2022,
    module: ts.ModuleKind.ESNext,
    moduleResolution: ts.ModuleResolutionKind.Bundler,
    jsx: ts.JsxEmit.ReactJSX,
    allowJs: true,
    noEmit: true,
    baseUrl: root,
    paths: {
      '@app/*': ['src/app/*'],
      '@shared/*': ['src/shared/*'],
      '@modules/*': ['src/modules/*'],
    },
    ...compilerOptions,
  };
  const originalHost = ts.createCompilerHost(options);
  const host = {
    ...originalHost,
    directoryExists: (name) =>
      [...sources.keys()].some((filename) => filename.startsWith(path.resolve(name) + path.sep)) ||
      originalHost.directoryExists?.(name),
    realpath: (name) =>
      sources.has(path.resolve(name)) ? path.resolve(name) : originalHost.realpath?.(name) || name,
    fileExists: (name) => sources.has(path.resolve(name)) || originalHost.fileExists(name),
    readFile: (name) => sources.get(path.resolve(name)) ?? originalHost.readFile(name),
    getSourceFile: (name, languageVersion) =>
      sources.has(path.resolve(name))
        ? ts.createSourceFile(name, sources.get(path.resolve(name)), languageVersion, true)
        : originalHost.getSourceFile(name, languageVersion),
  };
  const program = ts.createProgram([...sources.keys()], options, host);
  const checker = program.getTypeChecker();
  const violations = [],
    edges = [];
  const add = (rule, info, node, source, detail) => {
    const location = source.getLineAndCharacterOfPosition(node.getStart(source));
    violations.push({
      rule,
      file: info.relative,
      line: location.line + 1,
      column: location.character + 1,
      message: detail,
    });
  };
  const resolvesInternally = (specifier) =>
    specifier.startsWith('.') ||
    Object.keys(options.paths || {}).some((alias) => specifier.startsWith(alias.replaceAll('*', '')));
  for (const filename of sources.keys()) {
    const source = program.getSourceFile(filename);
    const info = classification(filename, root);
    if (!source) continue;
    if (info.area === 'unlayered' && !filename.endsWith('.d.ts'))
      add(
        'unlayered-source',
        info,
        source,
        source,
        'Place production code under app, modules or shared.',
      );
    const domain = info.area === 'module' && info.layer === 'domain';
    const ui =
      info.area === 'module' && ['ui', 'presentation', 'pages', 'publicpages'].includes(info.layer);
    const application = info.area === 'module' && info.layer === 'application';
    const checkImport = (node, specifier, kind) => {
      if (specifier === undefined) {
        add(
          'dynamic-import-literal',
          info,
          node,
          source,
          'Use a literal dynamic import so its layer boundary can be verified.',
        );
        return;
      }
      const resolved = ts.resolveModuleName(specifier, filename, options, host).resolvedModule;
      const targetFilename = resolved?.resolvedFileName;
      const target = targetFilename && classification(targetFilename, root);
      edges.push({ from: info.relative, specifier, to: target?.relative || null, kind });
      if (
        !resolved &&
        resolvesInternally(specifier) &&
        !/\.(?:css|scss|svg|png|jpg|jpeg|woff2?|json)$/.test(specifier)
      )
        add(
          'unresolved-internal-import',
          info,
          node,
          source,
          `Cannot resolve internal import ${specifier}.`,
        );
      if (info.area === 'shared' && target && ['app', 'module'].includes(target.area))
        add(
          'shared-dependency',
          info,
          node,
          source,
          'Shared code cannot depend on app or feature modules.',
        );
      if (info.area === 'module' && target?.area === 'app')
        add(
          'module-app-dependency',
          info,
          node,
          source,
          'Feature modules cannot depend on app composition.',
        );
      if (
        target?.area === 'module' &&
        (info.area !== 'module' || info.module !== target.module) &&
        !publicEntry(target, info)
      )
        add(
          'module-public-entry',
          info,
          node,
          source,
          `Use a declared public entry of ${target.module}, not an internal file.`,
        );
      if (
        domain &&
        (platformPackages.test(specifier) ||
          (target?.area === 'module' &&
            ['application', 'data-access', 'ui', 'presentation', 'pages', 'publicpages'].includes(
              target.layer,
            )) ||
          (target?.area === 'shared' && target.layer === 'api') ||
          (target && transportPath.test(target.relative)) ||
          /\.(?:css|scss)$/.test(specifier))
      )
        add(
          'domain-platform-dependency',
          info,
          node,
          source,
          'Domain code must be independent of React, UI, transport and browser services.',
        );
      if (
        (ui || application) &&
        ((target?.area === 'module' && target.layer === 'data-access') ||
          (target &&
            /(?:^|\/)shared\/(?:api\/|lib\/(?:api|apiClient|http)(?:\.[^/]+)?$)/i.test(
              target.relative,
            )) ||
          /^(?:axios|https?)(?:\/|$)/.test(specifier))
      )
        add(
          'transport-layer-dependency',
          info,
          node,
          source,
          'UI/application use domain ports; transport adapters belong to data-access.',
        );
    };
    function visit(node) {
      if ((ts.isImportDeclaration(node) || ts.isExportDeclaration(node)) && node.moduleSpecifier)
        checkImport(
          node,
          literalValue(node.moduleSpecifier),
          ts.isImportDeclaration(node) ? 'import' : 'export',
        );
      if (ts.isImportEqualsDeclaration(node) && ts.isExternalModuleReference(node.moduleReference))
        checkImport(node, literalValue(node.moduleReference.expression), 'require');
      if (ts.isImportTypeNode(node) && ts.isLiteralTypeNode(node.argument))
        checkImport(node, literalValue(node.argument.literal), 'import-type');
      if (
        ts.isCallExpression(node) &&
        (node.expression.kind === ts.SyntaxKind.ImportKeyword ||
          (ts.isIdentifier(node.expression) && node.expression.text === 'require'))
      )
        checkImport(
          node,
          literalValue(node.arguments[0]),
          node.expression.kind === ts.SyntaxKind.ImportKeyword ? 'dynamic-import' : 'require',
        );
      if (ts.isIdentifier(node) && referenceIdentifier(node)) {
        const name = node.text;
        const symbol = checker.getSymbolAtLocation(node);
        const locallyDeclared = symbol?.declarations?.some((declaration) =>
          sources.has(path.resolve(declaration.getSourceFile().fileName)),
        );
        if (!locallyDeclared && domain && browserNames.has(name))
          add(
            'domain-browser-global',
            info,
            node,
            source,
            `Domain code cannot read browser global ${name}.`,
          );
        if (!locallyDeclared && networkNames.has(name) && (domain || ui || application))
          add('direct-network', info, node, source, `${name} belongs in a data-access adapter.`);
      }
      if (
        ts.isPropertyAccessExpression(node) &&
        ts.isIdentifier(node.expression) &&
        ['window', 'globalThis', 'self'].includes(node.expression.text)
      ) {
        if ((domain || ui || application) && networkNames.has(node.name.text))
          add(
            'direct-network',
            info,
            node,
            source,
            `${node.expression.text}.${node.name.text} belongs in data-access.`,
          );
        if (domain && browserNames.has(node.name.text))
          add(
            'domain-browser-global',
            info,
            node,
            source,
            `Domain code cannot read browser service ${node.name.text}.`,
          );
      }
      if (
        ts.isElementAccessExpression(node) &&
        ts.isIdentifier(node.expression) &&
        ['window', 'globalThis', 'self'].includes(node.expression.text)
      ) {
        const member = literalValue(node.argumentExpression);
        if ((domain || ui || application) && networkNames.has(member))
          add(
            'direct-network',
            info,
            node,
            source,
            `${node.expression.text}[${member}] belongs in data-access.`,
          );
        if (domain && browserNames.has(member))
          add(
            'domain-browser-global',
            info,
            node,
            source,
            `Domain code cannot read browser service ${member}.`,
          );
      }
      ts.forEachChild(node, visit);
    }
    visit(source);
  }
  const unique = [
    ...new Map(
      violations.map((item) => [`${item.rule}:${item.file}:${item.line}:${item.column}`, item]),
    ).values(),
  ];
  return { files: sources.size, edges, violations: unique };
}

export function checkProject(
  root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..'),
) {
  const files = {};
  function read(directory) {
    for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
      const filename = path.join(directory, entry.name);
      if (entry.isDirectory()) read(filename);
      else if (extensionPattern.test(entry.name) && !/\.(?:test|spec)\.[^.]+$/.test(entry.name))
        files[filename] = fs.readFileSync(filename, 'utf8');
    }
  }
  read(path.join(root, 'src'));
  const configPath = ts.findConfigFile(root, ts.sys.fileExists, 'tsconfig.json');
  const config = configPath ? ts.readConfigFile(configPath, ts.sys.readFile) : { config: {} };
  if (config.error)
    throw new Error(ts.flattenDiagnosticMessageText(config.error.messageText, '\n'));
  const parsed = ts.parseJsonConfigFileContent(config.config, ts.sys, root);
  return analyzeArchitecture(files, { root, compilerOptions: parsed.options });
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const result = checkProject(process.argv[2] ? path.resolve(process.argv[2]) : undefined);
  for (const item of result.violations)
    process.stderr.write(
      `${item.file}:${item.line}:${item.column} [${item.rule}] ${item.message}\n`,
    );
  process.stdout.write(
    `Architecture: ${result.files} source files, ${result.edges.length} import edges, ${result.violations.length} violations.\n`,
  );
  process.exitCode = result.violations.length ? 1 : 0;
}
