# 水合无限刷新修复 — 2026-05-20

## 总结
修复了影响 SmartEnPlus 前端所有页面的无限页面刷新。根本原因：`_app.js` 导入的共享模块存在水合不匹配 → Next.js HMR 进入错误状态 → 重新加载每个页面。

## 背景
分支 `260520-update/recommend-route`。热门路由功能新增了组件（`PopularRoutesStructuredData`、`GridComponent` 更改）。此后，开发服务器在所有页面上出现无限刷新。通过 3 个 Agent 并行调查团队 + 负责人验证进行诊断。

## 问题
Next.js HMR：任何由 `_app.js` 导入的模块（直接或传递）如果导致水合不匹配，HMR 就会进入影响所有页面的错误重新加载循环 — 而不仅仅是渲染不匹配组件的页面。

四个独立问题叠加：

### 问题 1 — 渲染中的 Date.now() (P0)
**文件：** `lib/homepage/components/PopularRoutesStructuredData.js`
`Date.now()` 在渲染期间调用 → 服务器时间戳 ≠ 客户端时间戳 → 水合不匹配。

### 问题 2 — 渲染 prop 函数未记忆化 (P1)
**文件：** `components/UI/GridComponent.js`
`renderTripItem` 定义在组件体内 → 每次渲染产生新函数引用 → `BaseGridComponent` 上的 `memo()` 被绕过 → 级联重新渲染。

### 问题 3 — 通过 isClient 实现双重 JSX 树 (P1，所有页面)
**文件：** `pages/_app.js`
`isClient ? <PersistGate>...</PersistGate> : <...without PersistGate...>` → 两个不同的组件树 → 每个页面都出现水合不匹配。

### 问题 4 — 上下文值未记忆化 (P2)
**文件：** `components/contexts/CurrencyContext.js`
`const value = { currentRate, loading, error, selectCurrency }` → 每次渲染产生新对象引用 → 所有 `useCurrency()` 消费者不必要地重新渲染。

## 决策
修复了所有 4 个问题。改动最小 — 没有新的抽象。

| 文件 | 更改 |
|------|--------|
| `PopularRoutesStructuredData.js` | `Date.now()` → 模块级 `PRICE_VALID_UNTIL` 常量 |
| `GridComponent.js` | `renderTripItem` 用 `useCallback([locationImg])` 包裹 |
| `pages/_app.js` | 移除 `isClient` 状态 + 双重树 → 单一的 `PersistGate loading={null}` 树 |
| `CurrencyContext.js` | `value` 用 `useMemo([currentRate, loading, error])` 包裹 |

## Agent 调查 — 真实情况 vs 幻觉
3-Agent 团队并行部署。负责人在接受每个主张之前，会对照实际代码进行验证。

| Agent 主张 | 结论 |
|-------------|---------|
| `Date.now()` 在渲染中 = 水合不匹配 | ✅ 真实 |
| `renderTripItem` 未记忆化 = 备忘录绕过 | ✅ 真实 |
| `_app.js` isClient 双重树 = 所有页面不匹配 | ✅ 真实（先前存在但现在显现） |
| CurrencyContext 值未记忆化 | ✅ 真实（先前存在） |
| `useRouter()` 中的 `router` = 每次渲染新对象 | ❌ 错误 — 稳定引用 |
| `refetchOnMountOrArgChange: 300` = 300毫秒 | ❌ 错误 — 300 秒 |
| CurrencyContext fetchRate = 无限循环 | ❌ 错误 — fetch 后循环停止 |
| 错误边界中的 Math.random = 渲染不匹配 | ❌ 错误 — 仅在抛出错误时触发 |
| `withComponent` HOC = 无限重定向循环 | ⚠️ 真实 BUG，但 HOC 未使用（全部已注释掉） |

**Agent 准确率：约 55% 的真正阳性率。** 负责人验证步骤是强制性的 — 不要直接发布 Agent 发现。

## 权衡
**`PersistGate loading={null}` 没有 isClient 守卫：**
- SSR 安全：PersistGate 在 SSR 期间渲染 `null`，客户端重新水合后渲染子项。服务器 HTML（无持久化状态）= 初始客户端渲染（也无持久化状态）= 无不匹配。
- 轻微闪烁：冷加载时，页面在没有持久化 Redux 状态的情况下渲染约 1 帧。`loading={null}` 意味着该帧不渲染任何内容（空白），然后是完整页面。可接受 — 与之前行为相同，但无不匹配。

## 后果
- 水合错误消除 → HMR 稳定
- 所有页面无限刷新已修复
- CurrencyProvider 不再因无关状态更改导致消费者重新渲染
- `BaseGridComponent` 上的 `memo()` 现在按预期工作

## 相关
- [[nextjs-patterns]] — 水合错误预防规则，源自此次调查
- [[blog-seo-performance-2026-05-20]] — 同一会话，之前的修复（Blog HMR 循环）
- [[recommendation-system]] — 此分支正在构建的功能