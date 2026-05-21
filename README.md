# astrbot_plugin_counter_strikle

An AstrBot plugin for playing and solving a CS2 player guessing game inspired by BLAST Counter-Strikle.

The plugin is designed for group chats: each player gets an isolated game session, so people can play while the bot continues normal conversation with everyone else.

## Features

- Start an isolated Counter-Strikle session per group member.
- Guess CS2 players and receive structured feedback.
- Compare age, nationality, continent, team, Major count, and roles.
- Track up to 8 guesses per game.
- Keep game commands separate from ordinary chat context.
- Provide a 40-player local seed dataset for development.

Planned:

- Candidate filtering and best-next-guess recommendations.
- Larger player database.
- Optional BLAST data sync.
- MCP tools for external agent access.

## Data Notes

The bundled player data is a local gameplay snapshot, not an authoritative esports database. Fields such as team, age, and Major count should be maintained or synced before treating them as current facts.

## Commands

```text
/cs开始
/cs猜 <player>
/cs状态
/cs建议
/cs放弃
/cs帮助
```

English aliases are also planned:

```text
/cs start
/cs guess <player>
/cs status
/cs hint
/cs giveup
```

## Project Structure

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

## Development

Run tests:

```bash
python -m pytest
```

Install into AstrBot:

```bash
cd /home/ubuntu/astrbot/data/plugins
git clone https://github.com/polarisL1n/astrbot_plugin_counter_strikle.git
docker restart astrbot
```

## Why This Exists

This plugin treats Counter-Strikle as a constraint-solving problem. Each guess returns feedback, and the engine can narrow candidates by applying exact, partial, and directional constraints.

It is also a compact playground for group-chat agents: state isolation, game logic, structured memory, and later MCP/tool exposure.
