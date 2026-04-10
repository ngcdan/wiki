---
title: "BF1 AI — UI List Guide"
tags: [bf1, ai, ui, guide]
---

# UI List Pattern Guide — @of1-webui/lib

Reference guide for building List screens using `@of1-webui/lib`. Two patterns cover the majority of use cases.

---

## Pattern A: DbEntityList

**When to use:** Data loaded from server with independent search, filter, or pagination. Pattern A handles the full range of interactions — read-only display, popup editors, status changes, and bulk operations. This is the default pattern for most list screens.

**When NOT to use:** The list is a sub-component inside a parent form and does not load data independently → use Pattern B.

---

### A1. Class Structure

```tsx
// Plugin and List are always in the same file.
export class UISomethingPlugin extends entity.DbEntityListPlugin { ... }

interface UISomethingListProps extends entity.DbEntityListProps {
  space: 'User' | 'Company' | 'System'; // add domain-specific props here
  type?: string;                         // required if using FOOTER_MULTI_SELECT
}
export class UISomethingList extends entity.DbEntityList<UISomethingListProps> { ... }
```

---

### A2. Plugin — Backend & Search Config

`DbEntityListPlugin` — loads data from the server; requires a backend config (service, method) and search params.

```tsx
export class UISomethingPlugin extends entity.DbEntityListPlugin {

  constructor() {
    super([]);

    this.backend = {
      backend: 'crm',         // backend name (crm, fms, ...)
      context: 'company',     // optional: 'company' | 'user'
      service: 'SomeService',
      searchMethod: 'searchSomething',
    };

    this.searchParams = {
      params: {},
      filters: [...sql.createSearchFilter()],
      optionFilters: [
        sql.createStorageStateFilter([entity.StorageState.ACTIVE, entity.StorageState.ARCHIVED]),
      ],
      rangeFilters: [
        ...sql.createDateTimeFilter('requestDate', T('Request Date'), new util.TimeRange()),
      ],
      maxReturn: 1000,
    };
  }

  // Builder methods — fluent API to configure search from outside
  withStatus(status: string) {
    this.addSearchParam('status', status);
    return this;
  }

  withDateFilter(filterName: string, fromValue: string, toValue: string) {
    if (this.searchParams?.rangeFilters) {
      for (let filter of this.searchParams.rangeFilters) {
        if (filter.name === filterName) {
          filter.fromValue = fromValue;
          filter.toValue = toValue;
          break;
        }
      }
    }
    return this;
  }

  loadData(uiList: entity.DbEntityList<any>): void {
    this.createBackendSearch(uiList, { params: this.searchParams }).call();
  }
}
```

---

### A3. createVGridConfig — Skeleton

```tsx
createVGridConfig(): grid.VGridConfig {
  const { pageContext, space, type } = this.props;
  const writeCap = pageContext.hasUserWriteCapability();
  const moderatorCap = pageContext.hasUserModeratorCapability();

  let config: grid.VGridConfig = {
    id: `wfms-something-list-${space}`, // optional but recommended for state persistence
    record: {
      dataCellHeight: 40,
      editor: { enable: true, supportViewMode: ['table'] },
      control: {
        width: 30,
        items: writeCap ? [/* row action buttons */] : [],
      },
      fields: [
        entity.DbEntityListConfigTool.FIELD_INDEX(),
        ...entity.DbEntityListConfigTool.FIELD_SELECTOR(this.needSelector()),
        // ... field configs
      ],
    },
    toolbar: { hide: true },
    footer: {
      default: {
        render: (ctx: grid.VGridContext) => { /* New buttons */ return <></> }
      },
      selector: entity.DbEntityListConfigTool.FOOTER_MULTI_SELECT(T('Select'), type),
    },
    view: {
      currentViewName: 'table',
      availables: { table: { viewMode: 'table' } },
    },
  };

  return responsiveGridConfig(config); // wrap with responsiveGridConfig if the grid needs responsive behavior
}
```

---

### A4. FieldConfig Techniques

#### Basic field
```tsx
{ name: 'code', label: T('Code'), width: 120, container: 'fixed-left', filterable: true }
```

