// Dreamcobots Stripe Integration — iOS (Swift)
//
// Install: pod install (after adding the Podfile to your Xcode project)
// Configure: set your publishable key at app launch
//
// Usage: call DreamcobotsStripe.configure() in AppDelegate or @main

import Foundation
import Stripe
import StripePaymentSheet

public enum DreamcobotsStripe {
    /// Call this once at app launch with your Stripe publishable key.
    /// Read the key from your backend or a configuration file — never
    /// hard-code secret keys in client-side code.
    public static func configure(publishableKey: String) {
        STPAPIClient.shared.publishableKey = publishableKey
    }

    /// Present a PaymentSheet to collect a payment from the user.
    ///
    /// - Parameters:
    ///   - clientSecret: PaymentIntent client_secret from your backend.
    ///   - presentingViewController: The view controller to present from.
    ///   - completion: Called with the PaymentSheetResult.
    public static func presentPaymentSheet(
        clientSecret: String,
        from presentingViewController: UIViewController,
        completion: @escaping (PaymentSheetResult) -> Void
    ) {
        var configuration = PaymentSheet.Configuration()
        configuration.merchantDisplayName = "Dreamcobots"

        let paymentSheet = PaymentSheet(
            paymentIntentClientSecret: clientSecret,
            configuration: configuration
        )
        paymentSheet.present(from: presentingViewController, completion: completion)
    }
}
