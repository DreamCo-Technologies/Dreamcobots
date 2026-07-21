package com.dreamco.bots;

import com.dreamco.BaseBot;
import com.dreamco.EventBus;

/**
 * DreamCo Java — Real Estate Bot.
 *
 * <p>Discovers real-estate deals and publishes a {@code deal_found} event on the shared {@link
 * EventBus} so downstream bots (analyser, outreach, payment) can act on it.
 */
public class RealEstateBot implements BaseBot {

  private final String name;

  /** Create a new {@code RealEstateBot} with the given display name. */
  public RealEstateBot(String name) {
    this.name = name;
  }

  @Override
  public String getName() {
    return name;
  }

  /**
   * Find a real-estate deal and publish it on {@code bus}.
   *
   * @param bus the shared event bus
   */
  @Override
  public void run(EventBus bus) {
    System.out.println("🏠 Java Real Estate Bot running: " + name);

    String dealJson =
        "{ \"address\": \"456 Oak Ave\", \"profit\": 30000, \"source\": \"java_real_estate\" }";

    bus.publish("deal_found", dealJson);
    System.out.println("🏠 Published deal_found → " + dealJson);
  }
}
