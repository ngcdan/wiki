---
title: "BF1 AI — WebUI Boilerplate"
tags: [bf1, ai, frontend, boilerplate]
---

# WebUI Plugin Boilerplate — OF1 Platform

Tài liệu này cung cấp template đầy đủ để tạo một WebUI plugin mới theo chuẩn của OF1 Platform, dựa trên phân tích `webui/crm`.

## Kiến trúc tổng quan

- **Build tool**: Webpack 5 + Module Federation Plugin
- **Framework**: React 18 (Class Components là chủ đạo, KHÔNG dùng Hooks)
- **Language**: TypeScript 5.1 (ES2022)
- **Styling**: Bootstrap utility classes + SCSS (không dùng CSS-in-JS)
- **State**: React class state + AppContext (không dùng Redux/Pinia)
- **Navigation**: SpacePlugin system (không dùng React Router truyền thống)
- **API**: `appContext.createHttpBackendCall()` hoặc `appContext.createHttpRemoteBackendCall()`
- **Package manager**: `pnpm` (KHÔNG dùng npm/yarn)

---

## 1. Cấu trúc thư mục

```
webui/<plugin-name>/
├── src/
│   ├── app/
│   │   └── <plugin>/
│   │       ├── <module-a>/
│   │       │   ├── UIXxxList.tsx         # Màn hình danh sách
│   │       │   ├── UIXxxEditor.tsx       # Màn hình thêm/sửa
│   │       │   └── index.tsx             # Re-export
│   │       ├── common/
│   │       │   └── widgets/              # Widget dùng chung
│   │       ├── init.tsx                  # SpacePlugin + màn hình
│   │       └── index.tsx
│   ├── Init.tsx                          # Module Federation entry
│   └── index.tsx                         # UMD entry
├── package.json
├── tsconfig.json
├── webpack.config.ts
└── README.md
```

---

## 2. `package.json`

```json
{
  "name": "@of1-webui/<plugin-name>",
  "version": "1.0.0",
  "description": "OF1 <Plugin Name> WebUI",
  "author": "tuan08",
  "main": "dist/main.js",
  "module": "dist/main.js",
  "jsnext:main": "dist/main.js",
  "types": "dist/@types/index.d.ts",
  "scripts": {
    "build":       "cross-env NODE_OPTIONS='--import=tsx' webpack --mode production",
    "dev-build":   "cross-env NODE_OPTIONS='--import=tsx' webpack --mode development",
    "dev-watch":   "cross-env NODE_OPTIONS='--import=tsx' webpack --mode development --watch",
    "dev-server":  "cross-env NODE_OPTIONS='--import=tsx' webpack serve --mode development --open"
  },
  "dependencies": {
    "@of1-webui/lib":      "file:../../../of1-core/webui/lib",
    "@of1-webui/platform": "file:../../../of1-platform/webui/platform"
  },
  "peerDependencies": {
    "react":            "^18.3.1",
    "react-dom":        "^18.3.1",
    "react-router-dom": "6.29.0",
    "react-feather":    "^2.0.10",
    "recharts":         "^2.15.1"
  },
  "devDependencies": {
    "@types/node":             "^20.14.2",
    "@types/react":            "18.2.12",
    "@types/react-dom":        "18.2.5",
    "@types/react-router-dom": "^5.3.3",
    "@types/webpack":          "^5.28.5",
    "cross-env":               "^7.0.3",
    "css-loader":              "^6.11.0",
    "fork-ts-checker-webpack-plugin": "^8.0.0",
    "html-webpack-plugin":     "^5.6.0",
    "mini-css-extract-plugin": "^2.9.0",
    "sass":                    "1.71.1",
    "sass-loader":             "^16.0.4",
    "style-loader":            "^3.3.4",
    "ts-loader":               "^9.5.1",
    "tsx":                     "4.19.2",
    "typescript":              "5.1.3",
    "webpack":                 "5.87.0",
    "webpack-cli":             "5.1.4",
    "webpack-dev-server":      "5.2.0"
  },
  "files": ["dist"]
}
```

---

## 3. `webpack.config.ts`

Thay `<plugin-name>`, `<PLUGIN_NAME>`, `<PORT>` theo plugin mới.

