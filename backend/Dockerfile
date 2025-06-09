# Образ Gradle
FROM gradle:jdk17 as builder

WORKDIR /app
COPY . .

RUN gradle build

# Образ с JRE для финального контейнера
FROM eclipse-temurin:17-jre

# Артефакт из builder-стадии
COPY --from=builder /app/build/libs/*.jar /app/application.jar

COPY config.json /app/config.json


# Точка входа
ENTRYPOINT ["java", "-jar", "/app/application.jar"]