plugins {
    kotlin("jvm") version "2.1.20"
    id("application")
}

group = "com.adisalagic"
version = "1.0-SNAPSHOT"
application.mainClass = "com.adisalagic.Main"

repositories {
    mavenCentral()
    maven("https://jitpack.io")
}

dependencies {
    // https://mvnrepository.com/artifact/com.squareup.okhttp/okhttp
    implementation("com.squareup.okhttp3:okhttp:4.12.0")
    // https://mvnrepository.com/artifact/com.google.code.gson/gson
    implementation("com.google.code.gson:gson:2.13.1")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.10.2")
    implementation("io.github.kotlin-telegram-bot.kotlin-telegram-bot:telegram:6.3.0")
    testImplementation(kotlin("test"))
}

tasks.jar {
    manifest.attributes["Main-Class"] = application.mainClass
    val dependencies = configurations
        .runtimeClasspath
        .get()
        .map(::zipTree) // OR .map { zipTree(it) }
    from(dependencies)
    duplicatesStrategy = DuplicatesStrategy.EXCLUDE
}

tasks.test {
    useJUnitPlatform()
}
kotlin {
    jvmToolchain(17)
}