```typescript
import webpack from "webpack";
import path from "path";

const isDevelopment = process.argv[process.argv.indexOf('--mode') + 1] === 'development';
const watchOpt = process.argv[process.argv.indexOf('--watch')];

let devtool: boolean | 'source-map' = false;
if (isDevelopment) devtool = 'source-map';

// Module Federation — expose ./init để host app load động
const federationConfig = new webpack.container.ModuleFederationPlugin({
  name: 'ModuleFederationPlugin',
  library: { type: 'var', name: '<PLUGIN_NAME>FederationPlugin' },  // e.g. CRMFederationPlugin
  filename: 'webui/init.js',
  exposes: {
    './init': './src/Init.tsx'
  },
  shared: {
    'react':               { import: false },
    'react-dom':           { import: false },
    'react-router-dom':    { import: false },
    'bootstrap':           { import: false },
    'react-feather':       { import: false },
    'recharts':            { import: false },
    'keycloak-js':         { import: false },
    '@of1-webui/lib':      { import: false },
    '@of1-webui/platform': { import: false }
  }
});

const config: webpack.Configuration = {
  entry: ["./src/index.tsx"],

  output: {
    publicPath: `/platform/plugin/<plugin-name>/`,     // e.g. /platform/plugin/crm/
    filename: "webui/<plugin-name>-[name].js",
    chunkFilename: 'webui/<plugin-name>-chunk-[name].js',
    library: {
      name: 'of1_webui_<plugin_name>',                 // e.g. of1_webui_crm
      type: 'umd2',
      umdNamedDefine: true
    },
    clean: !isDevelopment
  },

  optimization: {
    minimize: !isDevelopment,
    runtimeChunk: false,
    concatenateModules: false,
    emitOnErrors: false
  },

  resolve: {
    extensions: ['.ts', '.tsx', '.js'],
    modules: [path.resolve(__dirname, 'src'), 'node_modules']
  },

  watchOptions: {
    aggregateTimeout: 200,
    ignored: /node_modules/,
  },

  devtool,

  module: {
    rules: [
      {
        test: /\.tsx?$/,
        loader: 'ts-loader',
        exclude: /node_modules/,
        options: { transpileOnly: watchOpt ? true : false }
      },
      {
        test: /\.css$/i,
        use: ["style-loader", "css-loader"],
      },
      {
        test: /\.s(a|c)ss$/,
        exclude: /\.module.(s(a|c)ss)$/,
        use: [
          { loader: 'style-loader' },
          { loader: 'css-loader' },
          { loader: 'sass-loader', options: { sourceMap: isDevelopment } }
        ]
      }
    ],
  },

  //@ts-ignore
  plugins: [federationConfig],

  //@ts-ignore
  devServer: {
    hot: true,
    port: <PORT>,                                      // e.g. 3003 cho CRM, chọn port khác
    historyApiFallback: true,
    allowedHosts: 'all',
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Credentials': 'true',
      'Access-Control-Allow-Headers': '*',
      'Access-Control-Allow-Methods': '*'
    },
    static: {
      directory: path.join(__dirname, "public"),
    }
  }
};

export default config;
```

---

## 4. `tsconfig.json`

```json
{
  "compilerOptions": {
    "baseUrl": "./src",
    "outDir": "dist",
    "target": "es2022",
    "module": "ES2022",
    "moduleResolution": "Bundler",
    "lib": ["dom", "es2020", "es2022", "esnext"],
    "esModuleInterop": true,
    "sourceMap": true,
    "allowJs": false,
    "jsx": "react",
    "declaration": true,
    "declarationDir": "dist/@types",
    "declarationMap": true,
    "forceConsistentCasingInFileNames": true,
    "allowSyntheticDefaultImports": true,
    "noImplicitReturns": false,
    "noImplicitThis": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "noUnusedLocals": false,
    "noUnusedParameters": false,
    "experimentalDecorators": true,
    "emitDecoratorMetadata": true
  },
  "include": ["./src"],
  "exclude": ["node_modules", "build", "dist", "example"]
}
```

---

## 5. `src/index.tsx` — UMD Entry Point

```tsx
import React from 'react';

export * as app from './app'

let react = React as any;
if (!react['id']) {
  react['id'] = '@of1-webui/<plugin-name>'
  console.log('React is not loaded. Expect React is already loaded in module @of1-webui/<plugin-name>');
}
```

---

## 6. `src/Init.tsx` — Module Federation Entry

