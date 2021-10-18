pkill -f -9 /home/stocktool/twitter-api-listener/__main__.py
source /home/stocktool/envs/ci.env
source /home/stocktool/env/bin/activate
cd /home/stocktool/twitter-api-listener
git pull
(nohup python /home/stocktool/twitter-api-listener/__main__.py &) && sleep 1