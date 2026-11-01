#!/bin/sh
# macOS visible-terminal helper. No key is supplied in arguments or logs.
cd -- "$(dirname -- "$0")" || exit 1
printf '选择 / Select provider: 1 DeepSeek, 2 Yuanbao: '
read -r choice
case "$choice" in
  1) provider=deepseek ;;
  2) provider=yuanbao ;;
  *) printf '请输入 1 或 2 / Enter 1 or 2\n'; exit 1 ;;
esac
python3 xcoze_search.py setup --provider "$provider" --verify
result=$?
printf '\n程序结束（退出码 %s）。按回车关闭。' "$result"
read -r ignored
exit "$result"