```tsx
import { app } from '@of1-webui/lib';
import { init as pluginInit } from './app/<plugin>/init';

export function init() {
  console.log("<PluginName>Module: init()")

  const baseUrl = '/platform/plugin/<plugin-name>'
  const backend = new app.host.BackendConfig(
    `${baseUrl}`,
    `${baseUrl}/rest/v1.0.0`,
    `${baseUrl}/api`
  );
  app.host.BACKEND_CONFIGS.add("<plugin-name>", backend)

  pluginInit();
}
```

---

## 7. `src/app/<plugin>/init.tsx` — SpacePlugin & Screen Registration

```tsx
import React from "react";
import * as icon from 'react-feather';
import { app, bs } from '@of1-webui/lib';

// Import các UI component chính
import { UIXxxList } from "./module-a";
import { UIXxxEditor } from "./module-b";

import space = app.space;

const MODULE_NAME = '<plugin-name>';          // e.g. 'crm'
const FEATURE_BASIC = '<plugin>-basic';       // e.g. 'crm-basic'

class PluginSpacePlugin extends space.SpacePlugin {
  constructor() {
    super('<domain>/<plugin>', '<Plugin> Navigation');
    // e.g. super('forwarder/sales', 'Sale Navigation')
  }

  override createUserScreens(): space.ScreenConfig[] {
    if (bs.ScreenUtil.isMobileScreen()) return this.createMobileScreens();
    return this.createDesktopScreens();
  }

  private createDesktopScreens(): space.ScreenConfig[] {
    return [
      {
        id: '<plugin>-main',
        label: '<Plugin> Main',
        backend: MODULE_NAME,
        icon: icon.Globe,
        checkPermission: {
          feature: { module: MODULE_NAME, name: FEATURE_BASIC },
          requiredCapability: app.READ,
        },
        renderUI: (appCtx: app.AppContext, pageCtx: app.PageContext) => {
          return <UIXxxList appContext={appCtx} pageContext={pageCtx} />;
        },
        screens: [
          {
            id: '<plugin>-sub-screen',
            label: 'Sub Screen',
            backend: MODULE_NAME,
            icon: icon.List,
            checkPermission: {
              feature: { module: MODULE_NAME, name: FEATURE_BASIC },
              requiredCapability: app.WRITE,
            },
            renderUI: (appCtx: app.AppContext, pageCtx: app.PageContext) => {
              return <UIXxxEditor appContext={appCtx} pageContext={pageCtx} />;
            },
          },
        ]
      },
    ];
  }

  private createMobileScreens(): space.ScreenConfig[] {
    // Mobile thường đơn giản hơn — chỉ giữ lại màn hình chính
    return this.createDesktopScreens().map(s => ({ ...s, screens: [] }));
  }

  override createSystemScreens(): space.ScreenConfig[] {
    return [
      {
        id: '<plugin>-admin',
        label: '<Plugin> Admin',
        backend: MODULE_NAME,
        icon: icon.Settings,
        checkPermission: {
          feature: { module: MODULE_NAME, name: FEATURE_BASIC },
          requiredCapability: app.MODERATOR,
        },
        renderUI: (appCtx: app.AppContext, pageCtx: app.PageContext) => {
          return <UIXxxList appContext={appCtx} pageContext={pageCtx} isAdmin />;
        },
      }
    ];
  }
}

export function init() {
  app.space.SPACE_PLUGIN_MANAGER.register(new PluginSpacePlugin());
}
```

---

## 8. List Component — `UIXxxList.tsx`

Pattern chuẩn cho màn hình danh sách dạng grid.

