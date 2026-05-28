package com.dreamco.bots;

import java.net.URI;
import java.net.http.*;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.*;

/**
 * Web Scraping Engine
 * Division: DreamFlow | Tier: pro
 * Enterprise-grade web scraping with JavaScript rendering and structured data extraction.
 * Revenue: Usage-based | Price: $199/mo
 */
public class WebScrapingEngineBot {
    private static final String SYSTEM_PROMPT = "You are Web Scraping Engine, a specialized AI bot in the DreamCo Empire OS DreamFlow division. Enterprise-grade web scraping with JavaScript rendering and structured data extraction. You operate with precision, provide actionable intelligence, and generate measurable results. Be concise, data-driven, and focused on ROI.";
    private static final String MODEL = "gpt-4o-mini";
    private static final String API_URL = "https://api.openai.com/v1/chat/completions";
    private static final Map<String, String> CONFIG = Map.of(
        "slug", "web-scraper",
        "division", "DreamFlow",
        "tier", "pro",
        "revenue", "Usage-based"
    );

    private final HttpClient http = HttpClient.newHttpClient();
    private final ObjectMapper mapper = new ObjectMapper();
    private final String apiKey = System.getenv("OPENAI_API_KEY");

    public String run(String userMessage) throws Exception {
        var body = mapper.writeValueAsString(Map.of(
            "model", MODEL, "max_tokens", 2000,
            "messages", List.of(
                Map.of("role", "system", "content", SYSTEM_PROMPT),
                Map.of("role", "user", "content", userMessage)
            )
        ));
        var req = HttpRequest.newBuilder().uri(URI.create(API_URL))
            .header("Authorization", "Bearer " + apiKey)
            .header("Content-Type", "application/json")
            .POST(HttpRequest.BodyPublishers.ofString(body)).build();
        var res = http.send(req, HttpResponse.BodyHandlers.ofString());
        var json = (Map<?, ?>) mapper.readValue(res.body(), Map.class);
        var choices = (List<?>) json.get("choices");
        var msg = (Map<?, ?>) ((Map<?, ?>) choices.get(0)).get("message");
        return (String) msg.get("content");
    }

    public String makeMonev(String task) throws Exception {
        return run("MONEY MODE: " + task + ". Maximize revenue using all capabilities.");
    }

    public static void main(String[] args) throws Exception {
        var bot = new WebScrapingEngineBot();
        System.out.println("Running Web Scraping Engine...");
        System.out.println(bot.run("What can you help me make money with today?"));
    }
}
