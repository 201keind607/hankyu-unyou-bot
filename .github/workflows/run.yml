name: Hankyu Bot

on:
  schedule:
    - cron: "6 15 * * *"

  workflow_dispatch:

jobs:
  run:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Python setup
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install
        run: |
          pip install requests

      - name: Run bot
        env:
          DISCORD_WEBHOOK: ${{ secrets.DISCORD_WEBHOOK }}
        run: |
          python bot.py
