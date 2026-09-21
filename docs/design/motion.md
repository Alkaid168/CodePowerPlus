# 动效规范

动效不是装饰层。实现前先回答：这个交互每天发生多少次、动画要解决什么问题、是否可以用更便宜的技术完成。

## 1. 先做决策

| 使用频率 | 决策 |
| --- | --- |
| 每天 100 次以上：命令面板、导航切换、键盘动作 | 不做开合或缩放动画 |
| 每天几十次：按钮、行悬停、列表导航 | 只做近乎不可察觉的反馈，`100–180ms` |
| 偶尔：弹层、抽屉、Toast | 标准过渡，`180–320ms` |
| 首次或低频：成功、完成引导 | 可以使用短暂错峰和更明显的反馈 |

键盘触发的动作不能依赖动画完成才能继续输入。

## 2. 动效目的

每个动画必须属于以下一种：

- Feedback：按钮按下、切换成功、错误反馈。
- Spatial consistency：弹层从触发位置出现，也沿原路退出。
- State indication：选中、加载、禁用、审核状态变化。
- Preventing jarring change：列表、页面或面板内容替换时的桥接。
- Explanation / Delight：只用于低频或首次体验。

无法命名目的的动画不要实现。

## 3. 技术选择

| 需求 | 实现 |
| --- | --- |
| Hover、press、颜色、开关 | CSS transition |
| 挂载时一次性进入 | CSS `@starting-style` 或短 CSS animation |
| 固定预演动画 | CSS animation |
| 需要 JS 控制的合成动画 | WAAPI |
| 拖拽、手势、弹簧、可打断布局 | Motion 或等价弹簧库 |

不要为淡入淡出引入完整动画库。不要用 `requestAnimationFrame` 模拟可以直接交给 CSS 的固定动画。

## 4. 性能属性

只动画 `transform`、`opacity`，必要时使用 `clip-path`。折叠面板允许使用 `height`。禁止动画 `width / margin / padding / top / left`。

## 5. 曲线

```css
--ease-out: cubic-bezier(0.23, 1, 0.32, 1);
--ease-in-out: cubic-bezier(0.77, 0, 0.175, 1);
--ease-drawer: cubic-bezier(0.32, 0.72, 0, 1);
```

- 进入、退出和系统反馈使用 `ease-out`。
- 屏幕内移动和布局变化使用 `ease-in-out`。
- 悬停颜色使用普通 `ease`。
- 禁止在 UI 进入时使用 `ease-in`。
- 抽屉优先使用 `ease-drawer`。

## 6. 时长

| 场景 | 时长 |
| --- | --- |
| 按钮按下 | `100–120ms` |
| 悬停、颜色变化 | `140–180ms` |
| Tooltip、小气泡 | `125–200ms` |
| Dropdown、Select | `150–250ms` |
| 卡片进入 | `220–300ms` |
| Modal | `240–320ms` |
| Drawer | `280–380ms` |
| Toast 进出 | `180–240ms` |
| 页面内容切换 | `240–320ms` |

除明确说明外，UI 动效控制在 `300ms` 内。大面板或抽屉可延长到 `380ms`。

## 7. 组件规则

### 按钮

- pointer-down 立即可见反馈。
- pressed：`scale(.975)`，`100–120ms`。
- Hover 只上移 `1px`，不使用彩色 glow。
- Disabled 不播放 hover 或 press。

### 卡片

- Hover：`translateY(-2px)`，`160–180ms`。
- 可点击卡片可轻微上移；静态卡片原则上不移动，总览指标卡允许 `2px` 上移与边界加深。
- 多个卡片进入时按 `30–80ms` 错峰，不一起跳入。

### 弹层

- 从触发元素原点缩放，起始 `scale(.96)` + `opacity: 0`，禁止 `scale(0)`。
- 进入 `180–220ms`，退出 `140–180ms`。
- Modal 可以居中，但仍从 `scale(.97)` 开始。
- 进入和退出路径必须对称。

### 侧栏与 Tabs

- 选择状态用颜色和背景切换，不做滑动胶囊追逐。
- 高频导航不播放整页滑动。
- 页面切换最多使用 `opacity + translateY(6px)`，`240–280ms`。

### 列表与表格

- 数据内容不为装饰而移动。
- 新增行可以进行 `opacity + translateY(6px)`，退出沿原方向。
- 行 hover 只改变背景或边界，不改变行高。

### Toast 与 Switch

- 使用 transition，不用 keyframes。
- Toast 从进入方向退出。
- 用户连续触发时从当前状态重新定向，不重新从头播放。

### Slider 与拖拽

- 滑块位置必须在拖动过程中 1:1 更新。
- 拖动结束可以使用弹簧接管速度。
- 默认弹簧：`{ type: "spring", duration: .4, bounce: 0 }`。
- 只有带惯性的甩动或拖拽关闭才使用 `bounce: .1–.2`。
- 边界采用渐进阻力，不突然冻结。

## 8. 键盘与打断

- 高频命令不能等待动画结束才能接收下一次输入。
- 弹层、抽屉、Toast 的动画期间不能锁死 pointer 或 keyboard。
- 任何可反复触发的元素优先使用 transition，保证可以从中途重定向。
- 手势使用弹簧并继承当前速度。

## 9. 无障碍降级

```css
@media (hover: hover) and (pointer: fine) {
  .interactive:hover { /* 仅精确指针 */ }
}

@media (prefers-reduced-motion: reduce) {
  .moving { transform: none !important; transition: opacity 160ms ease; }
}

@media (prefers-reduced-transparency: reduce) {
  .floating { background: #fff; backdrop-filter: none; }
}

@media (prefers-contrast: more) {
  .control { border-color: #111; background: #fff; }
}
```

减少动态不是删除全部反馈。保留颜色、边界、透明度和短交叉淡化，删除位置移动、弹簧和持续动画。

## 10. 禁止项

- `transition: all`
- `scale(0)` 进入
- UI 进入使用 `ease-in`
- 高频操作使用 keyframes
- 无目的持续漂浮
- 彩色外发光
- 多个元素同时无错峰出现
- 为每张静态数据卡添加视差
- 动画期间阻止第二次输入


## 11. 页面与卡片入场

- 页面切换时，所有 `.card` 使用 `card-enter`：`opacity 0 → 1` 与 `translateY(7px) → 0`。
- 默认时长 `300ms`，使用 `--ease-out`；同一容器通过 `36ms` 递增延迟形成轻量错峰。
- 不再使用顶栏；左侧栏固定，只有主体内容滚动。
- `prefers-reduced-motion` 下改为 `160ms` 透明度过渡，不移入位置。
- 表格行、输入框等高频控件不播放页面级入场动画。

