import Foundation

/// Local Apple-platform transport for Buddy during Xcode/macOS/iOS development.
/// Production apps should call DreamCo's server-side Buddy gateway instead of
/// embedding a provider credential in the application bundle.
public final class BuddyOpenRouterService {
    public struct Message: Codable {
        public let role: String
        public let content: String
        public init(role: String, content: String) {
            self.role = role
            self.content = content
        }
    }

    public struct ProviderOptions: Codable {
        public var sort: String?
        public var allowFallbacks: Bool?
        public var dataCollection: String?
        public var zdr: Bool?
    }

    private struct ChatRequest: Codable {
        let model: String
        let messages: [Message]
        let temperature: Double?
        let provider: ProviderOptions?
    }

    private struct ChatResponse: Codable {
        struct Choice: Codable {
            struct ChoiceMessage: Codable {
                let content: String?
            }
            let message: ChoiceMessage
        }
        let choices: [Choice]
        let model: String?
        let id: String?
    }

    public enum ServiceError: LocalizedError {
        case missingAPIKey
        case invalidResponse
        case http(Int, String)
        case decoding(Error)

        public var errorDescription: String? {
            switch self {
            case .missingAPIKey:
                return "OPENROUTER_API_KEY is not configured."
            case .invalidResponse:
                return "Buddy received an invalid model response."
            case let .http(code, body):
                return "Buddy provider HTTP \(code): \(body)"
            case let .decoding(error):
                return "Buddy response decoding failed: \(error.localizedDescription)"
            }
        }
    }

    private let session: URLSession
    private let baseURL: URL
    private let apiKeyProvider: () -> String?

    public init(
        session: URLSession = .shared,
        baseURL: URL = URL(string: "https://openrouter.ai/api/v1")!,
        apiKeyProvider: @escaping () -> String? = {
            ProcessInfo.processInfo.environment["OPENROUTER_API_KEY"]
        }
    ) {
        self.session = session
        self.baseURL = baseURL
        self.apiKeyProvider = apiKeyProvider
    }

    public func chat(
        prompt: String,
        model: String = "openai/gpt-5.5",
        providerSort: String = "price"
    ) async throws -> String {
        guard let key = apiKeyProvider(), !key.isEmpty else {
            throw ServiceError.missingAPIKey
        }

        var request = URLRequest(url: baseURL.appendingPathComponent("chat/completions"))
        request.httpMethod = "POST"
        request.setValue("Bearer \(key)", forHTTPHeaderField: "Authorization")
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("DreamCo Buddy", forHTTPHeaderField: "X-OpenRouter-Title")
        request.httpBody = try JSONEncoder().encode(
            ChatRequest(
                model: model,
                messages: [Message(role: "user", content: prompt)],
                temperature: 0.2,
                provider: ProviderOptions(
                    sort: providerSort,
                    allowFallbacks: true,
                    dataCollection: "deny",
                    zdr: nil
                )
            )
        )

        let (data, response) = try await session.data(for: request)
        guard let http = response as? HTTPURLResponse else {
            throw ServiceError.invalidResponse
        }
        guard (200..<300).contains(http.statusCode) else {
            throw ServiceError.http(
                http.statusCode,
                String(data: data, encoding: .utf8) ?? "Unknown provider error"
            )
        }

        do {
            let decoded = try JSONDecoder().decode(ChatResponse.self, from: data)
            guard let content = decoded.choices.first?.message.content else {
                throw ServiceError.invalidResponse
            }
            return content
        } catch let error as ServiceError {
            throw error
        } catch {
            throw ServiceError.decoding(error)
        }
    }
}
