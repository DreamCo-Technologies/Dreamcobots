// DreamCobots — Stripe iOS (Swift) Integration
//
// Provides Stripe Checkout and PaymentSheet integration for iOS apps.
//
// Setup:
//   1. Add pod 'StripePaymentSheet' to your Podfile and run `pod install`
//   2. Set your Publishable Key in AppDelegate or SwiftUI App entry point
//   3. Implement a backend endpoint that creates a PaymentIntent and
//      returns { clientSecret: "..." }
//
// This file shows the SwiftUI-based PaymentSheet integration.

import SwiftUI
import StripePaymentSheet

// MARK: - Payment Sheet View Model

@MainActor
final class PaymentViewModel: ObservableObject {

    @Published var paymentSheet: PaymentSheet?
    @Published var paymentResult: PaymentSheetResult?
    @Published var isLoading = false

    private let backendURL: URL

    init(backendURL: URL = URL(string: "https://your-backend.example.com")!) {
        self.backendURL = backendURL
    }

    /// Fetch a PaymentIntent client secret from your backend, then prepare the PaymentSheet.
    func preparePaymentSheet(amountInCents: Int, currency: String) async {
        isLoading = true
        defer { isLoading = false }

        guard let url = URL(string: "\(backendURL)/create-payment-intent") else { return }

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try? JSONSerialization.data(withJSONObject: [
            "amount": amountInCents,
            "currency": currency
        ])

        guard let (data, _) = try? await URLSession.shared.data(for: request),
              let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
              let clientSecret = json["clientSecret"] as? String,
              let publishableKey = json["publishableKey"] as? String else {
            return
        }

        STPAPIClient.shared.publishableKey = publishableKey

        var configuration = PaymentSheet.Configuration()
        configuration.merchantDisplayName = "DreamCobots"
        configuration.allowsDelayedPaymentMethods = true

        paymentSheet = PaymentSheet(paymentIntentClientSecret: clientSecret,
                                   configuration: configuration)
    }

    /// Handle the result from the presented PaymentSheet.
    func handlePaymentResult(_ result: PaymentSheetResult) {
        paymentResult = result
        switch result {
        case .completed:
            print("Payment succeeded")
        case .canceled:
            print("Payment canceled by user")
        case .failed(let error):
            print("Payment failed: \(error.localizedDescription)")
        }
    }
}

// MARK: - Payment View

struct PaymentView: View {

    @StateObject private var viewModel = PaymentViewModel()

    var body: some View {
        VStack(spacing: 20) {
            Text("DreamCobots Payment")
                .font(.title2)
                .bold()

            if viewModel.isLoading {
                ProgressView("Preparing payment…")
            } else if let sheet = viewModel.paymentSheet {
                PaymentSheet.PaymentButton(
                    paymentSheet: sheet,
                    onCompletion: viewModel.handlePaymentResult
                ) {
                    Label("Pay Now", systemImage: "creditcard")
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.accentColor)
                        .foregroundColor(.white)
                        .cornerRadius(10)
                }
            } else {
                Button("Prepare Payment") {
                    Task { await viewModel.preparePaymentSheet(amountInCents: 2500, currency: "usd") }
                }
                .buttonStyle(.borderedProminent)
            }

            if let result = viewModel.paymentResult {
                switch result {
                case .completed:
                    Label("Payment successful!", systemImage: "checkmark.circle.fill")
                        .foregroundColor(.green)
                case .canceled:
                    Text("Payment canceled.")
                        .foregroundColor(.secondary)
                case .failed(let error):
                    Label("Payment failed: \(error.localizedDescription)",
                          systemImage: "xmark.circle.fill")
                        .foregroundColor(.red)
                }
            }
        }
        .padding()
    }
}

// MARK: - App Entry Point (example)

@main
struct DreamCobotsApp: App {
    var body: some Scene {
        WindowGroup {
            PaymentView()
        }
    }
}
