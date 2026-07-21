package com.dreamco;

/**
 * DreamCo Java Base Bot — interface contract.
 *
 * <p>All Java bots in the DreamCo ecosystem must implement this interface so that they can be
 * discovered, tested, and orchestrated by the master controller.
 */
public interface BaseBot {

  /**
   * Execute the bot's core logic and emit events on {@code bus}.
   *
   * @param bus the shared {@link EventBus} used for inter-bot communication
   */
  void run(EventBus bus);

  /**
   * Return the human-readable name of this bot.
   *
   * @return bot name
   */
  String getName();
}