```tsx
import React from 'react';
import * as FeatherIcon from 'react-feather';
import { app, bs, entity, input, util } from '@of1-webui/lib';

const T = (str: string) => str;

// ---- Plugin (search/filter state) ----

class UIXxxListPlugin extends entity.DbQueryPlugin {
  searchText: string = '';
  status: string = '';

  override createSearchParams() {
    return {
      searchText: this.searchText,
      status: this.status,
    };
  }
}

// ---- Props ----

interface UIXxxListProps extends entity.DbEntityListProps {
  isAdmin?: boolean;
}

// ---- Component ----

export class UIXxxList extends entity.DbEntityList<UIXxxListPlugin, UIXxxListProps> {

  constructor(props: UIXxxListProps) {
    super(props);
    this.plugin = new UIXxxListPlugin(
      props.appContext,
      '<plugin-name>',          // backend name
      'XxxService',              // service class name
      'search'                   // method name
    );
  }

  createColumns(): entity.ColumnConfig[] {
    return [
      {
        field: 'code', label: T('Code'), width: 120,
        renderCell: (record: any) => <b>{record.code}</b>
      },
      {
        field: 'name', label: T('Name'), width: 200,
      },
      {
        field: 'status', label: T('Status'), width: 130,
        renderCell: (record: any) => renderStatusBadge(record.status)
      },
      {
        field: 'createdTime', label: T('Created'), width: 150,
        renderCell: (record: any) => util.DateTimeUtil.formatDisplay(record.createdTime)
      },
    ];
  }

  createActions(): entity.ActionConfig[] {
    let { appContext, pageContext } = this.props;
    let writeCap = pageContext.hasUserWriteCapability();
    return [
      {
        label: T('New'), icon: FeatherIcon.Plus, hide: !writeCap,
        onClick: () => {
          bs.dialogShow(T('New Item'), (
            <UIXxxEditor
              appContext={appContext} pageContext={pageContext}
              observer={entity.createNewBeanObserver({ status: 'NEW' })}
              onPostCommit={() => this.plugin.reload()}
            />
          ), { size: 'lg' });
        }
      },
      {
        label: T('Edit'), icon: FeatherIcon.Edit, hide: !writeCap,
        onClick: (record: any) => {
          bs.dialogShow(T('Edit Item'), (
            <UIXxxEditor
              appContext={appContext} pageContext={pageContext}
              observer={entity.createBeanObserver(record)}
              onPostCommit={() => this.plugin.reload()}
            />
          ), { size: 'lg' });
        }
      },
      {
        label: T('Delete'), icon: FeatherIcon.Trash2, hide: !writeCap,
        onClick: (record: any) => {
          bs.dialogConfirm(T('Confirm Delete'), T('Are you sure?'), () => {
            appContext.createHttpBackendCall('XxxService', 'deleteById', { id: record.id })
              .withSuccessData(() => this.plugin.reload())
              .call();
          });
        }
      }
    ];
  }

  renderSearchBar() {
    return (
      <div className="flex-hbox p-1 gap-2">
        <input.WStringInput
          placeholder={T('Search...')}
          onChange={(val: string) => {
            this.plugin.searchText = val;
            this.plugin.reload();
          }}
        />
        <input.WSelectInput
          options={['', 'NEW', 'ACTIVE', 'CLOSED']}
          placeholder={T('All Status')}
          onChange={(val: string) => {
            this.plugin.status = val;
            this.plugin.reload();
          }}
        />
      </div>
    );
  }

  render() {
    return (
      <div className="flex-vbox h-100">
        {this.renderSearchBar()}
        {super.render()}
      </div>
    );
  }
}
```

---

## 9. Editor/Form Component — `UIXxxEditor.tsx`

Pattern chuẩn cho form thêm/sửa entity.

