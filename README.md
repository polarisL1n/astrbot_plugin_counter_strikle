# astrbot_plugin_counter_strikle

一个给 AstrBot 用的 CS2 猜选手小游戏插件，灵感来自 BLAST 的 Counter-Strikle。

插件面向群聊场景设计：每个玩家都有独立游戏会话，群里有人玩游戏时，其他人仍然可以正常和 Bot 聊天。

## 功能

- 按群成员隔离 Counter-Strikle 游戏会话
- 猜 CS2 选手并返回结构化反馈
- 比较年龄、国籍、洲、队伍、Major 数量和位置
- 每局最多 8 次猜测
- 游戏命令和普通聊天上下文隔离
- 内置 40 人本地种子数据集，方便先跑通玩法
- 当前版本不依赖大模型，核心玩法由规则引擎完成
- 可选 LLM 短评价：开启后用当前会话模型生成一句不剧透的轻量评价
- 第 4 次未猜中时给出一条本地趣味提示

计划支持：

- 候选人过滤和下一猜推荐
- 更完整的选手数据库
- 可选的 BLAST 数据同步
- MCP 工具接口，供外部 Agent 调用

## 数据说明

当前内置选手数据是用于玩法验证的本地快照，不是权威实时数据库。队伍、年龄、Major 数量等字段会随时间变化，正式使用前建议维护或接入同步脚本。

## 指令

```text
/cs
/cs开始
/cs 开始
/cs猜 <选手名>
/cs 猜 <选手名>
/cs状态
/cs建议
/cs放弃
/cs帮助
```

示例：

```text
/cs
/cs开始
/cs猜 m0NESY
/cs建议
```

单独输入 `/cs` 会显示新手教程，包括玩法、反馈含义、命令说明和会话隔离规则。

## 可选 LLM 增强

插件默认不依赖大模型。后台配置里可以打开 `enable_llm_commentary`，打开后每次猜测会调用当前会话使用的聊天模型，生成一行短评价。

为了不干扰游戏本身，LLM 只负责替换 `评价：...` 这一行：

```text
评价：这手方向不算歪，继续压范围。
```

如果模型不可用、超时或返回空内容，插件会自动回退到本地模板评价。第 4 次未猜中时的 `提示：...` 来自本地选手数据，不需要调用模型。

## 项目结构

```text
astrbot_plugin_counter_strikle/
├── main.py
├── metadata.yaml
├── requirements.txt
├── counter_strikle/
│   ├── __init__.py
│   ├── data/
│   │   └── players.json
│   ├── game.py
│   ├── models.py
│   ├── solver.py
│   └── storage.py
└── tests/
    └── test_game.py
```

## 本地开发

运行测试：

```bash
python3 -m pytest
```

如果本地没有安装 pytest，可以先做核心冒烟测试：

```bash
python3 -c "from counter_strikle.game import create_game; from counter_strikle.solver import filter_candidates; g=create_game(answer_id='donk'); g.guess('m0NESY'); assert any(p.id=='donk' for p in filter_candidates(g.players,g.guesses)); print('ok')"
```

安装到 AstrBot：

```bash
cd /home/ubuntu/astrbot/data/plugins
git clone https://github.com/polarisL1n/astrbot_plugin_counter_strikle.git
docker restart astrbot
```

## 设计思路

Counter-Strikle 本质上是一个约束求解问题。每次猜测都会产生反馈，插件根据完全匹配、半匹配、方向提示等约束逐步缩小候选人集合。

这个项目也可以作为群聊 Agent 的小型实验场：会话隔离、规则引擎、结构化状态、候选推荐，以及后续的 MCP 工具化都能在这里逐步加上。
