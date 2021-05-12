import Mqtt as mqtt

mqtt.set_db_info("host", "user", "pw", "db name")
mqtt.device_id = 7
mqtt.run_loop_subscribe()