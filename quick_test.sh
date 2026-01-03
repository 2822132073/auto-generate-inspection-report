#!/bin/bash
# 快速单次巡检数据提交示例

API_BASE="http://localhost:8000/api/v1"
PROJECT_CODE="${1:-PRJ001}"
HOSTNAME="${2:-test-$(date +%s)}"

echo "📤 提交巡检数据..."
echo "   项目: $PROJECT_CODE"
echo "   主机: $HOSTNAME"

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

curl -X POST "$API_BASE/inspections" \
  -H "Content-Type: application/json" \
  -d "{
    \"metadata\": {
      \"project_id\": \"$PROJECT_CODE\",
      \"hostname\": \"$HOSTNAME\",
      \"ip\": \"10.0.1.100\",
      \"os\": \"Ubuntu 22.04\",
      \"kernel\": \"5.15.0-89-generic\",
      \"arch\": \"x86_64\",
      \"timestamp\": \"$TIMESTAMP\"
    },
    \"data\": {
      \"env\": {},
      \"commands\": {
        \"free -h\": {
          \"command\": \"free -h\",
          \"return_code\": 0,
          \"output\": \"               total        used        free      shared  buff/cache   available\\nMem:            16Gi       8.2Gi       1.5Gi       256Mi       6.3Gi       7.2Gi\\nSwap:          2.0Gi       128Mi       1.9Gi\"
        },
        \"df -h\": {
          \"command\": \"df -h\",
          \"return_code\": 0,
          \"output\": \"Filesystem      Size  Used Avail Use% Mounted on\\n/dev/sda1       100G   45G   50G  48% /\"
        },
        \"uptime\": {
          \"command\": \"uptime\",
          \"return_code\": 0,
          \"output\": \"21:30:15 up 145 days, 8:24, 3 users, load average: 0.85, 0.92, 0.88\"
        },
        \"ps aux\": {
          \"command\": \"ps aux | head -5\",
          \"return_code\": 0,
          \"output\": \"USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND\\nroot         1  0.0  0.1 168568 11936 ?        Ss   Dec18   2:45 /sbin/init\"
        },
        \"netstat\": {
          \"command\": \"netstat -tunlp | head -5\",
          \"return_code\": 0,
          \"output\": \"Active Internet connections\\ntcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN      1024/sshd\"
        }
      }
    }
  }" | python3 -m json.tool

echo ""
echo "✅ 提交完成！"