#### fieldDataGetter — computed display value
```tsx
{
  name: 'requestDate', label: T('Req. Date'), width: 110,
  filterable: true, filterableType: 'date',
  fieldDataGetter(record: any) {
    return record['requestDate'] ? util.text.formater.compactDate(record['requestDate']) : '';
  },
}
```

#### format — simple value transform
```tsx
{
  name: 'partnerName', label: T('Partner Name'), width: 350,
  format(val: string) {
    return util.text.formater.uiTruncate(val, 330, true);
  },
}
```

#### filterable options
```tsx
{ name: 'status',   filterable: true, filterableType: 'Options' }
{ name: 'date',     filterable: true, filterableType: 'date' }
{ name: 'name',     filterable: true, filterableType: 'string' }
```

#### container — sticky columns
```tsx
{ name: 'code',   container: 'fixed-left'  } // freeze left
{ name: 'status', container: 'fixed-right' } // freeze right
```

#### customRender — custom JSX cell
```tsx
{
  name: 'isRefund', label: T('Refund'), width: 60,
  customRender: (_ctx, _field, dRecord, _focus) => {
    let record = dRecord.record;
    if (record.isRefund) {
      return (
        <div className='flex-hbox align-items-center justify-content-center'>
          <FeatherIcon.CheckCircle size={16} className='text-primary' />
        </div>
      );
    }
    return <></>;
  },
}
```

#### editor — inline string edit on a field
```tsx
{
  name: 'feedback', label: T('Feedback'), width: 270,
  editor: {
    type: 'string',
    enable: writeCap,
    onInputChange: (ctx: grid.FieldContext, oldVal: any, newVal: any) => {
      if (newVal !== oldVal) {
        let record = ctx.displayRecord.record;
        // save or update logic here
        this.handleSave(record);
      }
    },
  },
}
```

#### listener.onDataCellEvent — react when another cell changes
```tsx
{
  name: 'status', label: T('Status'), width: 120,
  listener: {
    onDataCellEvent: (cell: grid.VGridCell, event: grid.VGridCellEvent) => {
      if (event.field.name === 'feedback') {
        cell.forceUpdate(); // re-render this cell when feedback changes
      }
    },
  },
}
```

#### Row control buttons (del, copy, custom per-row actions)
```tsx
control: {
  width: 30,
  items: writeCap ? [
    {
      name: 'resend', hint: T('Resend'), icon: FeatherIcon.ExternalLink,
      customRender: (ctx: grid.VGridContext, dRecord: grid.DisplayRecord) => {
        let uiList = ctx.uiRoot as UISomethingList;
        return (
          <bs.Button laf='link' className='px-1' onClick={() => uiList.onResend(dRecord)}>
            <FeatherIcon.ExternalLink size={12} />
          </bs.Button>
        );
      },
    },
  ] : [],
}
```

---

### A5. Reusable Cell Renderers

#### renderTooltipAdvanced — tooltip + copy to clipboard

> `buildTooltipValues` is a project-level helper that formats tooltip HTML and plain text from a record.
> Import it from your project's price/common module, or adapt to your own formatting logic.

```tsx
// import { buildTooltipValues } from 'app/crm/price'; // adjust to your project

const tooltipFields = [
  { key: 'note', label: 'Note' },
  { key: 'feedback', label: 'Feedback' },
];

const renderTooltipAdvanced = (_ctx: grid.VGridContext, field: grid.FieldConfig, dRecord: grid.DisplayRecord) => {
  const record = dRecord.record;
  const val = field.fieldDataGetter ? field.fieldDataGetter(record) : record[field.name];
  const { htmlFormat, textFormat } = buildTooltipValues(record, tooltipFields);

  return (
    <bs.CssTooltip width={400} position='bottom-right' offset={{ x: field.width || 120, y: 0 }}>
      <bs.CssTooltipToggle>
        <div className='flex-hbox' onClick={() => {
          navigator.clipboard.writeText(textFormat);
          bs.toastShow('Copied to clipboard!', { type: 'success' });
        }}>
          {val}
        </div>
      </bs.CssTooltipToggle>
      <bs.CssTooltipContent>{htmlFormat}</bs.CssTooltipContent>
    </bs.CssTooltip>
  );
};

// Usage — attach to any field:
{ name: 'name', label: T('Name'), width: 350, customRender: renderTooltipAdvanced }
```

