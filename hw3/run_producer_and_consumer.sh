# скрипт запуска продьюсера и консьюмера

# stdout из producer не выводится, также добавлены команды,
# чтобы по ctrl-c завершался и consumer и producer
( python3 producer.py > /dev/null ; kill -TERM -$$ ) &
python3 consumer.py ; kill -TERM -$$