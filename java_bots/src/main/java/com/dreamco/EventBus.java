package com.dreamco;

/**
 * DreamCo Java Event Bus — interface contract.
 *
 * <p>All concrete Java event bus implementations (in-process, Redis-backed, HTTP-based, etc.) must
 * implement this interface so that bots remain decoupled from the underlying transport.
 */
public interface EventBus {

  /**
   * Publish {@code eventType} with the given JSON {@code data} payload to all registered
   * subscribers.
   *
   * @param eventType the event category (e.g. {@code "deal_found"})
   * @param data JSON-serialised event payload
   */
  void publish(String eventType, String data);

  /**
   * Subscribe {@code handler} to receive events of {@code eventType}.
   *
   * @param eventType the event category to listen for
   * @param handler callback invoked with the raw JSON payload string
   */
  void subscribe(String eventType, java.util.function.Consumer<String> handler);
}
