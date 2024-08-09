# Suilend Capsule CLI

## Installation

1. Ensure Python 3.12 is installed (use [Pyenv](https://github.com/pyenv/pyenv) to install if needed).
2. Ensure Poetry is installed (installation instructions [here](https://python-poetry.org/docs/#installing-with-the-official-installer)).
3. From the root directory (the directory where pyproject.toml is located), run `poetry install`.
4. Run `poetry shell` to enter a shell where CLI commands can be run from.

## Airdrop Suilend Capsules

First, specify addresses in "addresses.json". This should be a JSON array of addresses like so:

```
[
    "0x...01",
    "0x...02",
    "0x...03",
    "0x...04"
]
```

Then, run `capsule airdrop <RARITY>`. For example, if you want to airdrop common capsules, run `capsule airdrop common`. The script will then fetch all capsules, filter out the ones with the correct rarity, and airdrop them to the addresses in `addresses.json`. The script will raise an exception if there are not enough capsules for all the addresses. The max limit per airdrop transaction is 500.