```tsx
import React from 'react';
import * as FeatherIcon from 'react-feather';
import { bs, input, entity, app, util } from '@of1-webui/lib';
import { module } from '@of1-webui/platform';

const T = (str: string) => str;

export interface UIXxxEditorProps extends entity.AppComplexEntityEditorProps {
  isNew?: boolean;
}

export class UIXxxEditor extends entity.AppDbComplexEntityEditor<UIXxxEditorProps> {

  state = { isSending: false };

  // Validate trước khi commit
  onPreCommit = (observer: entity.ComplexBeanObserver) => {
    let bean = observer.getMutableBean();
    if (!bean.code?.trim()) {
      bs.dialogShow(T('Validation Error'), T('Code is required!'), { size: 'sm', backdrop: 'static' });
      throw new Error("Validation Failed");
    }
    this.setState({ isSending: true });
  }

  // Xử lý sau khi commit thành công
  onPostCommit = (savedEntity: any) => {
    let { onPostCommit, appContext } = this.props;
    this.setState({ isSending: false });
    appContext.addOSNotification('success', T('Saved successfully!'));
    if (onPostCommit) onPostCommit(savedEntity, this);
    else this.forceUpdate();
  }

  // Kiểm tra trùng code (async call khi blur)
  onCheckCodeExists = (_wInput: input.WInput, _bean: any, _field: string, _oldVal: any, newVal: any) => {
    if (!newVal?.trim()) return;
    this.props.appContext
      .createHttpBackendCall('XxxService', 'findByCode', { code: newVal })
      .withSuccessData((list: any[]) => {
        if (list?.length > 0) {
          bs.dialogShow(T('Warning'), (
            <div className="text-warning py-2">
              {T(`Code "${newVal}" already exists!`)}
            </div>
          ), { size: 'sm', backdrop: 'static' });
        }
      })
      .call();
  }

  // Sync các field liên quan
  onNameChange = (bean: any, field: string, _oldVal: any, newVal: any) => {
    bean[field] = newVal;
    if (field === 'name') {
      if (!bean.label) bean.label = newVal;
    }
    this.forceUpdate();
  }

  render() {
    let { appContext, pageContext, observer, readOnly } = this.props;
    let bean = observer.getMutableBean();
    let writeCap = pageContext.hasUserWriteCapability() && !readOnly;

    return (
      <div className="flex-vbox">
        <bs.Scrollable style={{ height: 500 }}>
          <div className="flex-vbox shadow-sm rounded bg-white p-2">

            {/* Row 1: Code + Name */}
            <bs.Row>
              <bs.Col span={4}>
                <input.BBStringField
                  bean={bean} field="code" label={T("Code")}
                  disable={!writeCap || !observer.isNewBean()}
                  required
                  onBgInputChange={this.onCheckCodeExists}
                />
              </bs.Col>
              <bs.Col span={8}>
                <input.BBStringField
                  bean={bean} field="name" label={T("Name")}
                  disable={!writeCap}
                  required
                  onInputChange={this.onNameChange}
                />
              </bs.Col>
            </bs.Row>

            {/* Row 2: Status + Category */}
            <bs.Row>
              <bs.Col span={4}>
                <input.BBSelectField
                  bean={bean} field="status" label={T("Status")}
                  disable={!writeCap}
                  options={['NEW', 'ACTIVE', 'CLOSED']}
                />
              </bs.Col>
              <bs.Col span={4}>
                <input.BBSelectField
                  bean={bean} field="category" label={T("Category")}
                  disable={!writeCap}
                  options={['TYPE_A', 'TYPE_B']}
                />
              </bs.Col>
              <bs.Col span={4}>
                <input.BBDateField
                  bean={bean} field="startDate" label={T("Start Date")}
                  disable={!writeCap}
                />
              </bs.Col>
            </bs.Row>

            {/* Row 3: Country lookup (dùng platform ref) */}
            <bs.Row>
              <bs.Col span={6}>
                <module.settings.BBRefCountry
                  key={util.IDTracker.next()}
                  appContext={appContext} pageContext={pageContext}
                  placement="bottom-start" offset={[0, 5]} minWidth={350}
                  disable={!writeCap}
                  label={T('Country')} placeholder="Enter Country"
                  bean={bean} beanIdField="countryId" beanLabelField="countryLabel" refCountryBy="id"
                  hideMoreInfo
                  onPostUpdate={(_inputUI, bean, selectOpt) => {
                    bean.countryId = selectOpt.id;
                    bean.countryLabel = selectOpt.label;
                    this.forceUpdate();
                  }}
                />
              </bs.Col>
            </bs.Row>

            {/* Row 4: Note */}
            <bs.Row>
              <bs.Col span={12}>
                <input.BBTextField
                  bean={bean} field="note" label={T("Note")}
                  disable={!writeCap}
                  style={{ height: '5em', fontSize: '1rem' }}
                />
              </bs.Col>
            </bs.Row>

          </div>
        </bs.Scrollable>

        {/* Toolbar commit */}
        <bs.Toolbar className="border">
          <entity.ButtonEntityCommit
            btnLabel={this.state.isSending ? T('Saving...') : T('Save')}
            appContext={appContext} pageContext={pageContext} observer={observer}
            hide={!writeCap}
            disable={this.state.isSending}
            commit={{
              entityLabel: T('Xxx'),
              context: '<plugin-name>',         // e.g. 'crm'
              service: 'XxxService',
              commitMethod: 'saveEntity'
            }}
            onPreCommit={this.onPreCommit}
            onPostCommit={this.onPostCommit}
          />
        </bs.Toolbar>
      </div>
    );
  }
}
```

