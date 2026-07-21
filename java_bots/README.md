# Java Bots

This directory contains bots written in Java.

## Linting & Formatting

Java bots in this directory are checked with:

- **Checkstyle** — linting (Google Java Style Guide)
- **google-java-format** — code formatting

### Running checks locally

```bash
# Checkstyle (download JAR first)
java -jar checkstyle-10.21.0-all.jar -c checkstyle.xml java_bots/

# google-java-format (download JAR first)
java -jar google-java-format-1.22.0-all-deps.jar --check java_bots/**/*.java

# Auto-format
java -jar google-java-format-1.22.0-all-deps.jar --replace java_bots/**/*.java
```

## Adding a New Java Bot

1. Create a subdirectory: `java_bots/<BotName>/`
2. Add your Java source files (`.java`)
3. Ensure all files pass Checkstyle and google-java-format checks before submitting a PR
4. Follow the [Google Java Style Guide](https://google.github.io/styleguide/javaguide.html)
