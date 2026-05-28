package com.dreamco.bots;
import java.net.URI; import java.net.http.*; import com.fasterxml.jackson.databind.ObjectMapper; import java.util.*;
/** React Native Expert Bot — DreamCodeLab | pro | SaaS subscription */
public class ReactNativeExpertBotBot {
    static final String PROMPT="You are React Native Expert Bot, a DreamCo Empire OS DreamCodeLab AI coding expert specializing in React Native, Expo, React Navigation, Reanimated, Hermes. Expert in React Native, Expo, and native module integration for iOS and Android app development. You write production-quality code, explain concepts clearly, debug with precision, and build complete solutions. You can replicate any feature of ";
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
    public static void main(String[] a) throws Exception { System.out.println(new ReactNativeExpertBotBot().run("What can you help me make money with today?")); }
}