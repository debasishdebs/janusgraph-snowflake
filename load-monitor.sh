#!/usr/bin/env bash
if [ -z "$1" ]
	then
		filename=load-monitor.log
else
	filename=$1
fi

echo "Filename " ${filename}

while true
do
	uptime | awk -v date="$(date +"%Y-%m-%d %r")" '{print date, $10, $11, $12}' >> ${filename}
	sleep 30s
done