#### Status cell with Popover inline change
```tsx
{
  name: 'status', label: T('Status'), width: 150,
  filterable: true, container: 'fixed-right',
  customRender: (ctx, _field, dRecord, _focus) => {
    let record = dRecord.record;
    let uiList = ctx.uiRoot as UISomethingList;
    let current = SomeStatusUtils.getStatusInfo(record['status']);
    let StatusIcon = current.icon;
    const remaining = SomeStatusUtils.getStatusList().filter(s => s.value !== record['status']);

    return (
      <bs.Popover className='d-flex flex-center w-100 h-100' title={T('Status')} closeOnTrigger='.btn'>
        <bs.PopoverToggle className={`flex-hbox flex-center px-2 py-2 rounded-2 bg-${current.color}-subtle text-${current.color} w-100`}>
          <StatusIcon size={14} className='me-1' />
          <span>{current.label}</span>
        </bs.PopoverToggle>
        <bs.PopoverContent>
          <div className='flex-vbox gap-2' style={{ width: '200px' }}>
            {remaining.map(opt => {
              let OptIcon = opt.icon;
              return (
                <div key={opt.value}
                  className={`d-flex flex-center px-2 py-1 rounded-2 bg-${opt.color}-subtle text-${opt.color} w-100 cursor-pointer`}
                  onClick={() => uiList.onChangeStatus(record, opt.value)}>
                  <OptIcon size={14} className='me-1' />
                  <span>{opt.label}</span>
                </div>
              );
            })}
          </div>
        </bs.PopoverContent>
      </bs.Popover>
    );
  },
}
```

---

### A6. Action Methods

#### Permission check — place inside the List class body

> `SESSION` comes from `const SESSION = app.host.HOST_SESSION;` at the top of the file.

```tsx
// inside UISomethingList class body
private checkPermission(record: any): boolean {
  const { pageContext } = this.props;
  const moderatorCap = pageContext.hasUserModeratorCapability();
  const writeCap = pageContext.hasUserWriteCapability();
  const isOwner = SESSION.getAccountId() === record['ownerAccountId'];

  if (!moderatorCap && !(writeCap && isOwner)) {
    bs.dialogShow(T('Access Denied'), (
      <div className='text-danger fw-bold text-center py-3'>
        <FeatherIcon.AlertCircle className='mx-2' />
        {T('You can only perform action on your own records.')}
      </div>
    ), { backdrop: 'static', size: 'md' });
    return false;
  }
  return true;
}
```

#### onDefaultSelect — open popup editor on row click
```tsx
onDefaultSelect(dRecord: grid.DisplayRecord): void {
  let record = dRecord.record;
  let { appContext, pageContext } = this.props;

  appContext.createHttpRemoteBackendCall('crm', 'SomeService', 'getSomething', { id: record.id })
    .withSuccessData((data: any) => {
      // BeanObserver: for existing, fully-loaded records fetched from server
      let observer = new entity.BeanObserver(data);
      const createPage = (appCtx: app.AppContext, pageCtx: app.PageContext) => (
        <UISomethingEditor appContext={appCtx} pageContext={pageCtx} observer={observer} />
      );
      pageContext.createPopupPage(
        `something-${util.IDTracker.next()}`,
        `Something: ${record.name}`,
        createPage,
        { size: 'flex-lg', backdrop: 'static' }
      );
    })
    .call();
}
```

#### onDeleteAction — bulk delete selected records
```tsx
onDeleteAction(): void {
  const { appContext, plugin } = this.props;
  const selectedIds = plugin.getListModel().getSelectedRecordIds();

  if (selectedIds.length === 0) {
    appContext.addOSNotification('warning', T('No records selected'));
    return;
  }

  const onConfirm = () => {
    appContext.createHttpRemoteBackendCall('crm', 'SomeService', 'deleteByIds', { ids: selectedIds })
      .withSuccessData(() => {
        appContext.addOSNotification('success', T('Deleted successfully'));
        this.reloadData();
      })
      .call();
  };
  bs.dialogConfirmMessage(T('Confirm Delete'), <div className='text-danger'>Delete selected records?</div>, onConfirm);
}
```

