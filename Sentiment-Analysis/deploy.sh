pkill -f -9 sentiment_analyzer.py
source /home/stocktool/envs/ci.env
source /home/stocktool/env/bin/activate
cd /home/stocktool/stock-market-tool
git pull
(nohup python /home/stocktool/stock-market-tool/sentiment_analyzer.py &) && sleep 1