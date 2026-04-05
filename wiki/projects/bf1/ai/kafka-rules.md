---
name: kafka-implementation-template
description: Template chuẩn để implement Kafka message (Producer, Consumer, Config, Event) vào dự án OF1. Cung cấp boilerplate code và TODOs để dev chỉ cần điền business logic, giảm thiểu thời gian setup.
---

# Template Triển Khai Kafka Message (OF1)
Skill này cung cấp các template code chuẩn để implement Kafka theo convention của dự án OF1.
Các template định nghĩa sẵn cách wrap message bằng `datatp.data.kafka.KafkaMessage`, serialize bằng `DataSerializer`, và cách truyền nhận `ClientContext` qua Kafka.

## 1. Event Model (`YourBusinessEvent.java`)
```java
package [your.package.event];

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Event model chứa data cần truyền qua Kafka.
 * TODO: Định nghĩa các field theo business logic
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class YourBusinessEvent {
    // TODO: Add properties thiết yếu cho event
    private String entityId;
    private String action;
    private Object payload;
}
```

## 2. Kafka Configuration (`YourQueueConfig.java`)
```java
package [your.package.event];

import datatp.data.kafka.KafkaConfig;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;

/**
 * Cấu hình khởi tạo các Bean cho Producer và Consumer.
 * TODO: Đổi tên class và bean name theo domain (Ví dụ: OrderQueueConfig).
 */
@Configuration
@Import(value = {KafkaConfig.class})
public class YourQueueConfig {

    @Bean("YourEventProducer")
    YourEventProducer createYourEventProducer() {
        return new YourEventProducer();
    }

    @Bean("YourEventConsumer")
    YourEventConsumer createYourEventConsumer() {
        return new YourEventConsumer();
    }
}
```

## 3. Producer (`YourEventProducer.java`)
```java
package [your.package.event];

import datatp.data.kafka.KafkaMessage;
import jakarta.annotation.PostConstruct;
import lombok.extern.slf4j.Slf4j;
import net.datatp.security.client.ClientContext;
import net.datatp.util.dataformat.DataSerializer;
import net.datatp.util.error.ErrorType;
import net.datatp.util.error.RuntimeError;
import net.datatp.util.text.StringUtil;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.kafka.core.KafkaTemplate;

/**
 * TODO: Đổi tên class, đảm bảo trùng với Bean name trong QueueConfig.
 */
@Slf4j
public class YourEventProducer {

    @Autowired
    private KafkaTemplate<String, String> kafkaTemplate;

    // TODO: Thay prefix 'datatp.msa.your-domain' bằng config thật trong thiết lập của dự án
    @Value("${datatp.msa.your-domain.queue.event-producer-enable:false}")
    private boolean enable;

    @Value("${datatp.msa.your-domain.queue.topic.events}")
    private String topicEvents;

    @PostConstruct
    public void onInit() {
        log.info("YourEventProducer config: enable={}, events={}", enable, topicEvents);
        if (enable && StringUtil.isEmpty(topicEvents)) {
            throw RuntimeError.IllegalArgument("Topic events is empty.");
        }
    }

    public void send(ClientContext ctx, YourBusinessEvent event) {
        if (!enable) {
            log.info("Event producer is disabled, skipping send");
            return;
        }
        try {
            // Wrapper convention của OF1
            KafkaMessage message = new KafkaMessage(ctx, event);
            String jsonMessage = DataSerializer.JSON.toString(message);

            kafkaTemplate.send(topicEvents, jsonMessage).whenComplete((result, ex) -> {
                if (ex != null) {
                    log.error("Failed to send event to topic {}: {}", topicEvents, ex.getMessage(), ex);
                }
            });
        } catch (Exception e) {
            log.error("Error while sending event: {}", e.getMessage(), e);
            throw new RuntimeError(ErrorType.IllegalState, "Failed to send event", e);
        }
    }
}
```

## 4. Consumer (`YourEventConsumer.java`)
```java
package [your.package.event];

import datatp.data.kafka.KafkaMessage;
import jakarta.annotation.PostConstruct;
import lombok.extern.slf4j.Slf4j;
import net.datatp.security.client.ClientContext;
import net.datatp.util.dataformat.DataSerializer;
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.kafka.annotation.KafkaListener;

/**
 * TODO: Đổi tên class và thay thế các logic comment bằng business logic thật
 */
@Slf4j
public class YourEventConsumer {

    @Value("${datatp.msa.your-domain.queue.topic.events}")
    private String topicEvents;

    // TODO: Add các Service dependency ở đây (e.g., @Autowired private YourLogic logic;)

    @PostConstruct
    public void onInit() {
        log.info("YourEventConsumer initialized for topic: {}", topicEvents);
    }

    // TODO: Thay các giá trị id, groupId và topic config cho đúng chuẩn dự án
    @KafkaListener(
        id = "msa.YourEventConsumer",
        topics = "${datatp.msa.your-domain.queue.topic.events}",
        groupId = "your-domain-consumer-group",
        autoStartup = "${datatp.msa.your-domain.queue.event-consumer-enable:false}",
        concurrency = "1") // TODO: Tăng giảm concurrency tùy khối lượng tải
    public void onEvent(ConsumerRecord<String, String> consumerRecord) {
        try {
            String json = consumerRecord.value();
            KafkaMessage message = DataSerializer.JSON.fromString(json, KafkaMessage.class);

            // Parse payload về Business Event Object
            YourBusinessEvent event = message.getDataAs(YourBusinessEvent.class);
            ClientContext ctx = message.getClientContext();

            // TODO: Implement Business logic ở đây
            /*
            Ví dụ:
            if ("CREATE".equals(event.getAction())) {
                yourLogic.handleCreate(ctx, event.getEntityId());
            }
            */

            log.info("Successfully processed event for entityId: {}", event.getEntityId());
        } catch (Exception e) {
            log.error("Error processing event: topic={}, partition={}, offset={}, error={}",
                    consumerRecord.topic(), consumerRecord.partition(), consumerRecord.offset(), e.getMessage(), e);
            // TODO: Thêm catch / logic xử lý Dead Letter Queue (nếu có yêu cầu từ system)
        }
    }
}
```

## 5. Cấu hình Properties (`application-env.yaml`)
```yaml
# TODO: Khai báo structure topic này tại file application-env.yaml
datatp:
  msa:
    your-domain:
      queue:
        event-producer-enable: true
        event-consumer-enable: true
        topic:
          events: "your_domain_events_topic" # Thêm config topic phục vụ retry, acks nếu có
```