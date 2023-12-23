from pyflink.common.serialization import SimpleStringSchema
from pyflink.common.typeinfo import Types, RowTypeInfo
from pyflink.common.watermark_strategy import TimestampAssigner
from pyflink.common.watermark_strategy import WatermarkStrategy
from pyflink.datastream import StreamExecutionEnvironment, TimeCharacteristic
from pyflink.datastream.connectors import DeliveryGuarantee
from pyflink.datastream.connectors.kafka import KafkaSource, \
    KafkaOffsetsInitializer, KafkaSink, KafkaRecordSerializationSchema
from pyflink.datastream.formats.json import JsonRowDeserializationSchema
from pyflink.datastream.functions import AggregateFunction, ProcessWindowFunction
from pyflink.datastream.window import TumblingEventTimeWindows, SlidingProcessingTimeWindows, \
    EventTimeSessionWindows, Time


class MaxAggFunction(AggregateFunction):
    def __init__(self):
        pass

    def create_accumulator(self):
        return float("-inf")

    def add(self, value, accumulator):
        return max(accumulator, value["temperature"])

    def get_result(self, accumulator):
        return accumulator

    def merge(self, a, b):
        return max(a, b)


class GetResultProcessWindowFunction(ProcessWindowFunction):
    def process(self, key, context, iterable):
        yield str({"device_id": key, "max_temperature": next(iter(iterable))})


class ExecutionTimeTimestampAssigner(TimestampAssigner):

    def extract_timestamp(self, value, record_timestamp):
        return value['execution_time']


def python_data_stream_example():
    env = StreamExecutionEnvironment.get_execution_environment()
    # Set the parallelism to be one to make sure that all data including fired timer and normal data
    # are processed by the same worker and the collected result would be in order which is good for
    # assertion.
    env.set_parallelism(1)
    env.set_stream_time_characteristic(TimeCharacteristic.EventTime)

    type_info: RowTypeInfo = Types.ROW_NAMED(['device_id', 'temperature', 'execution_time'],
                                             [Types.LONG(), Types.DOUBLE(), Types.INT()])

    json_row_schema = JsonRowDeserializationSchema.builder().type_info(type_info).build()

    source = KafkaSource.builder() \
        .set_bootstrap_servers('kafka:9092') \
        .set_topics('itmo2023') \
        .set_group_id('pyflink-e2e-source') \
        .set_starting_offsets(KafkaOffsetsInitializer.earliest()) \
        .set_value_only_deserializer(json_row_schema) \
        .build()

    sink = KafkaSink.builder() \
        .set_bootstrap_servers('kafka:9092') \
        .set_record_serializer(KafkaRecordSerializationSchema.builder()
                               .set_topic('itmo2023_processed')
                               .set_value_serialization_schema(SimpleStringSchema())
                               .build()
                               ) \
        .set_delivery_guarantee(DeliveryGuarantee.AT_LEAST_ONCE) \
        .build()

    ds = env.from_source(source, WatermarkStrategy.for_monotonous_timestamps().with_timestamp_assigner(
        ExecutionTimeTimestampAssigner()), "Kafka Source")
    ds.key_by(lambda x: x["device_id"]) \
        .window(
        # TumblingEventTimeWindows.of(Time.seconds(5)),
        # SlidingProcessingTimeWindows.of(Time.seconds(10), Time.seconds(5)),
        EventTimeSessionWindows.with_gap(Time.seconds(2)),
    ) \
        .aggregate(MaxAggFunction(), window_function=GetResultProcessWindowFunction(), output_type=Types.STRING()) \
        .sink_to(sink)

    env.execute_async("Devices preprocessing")


if __name__ == '__main__':
    python_data_stream_example()
