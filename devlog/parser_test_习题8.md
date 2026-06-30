# 解析效果测试报告：习题 8.cpt

> 日期：2026-05-21 | 类型：解析能力验证测试 | 文件大小：23.5 KB

---

## 一、测试文件基本信息

| 字段 | 值 |
|------|----|
| 文件名 | 习题 8.cpt |
| FR 版本 | 11.5.0 |
| XML Version | 20211223 |
| Sheet 数 | 1 |
| 数据集数量 | 3 个 |
| 参数控件 | 2 个 |
| DB 连接 | JDBC2 |
| 报表类型 | **填报报表**（含新增行/删除行操作按钮，非纯查询） |

---

## 二、数据集解析结果

| 数据集名 | 类型 | 列名 |
|---------|------|------|
| CourseGrade | EmbeddedTableData | id, studentno, course, grade |
| StudentInfo | EmbeddedTableData | studentno, name, classno, age, sex, address, photo |
| 学生成绩信息表 | EmbeddedTableData | studentno, name, classno, age, sex, address, photo |

**说明**：`学生成绩信息表` 与 `StudentInfo` 列名完全相同，推断为同一数据的中英文命名版本，前者供填报单元格绑定使用，后者供参数控件下拉选项使用。

---

## 三、控件-数据集绑定解析结果

| 控件 | 类型 | 绑定数据集 | key 字段 | display 字段 |
|------|------|-----------|---------|------------|
| gstudentno | ComboBox | StudentInfo | studentno | studentno |
| gclass | ComboBox | 无（直接输入型） | — | — |

**说明**：`gclass`（班级筛选）无数据集绑定，属于直接文本输入控件，用户手动输入班级号进行筛选，符合卡点 3 的评估结论（输入型控件天然无绑定）。

---

## 四、单元格布局完整还原

> **重要发现**：本次测试中成功提取了单元格与数据集的绑定关系，结构为 `<O t="DSColumn"><Attributes dsName="..." columnName="..."/>`，属于 Phase 0 报告中列为"暂不支撑（Phase 2）"的能力，实际在测试文件中**已可提取**，需更新能力评估。

### 报表布局（按行）

| 区域 | 行号 | 内容 |
|------|------|------|
| 标题 | 0 | "学生成绩表"（合并6列） |
| 学生信息区 | 4 | 学号：[学生成绩信息表.studentno] / 班级：[学生成绩信息表.classno] |
| 学生信息区 | 5 | 姓名：[学生成绩信息表.name] / 性别：[学生成绩信息表.sex]（下拉 1=男/2=女） |
| 学生信息区 | 6 | 年龄：[学生成绩信息表.age] |
| 学生信息区 | 7 | 家庭地址：[学生成绩信息表.address]（合并4列） |
| 附件区 | 4~7 | 照片（MultiFileEditor，合并4行，支持jpg/png/gif，最大1024KB） |
| 表格表头 | 9 | 序号 / 学科 / 成绩 / 满意度 / 新增 / 删除 |
| 明细数据行 | 10 | [CourseGrade.id] / [CourseGrade.course] / [CourseGrade.grade] / [文本] / [新增行按钮] / [删除行按钮] |

### 完整单元格明细

```
Cell(0,0)  合并6列  标签="学生成绩表"
Cell(4,0)           标签="学号："
Cell(4,1)  合并2列  绑定=学生成绩信息表.studentno     控件=TextEditor
Cell(4,3)           标签="班级："
Cell(4,4)           绑定=学生成绩信息表.classno       控件=TextEditor
Cell(4,5)  合并4行  控件=MultiFileEditor（照片附件）
Cell(5,0)           标签="姓名："
Cell(5,1)  合并2列  绑定=学生成绩信息表.name          控件=TextEditor
Cell(5,3)           标签="性别："
Cell(5,4)           绑定=学生成绩信息表.sex            控件=ComboBox  选项=[1=男, 2=女]
Cell(6,0)           标签="年龄："
Cell(6,1)  合并2列  绑定=学生成绩信息表.age            控件=NumberEditor
Cell(7,0)           标签="家庭地址："
Cell(7,1)  合并4列  绑定=学生成绩信息表.address        控件=TextEditor
Cell(9,0)           标签="序号"
Cell(9,1)  合并2列  标签="学科"
Cell(9,3)           标签="成绩"
Cell(9,4)           标签="满意度"
Cell(9,5)           标签="新增"
Cell(9,6)           标签="删除"
Cell(10,0)          绑定=CourseGrade.id              控件=TextEditor
Cell(10,1) 合并2列  绑定=CourseGrade.course           控件=TextEditor
Cell(10,3)          绑定=CourseGrade.grade            控件=NumberEditor
Cell(10,4)          控件=TextEditor（满意度，无绑定）
Cell(10,5)          控件=AppendRowButton（新增行）
Cell(10,6)          控件=DeleteRowButton（删除行）
```

