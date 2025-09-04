printf '{"src_ip":"10.10.2.8","indicator":"phish"}\n' > alert.json

python3 - <<'PY'
import json; j=json.load(open('alert.json'))
sev='high' if j['indicator']=='phish' else 'low'
open('decision.txt','w').write(sev); print(sev)
PY



sudo iptables-save > ipt.bak
sudo iptables -I INPUT -s 10.10.2.8 -j DROP
sudo iptables -I OUTPUT -d 10.10.2.8 -j DROP


printf "src=%s,decision=%s\n" "$(jq -r .src_ip alert.json)" "$(cat decision.txt)" > run.log


printf "time=%s,src=%s,decision=%s\n" "$(date +%F_%T)" "$(jq -r .src_ip alert.json)" "$(cat decision.txt)" | tee -a run.log
