S=/tmp/claude-0/-home-user-tirador-de-ia-das-fotos/3c9b5811-fca5-51b3-ac00-75dbd87eaeac/scratchpad
for pid in $(ps -eo pid,args | awk '/^ *[0-9]+ python3 -I .*crawl_bu\.py/ {print $1}'); do kill $pid; done
sleep 2
cd /
export CRAWL_MIN_INTERVAL=0.1
C="python3 -I $S/scripts/crawl_bu.py"
i=0
run() { i=$((i+1)); nohup $C "$@" > $S/urnas/crawl_bu_$i.out 2>&1 & }
CRAWL_SHARD=0/2 run ba
CRAWL_SHARD=1/2 run ba
run pe
run ce
run go
run ma
run am es
run pb rn
run mt al
run pi df
run ms se ro to ac ap rr zz
run pa sc pr sp mg rj rs
sleep 1
ps -eo pid,args | awk '/^ *[0-9]+ python3 -I .*crawl_bu\.py/' | wc -l
