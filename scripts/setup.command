#!/bin/sh
# macOS visible-terminal helper. No key is supplied in arguments or logs.
cd -- "$(dirname -- "$0")" || exit 1
printf '选择 / Select: 1 DeepSeek, 2 Yuanbao, 3 Tavily, 4 Exa, 5 Brave, 6 Bocha: '
read -r choice
case "$choice" in
  1) provider=deepseek ;;
  2) provider=yuanbao ;;
  3) provider=tavily ;;
  4) provider=exa ;;
  5) provider=brave ;;
  6) provider=bocha ;;
  *) printf '请输入 1 到 6 / Enter 1 to 6\n'; exit 1 ;;
esac
python3 xcoze_search.py setup --provider "$provider" --verify
result=$?
printf '\n程序结束（退出码 %s）。按回车关闭。' "$result"
read -r ignored
exit "$result"