#### onNew — open create popup
```tsx
onNew = () => {
  let { pageContext } = this.props;
  let bean: any = {
    ownerAccountId: SESSION.getAccountId(),
    ownerLabel: SESSION.getAccountAcl().getFullName(),
    status: 'NEW',
  };
  // ComplexBeanObserver: for new beans created client-side (not yet persisted)
  let observer = new entity.ComplexBeanObserver(bean);
  const createPage = (appCtx: app.AppContext, pageCtx: app.PageContext) => (
    <div className='flex-vbox'>
      <UISomethingEditor appContext={appCtx} pageContext={pageCtx} observer={observer}
        onPostCommit={(_bean) => {
          pageCtx.back();
          this.reloadData();
        }} />
    </div>
  );
  pageContext.createPopupPage('new-something', 'New Something', createPage, { size: 'flex-lg', backdrop: 'static' });
}
```

#### Backend call pattern
```tsx
appContext
  .createHttpRemoteBackendCall('crm', 'SomeService', 'someMethod', { param: value })
  .withSuccessData((data: any) => {
    appContext.addOSNotification('success', T('Success'));
    this.vgridContext.model.addOrUpdateByRecordId(data);
    this.vgridContext.getVGrid().forceUpdateView();
  })
  .withFail(() => {
    appContext.addOSNotification('error', T('Operation failed'));
  })
  .call();
```

#### Refresh grid
```tsx
this.reloadData();                              // reload from server
this.vgridContext.getVGrid().forceUpdateView(); // re-render grid only (no server call)
this.nextViewId();                              // force full re-mount of grid component
```

---

### A7. Render Variants

#### Simple — grid only
```tsx
render() {
  if (this.isLoading()) return this.renderLoading();
  return this.renderUIGrid();
}
```

#### With top toolbar
```tsx
render() {
  const { appContext, pageContext } = this.props;
  if (this.isLoading()) return this.renderLoading();
  return (
    <div className='flex-vbox'>
      <div className='bg-white flex-hbox flex-grow-0 justify-content-between align-items-center mx-1'>
        <div className='flex-hbox justify-content-start align-items-center'>
          {/* optional: insert filter widgets here, e.g. <UIYourGridFilter context={this.vgridContext} /> */}
        </div>
        <div className='flex-hbox justify-content-end align-items-center'>
          <bs.Button laf='danger' size='sm' className='p-1' outline onClick={() => this.onDeleteAction()}>
            <FeatherIcon.Trash size={14} /> Del
          </bs.Button>
        </div>
      </div>
      <div key={this.viewId} className='flex-vbox'>
        {this.renderUIGrid()}
      </div>
    </div>
  );
}
```

---

### A8. renderHeaderBar — Search + Date Filter + Actions Toolbar

Use `renderHeaderBar()` when the list needs a top bar combining a text search input, a date range filter, and action buttons (e.g. delete). Call it from `render()` above `renderUIGrid()`.

#### State

```tsx
interface UISomethingListState {
  dateFilter: DateRangeBean;
  pattern: string;
}

export class UISomethingList extends entity.DbEntityList {
  state: UISomethingListState;

  constructor(props: any) {
    super(props);

    const today = new Date();
    const firstDayOfMonth = new Date(today.getFullYear(), today.getMonth(), 1);
    const lastDayOfMonth = new Date(today.getFullYear(), today.getMonth() + 1, 0);

    const timeRange = new util.TimeRange();
    timeRange.fromSetDate(firstDayOfMonth);
    timeRange.toSetDate(lastDayOfMonth);

    this.state = {
      dateFilter: {
        fromValue: timeRange.fromFormat(),
        toValue: timeRange.toFormat(),
        label: 'This Month',
      },
      pattern: '',
    };
  }
}
```

#### Pattern filter (client-side, no server reload)

```tsx
onChangePattern = (_oldVal: any, newVal: any) => {
  this.setState({ pattern: newVal || '' }, () => {
    if (!this.vgridContext?.model) return;
    this.vgridContext.model.getRecordFilter().withPattern(newVal || '');
    this.vgridContext.model.filter();
    this.vgridContext.getVGrid().forceUpdateView();
  });
}
```

> `withPattern` performs a client-side text filter on already-loaded records — no server call is made.

#### Plugin builder for date filter

Add a builder method to the plugin so the header bar can update the date range before reloading:

```tsx
withDateModified(fromValue: string, toValue: string) {
  if (!this.searchParams?.rangeFilters) return this;
  for (const filter of this.searchParams.rangeFilters) {
    if (filter.name === 'modifiedTime') {
      filter.fromValue = fromValue;
      filter.toValue = toValue;
      break;
    }
  }
  return this;
}
```

#### renderHeaderBar implementation

```tsx
renderHeaderBar(): React.ReactNode {
  const { appContext, pageContext, plugin } = this.props;
  const pluginImp = plugin as UISomethingPlugin;
  const { dateFilter, pattern } = this.state;

  return (
    <div className='bg-white flex-hbox flex-grow-0 justify-content-between align-items-center mx-1 px-1 py-1 border-bottom'>

      {/* Left: text search — client-side pattern filter */}
      <div className='flex-hbox align-items-center'>
        <input.WStringInput
          className='flex-hbox'
          style={{ maxWidth: 320 }}
          name='search'
          value={pattern}
          placeholder={T('Enter Code, Label...')}
          onChange={this.onChangePattern}
        />
      </div>

      {/* Center/Right: date range filter — triggers server reload */}
      <div className='flex-shrink-0 flex-hbox justify-content-end align-items-center flex-grow-0 ms-auto'>
        <WDateRangeFilter
          appContext={appContext}
          pageContext={pageContext}
          initBean={dateFilter}
          onModify={(bean) => {
            this.setState({ dateFilter: bean });
            pluginImp.withDateModified(bean.fromValue, bean.toValue);
            this.reloadData(); // server reload with updated date params
          }}
        />
      </div>

      {/* Right: action buttons */}
      <bs.Button laf='warning' outline className='p-1' onClick={() => this.onDeleteAction()}>
        <FeatherIcon.Trash2 size={12} className='me-1' />
        {T('Del')}
      </bs.Button>

    </div>
  );
}
```

#### render

```tsx
render() {
  return (
    <div className='flex-vbox h-100'>
      {this.renderHeaderBar()}
      {this.renderUIGrid()}
    </div>
  );
}
```

---

**Responsibilities summary**

| Element | Behavior |
|---|---|
| `WStringInput` + `onChangePattern` | Client-side filter — no server call, instant |
| `WDateRangeFilter` + `withDateModified` | Updates plugin params then calls `reloadData()` |
| Action button (Del) | Delegates to `onDeleteAction()` — see A6 |

---

## Pattern B: VGridEntityListEditor

**When to use:** The list is a sub-component inside a parent form (e.g. charge list inside a quotation, contact list inside a partner editor). Data does not load independently from server — it is passed in via `props.plugin` by the parent. User edits inline directly on the grid.

**When NOT to use:** The list needs its own search, independent reload, or pagination → use Pattern A.

> **Key distinction:** No Plugin class is created. The parent owns the data lifecycle. This list only reads/writes the model, then notifies the parent via `onModifyBean`.

---

### B0. Integration — How the Parent Passes Data

The parent is responsible for creating the plugin and populating its model before mounting the list.

```tsx
// Inside parent form/editor
import { entity } from '@of1-webui/lib';

// 1. Create plugin with initial records (from observer or bean)
let plugin = new entity.VGridEntityListEditorPlugin(bean['charges'] || []);

// 2. Pass plugin to the list component
<UISomethingList
  appContext={appContext}
  pageContext={pageContext}
  plugin={plugin}
  onModifyBean={(records, action) => {
    bean['charges'] = records; // write back to parent bean
  }}
/>
```

---

### B1. Class Structure

```tsx
export interface UISomethingListProps extends entity.VGridEntityListEditorProps {
  // add domain-specific props here, e.g.:
  groups?: string[];
}
export class UISomethingList extends entity.VGridEntityListEditor<UISomethingListProps> {

  constructor(props: UISomethingListProps) {
    super(props);
    // optional: pre-sort records on init
    this.props.plugin.getModel().getRecords().sort((a: any) => {
      return a['type'] === 'ORIGIN' ? -1 : 1;
    });
  }

  onModify = () => { /* see B4 — onModify implementation */ }

  createVGridConfig(): grid.VGridConfig { ... }
  createNewBean() { ... }
  render() { ... }
}
```

