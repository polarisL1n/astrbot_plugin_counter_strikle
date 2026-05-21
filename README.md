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

计划支持：

- 候选人过滤和下一猜推荐
- 更完整的选手数据库
- 可选的 BLAST 数据同步
- MCP 工具接口，供外部 Agent 调用

## 数据说明

当前内置选手数据是用于玩法验证的本地快照，不是权威实时数据库。队伍、年龄、Major 数量等字段会随时间变化，正式使用前建议维护或接入同步脚本。

## 指令

```text
/cs开始
/cs猜 <选手名>
/cs状态
/cs建议
/cs放弃
/cs帮助
```

示例：

```text
/cs开始
/cs猜 m0NESY
/cs建议
```

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
