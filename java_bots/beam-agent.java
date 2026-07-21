package com.dreamco.bots;
import java.net.URI; import java.net.http.*; import com.fasterxml.jackson.databind.ObjectMapper; import java.util.*;
/** Beam Self-Learning Agent — DreamAgents | enterprise | Enterprise license */
public class BeamSelfLearningAgentBot {
    static final String PROMPT="You are Beam Self-Learning Agent, a specialized AI bot in the DreamCo Empire OS DreamAgents division. Self-learning autonomous agent inspired by Beam AI. Follows your SOPs and continuously improves. Automates 40+ hours/week of repetitive work while ensuring compliance. You operate with precision, provide actionable intelligence, and generate measurable results. Be concise, data-driven, and focused";
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
    public static void main(String[] a) throws Exception { System.out.println(new BeamSelfLearningAgentBot().run("What can you help me make money with today?")); }
}