---

### B2. createVGridConfig — Inline Editors

> In `renderCustom`, the parameter is named `onCellInputChange` to avoid shadowing the outer `onInputChange` closure.

```tsx
createVGridConfig(): grid.VGridConfig {
  const { appContext, pageContext } = this.props;
  const writeCap = pageContext.hasUserWriteCapability();
  const CELL_HEIGHT = 40;

  // Shared change handler — calls onModify to notify parent after any edit
  const onInputChange = (ctx: grid.FieldContext, oldVal: any, newVal: any) => {
    if (oldVal !== newVal) this.onModify();
  };

  let config: grid.VGridConfig = {
    record: {
      dataCellHeight: CELL_HEIGHT,
      editor: { enable: true, supportViewMode: ['table'] },
      control: {
        width: 40,
        items: [
          {
            name: 'del', hint: 'Delete', icon: FeatherIcon.Trash2,
            onClick: (ctx: grid.VGridContext, dRecord: grid.DisplayRecord) => {
              ctx.model.removeRecord(dRecord.record);
              ctx.getVGrid().forceUpdateView();
              this.onModify();
            },
          },
          {
            name: 'copy', hint: 'Copy', icon: FeatherIcon.Copy,
            onClick: (ctx: grid.VGridContext, dRecord: grid.DisplayRecord) => {
              let copy = JSON.parse(JSON.stringify(dRecord.record));
              this.vgridContext.model.insertDisplayRecordAt(dRecord.row, copy);
              ctx.getVGrid().forceUpdateView();
              this.onModify();
            },
          },
        ],
      },
      fields: [
        entity.DbEntityListConfigTool.FIELD_INDEX(),
        ...entity.DbEntityListConfigTool.FIELD_SELECTOR(this.needSelector()),

        // Simple string editor
        {
          name: 'note', label: T('Notes'), width: 400,
          editor: { type: 'string', enable: writeCap, onInputChange },
        },

        // Currency field with renderCustom
        {
          name: 'unitPrice', label: T('Unit Price'), width: 120,
          editor: {
            type: 'currency', enable: writeCap,
            renderCustom: (ctx: grid.FieldContext, onCellInputChange: grid.OnInputChange) => {
              const { tabIndex, focus, displayRecord, fieldConfig } = ctx;
              return (
                <input.BBCurrencyField bean={displayRecord.record} precision={3}
                  style={{ height: CELL_HEIGHT }} field={fieldConfig.name}
                  tabIndex={tabIndex} focus={focus} onInputChange={onCellInputChange} />
              );
            },
            onInputChange,
          },
        },

        // Ref selector with renderCustom
        {
          name: 'currency', label: T('Curr'), width: 80,
          editor: {
            type: 'string', enable: writeCap,
            renderCustom: (ctx: grid.FieldContext, onCellInputChange: grid.OnInputChange) => {
              const { tabIndex, focus, fieldConfig, displayRecord } = ctx;
              return (
                <module.settings.BBRefCurrency
                  tabIndex={tabIndex} autofocus={focus}
                  style={{ height: CELL_HEIGHT }} placeholder='Curr' minWidth={150}
                  appContext={appContext} pageContext={pageContext} required hideMoreInfo
                  bean={displayRecord.record} beanIdField={fieldConfig.name}
                  onPostUpdate={(_ui, _bean, _opt, _input) => onCellInputChange(displayRecord.record, '', null, null)} />
              );
            },
            onInputChange,
          },
        },

        // Percent field
        {
          name: 'taxRate', label: T('VAT (%)'), width: 100,
          customRender: (_ctx, _field, dRecord, _focus) => (
            <div>{util.text.formater.percent(dRecord.record.taxRate)}</div>
          ),
          editor: {
            type: 'percent', enable: true,
            renderCustom: (ctx: grid.FieldContext, onCellInputChange: grid.OnInputChange) => {
              const { tabIndex, focus, displayRecord } = ctx;
              return (
                <input.BBPercentField bean={displayRecord.record}
                  style={{ height: CELL_HEIGHT }} field='taxRate'
                  tabIndex={tabIndex} focus={focus} onInputChange={onCellInputChange} />
              );
            },
            onInputChange,
          },
        },
      ],
    },
    toolbar: { hide: true },
    view: {
      currentViewName: 'table',
      availables: { table: { viewMode: 'table' } },
    },
  };
  return config;
}
```

