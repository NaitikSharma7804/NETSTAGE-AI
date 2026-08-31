# Fix Recommendation Prompt Component

Generate safe, idempotent Cisco IOS configuration commands to remediate the diagnosed issue:
1. Specify appropriate configuration mode (e.g. `Router(config)#`, `Switch(config-if)#`).
2. Include interface or router process context.
3. Provide command verification step (e.g. `show ip interface brief`, `ping <destination>`).
4. Avoid disruptive commands unless strictly necessary.