# 音乐关系约束下的混音局部编辑

**Musical Relationship Constraints in AI-Assisted Local Mix Editing**

《人工智能混音局部编辑的音乐关系约束研究》的代码与研究文档。S1、S2补充材料以可直接阅读的Markdown文档提供。

## 研究文档

| 入口 | 内容与状态 |
| --- | --- |
| [S1：合成信号与总线压缩核验](docs/S1_signal_verification.md) | 完整输入、包络、处理配置、残差计算和历史参考值。已有组件运行记录。 |
| [S2：验证协议与候选比较](docs/S2_listening_protocol.md) | 候选池、代价口径、试听量表和统计规划。听觉研究尚未实施。 |
| [本次复算记录](docs/reproduction_check.md) | 对原始脚本的实际复算，与历史记录分开保存。 |
| [实现范围与来源](docs/provenance.md) | 原材料来源、此次迁移调整及代码的实现边界。 |
| [发布许可说明](docs/licensing.md) | 公开材料范围及许可状态。 |

这不是成品自动混音软件，不包含训练好的音乐模型，也不包含商业插件或受限歌曲分轨。最小干预原则在已符合任务要求的候选中比较代价；有限候选中的优先方案不代表全域最优。

## 先运行无需第三方依赖的候选演算

在仓库根目录执行（Python 3.10或以上）：

```bash
mkdir -p output
python3 code/candidate_protocol.py --output output/analytical_candidates.json
python3 -m unittest discover -s tests -v
```

程序枚举51个双轨增益组合，检查正向、零目标和反向目标，以及A、D两项的代价。评分函数的测试使用人工构造输入，只检验函数逻辑；没有生成或保存虚构听者数据。

## 运行S1组件核验

历史参考环境和本次打包环境均使用Python 3.13.5、NumPy 2.3.5、SoundFile 0.13.1、Pedalboard 0.9.23。先建立隔离环境，再按固定依赖安装：

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -r code/requirements.txt
python code/run_dsp_example.py --out output/dsp
```

完整输出在`output/dsp/`，包括36秒合成音频、20—22秒片段、`results.json`与残差轨迹。输出为浮点音频，不属于可直接当作音乐作品播放的示例；试听前先降低监听电平。

**原脚本可能覆盖同一输出目录内同名文件，重复运行请使用新的输出目录。**`output/`默认不提交。历史记录位于`records/reference/`，不得用新结果覆盖；本次打包复算位于`records/reproductions/package_check/`。

## 已实现与未实现

- 已提供：双轨增益演算、共享总线压缩组件核验、51候选选择示例、单一目标评分及任务汇总函数、完整听觉协议。
- 尚未提供：REAPER自动执行器、真实作品的底鼓／贝斯均衡渲染、通用多目标听评系统、功效模拟程序、实际听者数据，以及AI模型端到端实验。

代码中的`G`默认共同权限和技术检查已在这一固定演算场景满足；它没有连接宿主或实现通用权限审查。`listening_pass`实现的是单目标演示，不得直接声称覆盖S2中的多目标协议。噪声、点击声和削波检查是主稿规定的实施要求，当前脚本没有自动检测这些问题。

## 版本与引用

本仓库于2026-10-16公开：[stonestarskyer-source/relational-mix-editing](https://github.com/stonestarskyer-source/relational-mix-editing)。论文主稿以v1.9为本次对齐依据；核心脚本逐字保留自v1.8材料。版本标识为`paper-v1.9`，最终提交编号由对应标签及Release记录。引用固定提交下的S1／S2文件，不只指向不断更新的主分支。本材料没有DOI。

Apple Silicon Mac实际核验已完成：Python 3.13.5、固定依赖、15项测试及原始DSP自检通过。平台间数值和样本差异见[复算说明](docs/reproduction_check.md#2026-10-16-apple-silicon-mac-实际复算)。

论文全文与作者工作记录不属于本仓库的发布内容。论文署名、发表状态与最终许可均不能从代码运行成功推定。