---

### B3. createNewBean

```tsx
createNewBean() {
  return {
    type: 'ORIGIN',
    currency: 'USD',
    quoteRate: {},
    // set any default field values here
  };
}
```

---

### B4. onModify — Notify Parent

```tsx
onModify = () => {
  const { onModifyBean } = this.props;
  let records = this.vgridContext.model.getRecords();
  if (onModifyBean) onModifyBean(records, entity.ModifyBeanActions.MODIFY);
}

// Add new record
addRecord = () => {
  let item = this.createNewBean();
  this.vgridContext.model.addRecord(item);
  grid.initRecordState(item, 0).markNew();
  this.onModify();
  this.forceUpdate();
}

// Clear all or selected
onClear = () => {
  let selected = this.vgridContext.model.getSelectedDisplayRecords();
  if (selected.length > 0) {
    this.vgridContext.model.removeSelectedDisplayRecords();
    this.vgridContext.getVGrid().forceUpdateView();
    this.onModify();
  } else {
    bs.dialogConfirmMessage(T('Clear'), T('Clear all records?'), () => {
      this.vgridContext.model.update([]);
      this.vgridContext.getVGrid().forceUpdateView();
      this.onModify();
    });
  }
}
```

---

### B5. Render with Custom Toolbar

```tsx
render() {
  const { pageContext } = this.props;
  const writeCap = pageContext.hasUserWriteCapability();

  return (
    <div className='flex-vbox h-100'>
      <div className='bg-white border rounded-3 flex-vbox w-100 h-100'>

        <div className='flex-hbox flex-grow-0 align-items-center justify-content-between px-2 py-1'>
          <h5 className='text-muted'>
            <FeatherIcon.List className='me-2' size={16} />
            {T('Something List')}
          </h5>
          {writeCap && (
            <div className='flex-hbox justify-content-end align-items-center'>
              <bs.Button laf='success' className='border-0 py-1 px-1' outline onClick={this.addRecord}>
                <FeatherIcon.Plus size={12} /> {T('Add')}
              </bs.Button>
              <bs.Button laf='info' className='border-0 py-1 px-1' outline onClick={this.onClear}>
                <FeatherIcon.Trash2 size={12} /> {T('Clear')}
              </bs.Button>
            </div>
          )}
        </div>

        <div className='flex-vbox'>
          <grid.VGrid context={this.vgridContext} />
        </div>

      </div>
    </div>
  );
}
```

---

## Quick Reference

| Technique | Pattern | Section |
|---|---|---|
| Plugin: backend config, search params | A | A2 |
| Plugin: builder methods (withXxx) | A | A2 |
| createVGridConfig skeleton | A, B | A3, B2 |
| fieldDataGetter — computed display | A, B | A4 |
| format — simple value transform | A | A4 |
| filterable / filterableType | A | A4 |
| container fixed-left / fixed-right | A | A4 |
| customRender — custom JSX cell | A, B | A4 |
| editor — inline string edit | A, B | A4, B2 |
| editor renderCustom — BBCurrencyField, BBRefXxx, BBPercentField | B | B2 |
| listener.onDataCellEvent | A | A4 |
| Row control buttons (del, copy, custom) | A, B | A4, B2 |
| renderTooltipAdvanced — tooltip + copy | A | A5 |
| Status cell with Popover inline change | A | A5 |
| Permission check (writeCap, moderatorCap, ownership) | A | A6 |
| onDefaultSelect — open popup on row click | A | A6 |
| onDeleteAction — bulk delete | A | A6 |
| onNew — create popup | A | A6 |
| BeanObserver vs ComplexBeanObserver | A | A6 |
| Backend call: createHttpRemoteBackendCall | A | A6 |
| reloadData / forceUpdateView / nextViewId | A | A6 |
| Render: grid only vs. with toolbar | A | A7 |
| Integration — parent passes data via plugin | B | B0 |
| createNewBean — default record shape | B | B3 |
| onModify → onModifyBean callback | B | B4 |
| Add / clear records | B | B4 |
| Render with custom toolbar | B | B5 |
