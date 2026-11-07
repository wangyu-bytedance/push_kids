# Final native automation recovery — blocked

Executed after the 320 native run stopped responding; no upload or production API was called:

```text
/Applications/wechatwebdevtools.app/Contents/MacOS/cli auto --project /private/tmp/push-kids-themes-native-20261106 --auto-port 9631 --trust-project --disable-gpu
exit_code=246
[error] IDE service port disabled. To use CLI Call, please enter y to confirm enabling CLI capability, or manually open IDE -> Settings -> Security Settings, and set Service Port On.
[error] 工具的服务端口已关闭。要使用命令行调用工具，请手动打开工具 -> 设置 -> 安全设置，将服务端口开启。
```

The automation service could not be reopened. Security settings were left unchanged. Existing RPC/screenshot failures remain failures; missing and stale-source groups are NOT_RUN for the final diff. See `native-summary.json` for the source-bound count. This is a tooling blocker, not evidence that production rendering failed or passed.
