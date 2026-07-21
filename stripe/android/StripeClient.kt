// Dreamcobots Stripe Integration — Android (Kotlin)
//
// Add to your app/build.gradle:
//   implementation 'com.stripe:stripe-android:20.+'
//
// Configure: call DreamcobotsStripe.configure() in Application.onCreate()
// Never embed your secret key in Android code — all server-side calls
// (PaymentIntent creation, etc.) must go through your backend.

package com.dreamcobots.stripe

import android.content.Context
import com.stripe.android.PaymentConfiguration
import com.stripe.android.paymentsheet.PaymentSheet
import com.stripe.android.paymentsheet.PaymentSheetResult

object DreamcobotsStripe {

    /**
     * Initialise Stripe with the publishable key.
     * Call this in Application.onCreate() or your main Activity.
     *
     * @param context Android application context.
     * @param publishableKey Your Stripe publishable key (pk_live_... or pk_test_...).
     *   Retrieve this from your backend rather than embedding it directly.
     */
    fun configure(context: Context, publishableKey: String) {
        PaymentConfiguration.init(context, publishableKey)
    }

    /**
     * Present the Stripe PaymentSheet to collect a payment.
     *
     * @param paymentSheet A PaymentSheet instance from your Activity/Fragment.
     * @param clientSecret The PaymentIntent or SetupIntent client_secret from your backend.
     */
    fun presentPaymentSheet(paymentSheet: PaymentSheet, clientSecret: String) {
        paymentSheet.presentWithPaymentIntent(clientSecret)
    }

    /**
     * Handle the PaymentSheet result.
     */
    fun handleResult(result: PaymentSheetResult, onSuccess: () -> Unit, onFailure: (String) -> Unit) {
        when (result) {
            is PaymentSheetResult.Completed -> onSuccess()
            is PaymentSheetResult.Failed -> onFailure(result.error.message ?: "Payment failed")
            is PaymentSheetResult.Canceled -> { /* User cancelled */ }
        }
    }
}
