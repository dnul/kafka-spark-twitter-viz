spark-submit --class "Sample" --packages org.apache.spark:spark-streaming-kafka-0-8_2.11:2.1.0  --name DirectKafkaWordCount --master "local[2]" spark-consumer-kafka.py