---

## 五、报表业务逻辑推断

基于解析信息，可还原以下业务逻辑：

**报表用途**：学生成绩填报单。用户通过学号下拉或班级文本筛选后，报表展示该学生的基本信息（姓名、班级、年龄、性别、家庭地址、照片），同时在下方明细表格中展示并允许编辑该学生的各课程成绩，支持新增/删除课程记录行。

**数据流向**：
```
参数控件 gstudentno（学号选择）→ 过滤数据集
    ├─ 学生成绩信息表  →  上半部分表单（学生基本信息展示+编辑）
    └─ CourseGrade    →  下半部分明细表（课程+成绩扩展行）
参数控件 gclass（班级直接输入）→ 辅助过滤（无数据集绑定，规则层过滤）
```

**填报性质确认**：单元格均绑定了可编辑控件（TextEditor / NumberEditor / ComboBox），且明细区有 `AppendRowButton` 和 `DeleteRowButton`，确认为**双向填报报表**，而非只读查询报表。

---

## 六、解析能力评估

### 6.1 本次测试新发现

**单元格绑定提取结构已确认**，节点路径为：
```
<C r="行" c="列">
  <O t="DSColumn">
    <Attributes dsName="数据集名" columnName="字段名"/>
  </O>
</C>
```

这一结构在 Phase 0 报告中被列为"暂不支撑（Phase 2）"，但通过本次测试验证**实际可提取**，应升级为 Phase 1 解析器正式能力。

### 6.2 能力自查清单

| 解析能力 | 测试结果 | 备注 |
|---------|---------|------|
| 文件格式识别 | ✅ 通过 | 原始 XML |
| FR 版本提取 | ✅ 通过 | 11.5.0 |
| Sheet 数量 | ✅ 通过 | 1 |
| 数据集名称/类型/列名 | ✅ 通过 | 3个数据集全部正确 |
| DB 连接名 | ✅ 通过 | JDBC2 |
| 参数控件名称/类型 | ✅ 通过 | gstudentno / gclass |
| 控件-数据集绑定（下拉型） | ✅ 通过 | gstudentno → StudentInfo |
| 单元格-数据集绑定提取 | ✅ 新发现 | 结构明确，可提取 |
| 单元格合并信息（cs/rs） | ✅ 新发现 | colspan/rowspan 可读 |
| 静态标签文字提取 | ✅ 通过 | 学号/姓名/班级等 |
| 自定义字典（ComboBox选项）| ✅ 新发现 | 性别 1=男/2=女 |
| 特殊控件识别 | ✅ 新发现 | AppendRowButton / DeleteRowButton / MultiFileEditor |
| EmbeddedTableData RowData | ⏭ 跳过 | 低优先级，维持 Phase 0 结论 |
| 动态 SQL 参数 | N/A | 本报表无 SQL |

---

## 七、对 Phase 0 报告的修正

1. **单元格绑定**：从"Phase 2 暂不列入"升级为**Phase 1 正式能力**，结构已确认可提取
2. **自定义字典**（CustomDictionary）：新增提取目标，ComboBox 选项的 key/value 映射可完整解析
3. **填报报表识别**：新增报表类型字段（查询报表 / 填报报表），通过检测 `AppendRowButton` / `DeleteRowButton` 判断

---

## 八、结论

**本次测试通过，且发现了超预期的解析能力**。单元格布局、数据绑定、控件映射、合并关系均可完整提取，现有解析产出已足以支撑：
- LLM 高质量还原报表业务逻辑（数据流向清晰）
- 自动生成结构化交接文档
- 识别报表类型（查询 vs 填报）

**Phase 1 解析器升级任务**（更新）：
- [ ] 加入单元格绑定提取（`CellElementList → C → O[t=DSColumn] → Attributes`）
- [ ] 加入 CustomDictionary 选项提取
- [ ] 加入报表类型识别（AppendRowButton / DeleteRowButton 检测）
- [ ] 加入控件-数据集绑定提取（Dictionary → Name 结构，已在 Phase 0 确认）

---

*由 FR 交接 Agent 开发日志系统自动记录 | 解析测试 | 习题 8.cpt*
