#!/usr/bin/env bash
#if [ -z "$1" ]
#	then
#		filename=memory-monitor.log
#else
#	filename=$1
#	pid=$2
#fi

filename="NA"
pid="NA"
while getopts ":f:p:" opt; do
  case ${opt} in
    f) filename="$OPTARG"
    ;;
    p) pid="$OPTARG"
    ;;
    \?) echo "Invalid option -$OPTARG" >&2
    ;;
  esac
done

if [[ ${filename} == "NA" ]]; then
   filename=memory-monitor.log
fi
if [[ ${pid} == "NA" ]]; then
   echo "-p parameter for pid is compulsory parameter. Not passed so EXITING"
   exit -1
fi

echo "Filename " ${filename}

while true
do
    date="$(date +"%Y-%m-%d %r")"
	memory=$(free -m | awk -v date="$(date +"%Y-%m-%d %r")" '/^Mem/ {print "Used RAM (%):"100*$3/$2"%", "Free RAM:"$7/1024"GB"}')
	max_heap=$(java -XX:+PrintFlagsFinal -version | grep MaxHeapSize | awk '{split($0,a," "); print a[4]/1024/1024}')
	used_heap=$(jstat -gc ${pid} | tail -1 | awk '{split($0,a," "); sum=(a[3]+a[4]+a[6]+a[8]+a[10]+a[12])/1024; print sum}')
	used_heap_per=$(echo "scale=4 ; ($used_heap/$max_heap)*100" | bc)
	echo ${date} ": PID: ${pid} Heap used (MB):" ${used_heap}, " Head used (%):"${used_heap_per} "%", " Max Heap (MB) " ${max_heap}, ${memory} >> ${filename}
#	jstat -gc ${pid} | tail -1 | awk -v date="$(date +"%Y-%m-%d %r")" '{split($0,a," "); sum=(a[3]+a[4]+a[6]+a[8]+a[10]+a[12])/1024; print date, "Heap used " sum "Mb" "Used %" $used_heap_per "%"}' >> ${filename}
	sleep 30s
done