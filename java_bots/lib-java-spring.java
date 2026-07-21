package com.dreamco.bots;
import java.net.URI; import java.net.http.*; import com.fasterxml.jackson.databind.ObjectMapper; import java.util.*;
/** Java Spring Boot Bot — DreamCodeLab | pro | SaaS subscription */
public class JavaSpringBootBotBot {
    static final String PROMPT="You are Java Spring Boot Bot, a DreamCo Empire OS DreamCodeLab AI coding expert specializing in Spring Boot, Spring Security, JPA, Hibernate, Gradle, Maven. Expert in Spring Boot 3, Spring Security, JPA, and enterprise Java application architecture. You write production-quality code, explain concepts clearly, debug with precision, and build complete solutions. You can replicate any feature of any ";
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
    public static void main(String[] a) throws Exception { System.out.println(new JavaSpringBootBotBot().run("What can you help me make money with today?")); }
}