---

## 10. Status Configuration — Pattern chuẩn

```tsx
import * as FeatherIcon from 'react-feather';

// Định nghĩa status map
export const XxxStatus = {
  NEW: {
    label: 'New',        value: 'NEW',        color: 'info',      icon: FeatherIcon.Star
  },
  PROCESSING: {
    label: 'Processing', value: 'PROCESSING', color: 'primary',   icon: FeatherIcon.RefreshCw
  },
  APPROVED: {
    label: 'Approved',   value: 'APPROVED',   color: 'success',   icon: FeatherIcon.CheckCircle
  },
  REJECTED: {
    label: 'Rejected',   value: 'REJECTED',   color: 'danger',    icon: FeatherIcon.XCircle
  },
  ON_HOLD: {
    label: 'On Hold',    value: 'ON_HOLD',    color: 'warning',   icon: FeatherIcon.PauseCircle
  },
  CLOSED: {
    label: 'Closed',     value: 'CLOSED',     color: 'secondary', icon: FeatherIcon.Lock
  },
} as const;

// Render badge (dùng trong grid column hoặc card)
export const renderStatusBadge = (statusValue: string) => {
  let s = XxxStatus[statusValue as keyof typeof XxxStatus] ?? XxxStatus.NEW;
  let StatusIcon = s.icon;
  return (
    <div className={`flex-hbox flex-center px-2 py-1 rounded-2 bg-${s.color}-subtle text-${s.color} w-100`}>
      <StatusIcon size={14} className="me-1" />
      <span className="fw-bold" style={{ fontSize: '0.85rem' }}>{s.label}</span>
    </div>
  );
};
```

---

## 11. Utility / Tool Pattern

```tsx
// Không extend class, không dùng hooks — chỉ là object/functions thuần
export const XxxTool = {
  isTypeA: (record: any): boolean => record?.type === 'TYPE_A',
  isTypeB: (record: any): boolean => record?.type === 'TYPE_B',

  getDisplayLabel: (record: any): string => {
    if (!record) return '';
    return `${record.code} — ${record.name}`;
  },

  mapToCategory: (type: string, subtype: string): string => {
    if (type === 'A' && subtype === 'X') return 'AX';
    return 'OTHER';
  }
};
```

---

## 12. API Call Patterns

### Pattern 1: Simple call qua `createHttpBackendCall`

```tsx
// Đơn giản hơn — dùng khi backend chỉ có 1 backend config
appContext.createHttpBackendCall('XxxService', 'findAll', {})
  .withSuccessData((list: any[]) => {
    this.setState({ items: list });
  })
  .call();
```

### Pattern 2: Call qua `createHttpRemoteBackendCall` (chỉ định backend)

```tsx
// Dùng khi cần chỉ định backend cụ thể (multi-backend)
appContext.createHttpRemoteBackendCall('<plugin-name>', 'XxxService', 'findByCode', { code: val })
  .withSuccessData((list: any[]) => {
    // handle
  })
  .withErrorData((err: any) => {
    console.error('Error:', err);
  })
  .call();
```

---

## 13. Chú ý quan trọng

| Vấn đề | Giải pháp |
|--------|-----------|
| Component không re-render sau khi mutate bean | Gọi `this.forceUpdate()` |
| Bean field binding | Dùng `bean={bean} field='fieldName'` (không setState) |
| Dialog/Modal | Dùng `bs.dialogShow(title, jsx, options)` thay vì tự tạo modal |
| Responsive | Dùng `bs.ScreenUtil.isMobileScreen()` để phân nhánh |
| Layout Grid | `bs.Row` + `bs.Col span={n}` (n là bội số của 12) |
| Icons | `<FeatherIcon.IconName size={14} className="me-1" />` |
| Date format | `util.DateTimeUtil.formatDisplay(timestamp)` |
| Unique key | `util.IDTracker.next()` cho các component ref/lookup |
| Permissions | `pageContext.hasUserWriteCapability()` — WRITE; `app.READ`, `app.WRITE`, `app.MODERATOR`, `app.ADMIN` |
| Hooks (React) | **KHÔNG DÙNG** — project dùng class component toàn bộ |

## Liên quan

- [[bf1-ai-index|BF1 AI — Index]]
