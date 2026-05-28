package com.dreamco.bots;
import java.net.URI; import java.net.http.*; import com.fasterxml.jackson.databind.ObjectMapper; import java.util.*;
/** IT Service Desk Bot — DreamAutomation | pro | SaaS subscription */
public class ITServiceDeskBotBot {
    static final String PROMPT="You are IT Service Desk Bot, a specialized AI bot in the DreamCo Empire OS DreamAutomation division. Automated IT service desk with ticket routing, resolution, and knowledge base. You operate with precision, provide actionable intelligence, and generate measurable results. Be concise, data-driven, and focused on ROI.";
    static final String MODEL="gpt-4o-mini";
    final HttpClient http=HttpClient.newHttpClient(); final ObjectMapper m=new ObjectMapper();
    final String key=System.getenv("OPENAI_API_KEY");
    public String run(String msg) throws Exception {
        var body=m.writeValueAsString(Map.of("model",MODEL,"max_tokens",2000,"messages",List.of(Map.of("role","system","content",PROMPT),Map.of("role","user","content",msg))));
        var req=HttpRequest.newBuilder().uri(URI.create("https://api.openai.com/v1/chat/completions")).header("Authorization","Bearer "+key).header("Content-Type","application/json").POST(HttpRequest.BodyPublishers.ofString(body)).build();
        var res=http.send(req,HttpResponse.BodyHandlers.ofString());
        var json=(Map<?,?>)m.readValue(res.body(),Map.class);
        return (String)((Map<?,?>)((Map<?,?>)((List<?>)json.get("choices")).get(0)).get("message")).get("content");
    }
    public static void main(String[] a) throws Exception { System.out.println(new ITServiceDeskBotBot().run("What can you help me make money with today?")); }
}