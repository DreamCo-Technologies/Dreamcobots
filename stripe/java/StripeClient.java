package com.dreamcobots.stripe;

import com.stripe.Stripe;
import com.stripe.exception.StripeException;
import com.stripe.model.PaymentLink;
import com.stripe.model.Price;
import com.stripe.model.checkout.Session;
import com.stripe.param.PaymentLinkCreateParams;
import com.stripe.param.PriceCreateParams;
import com.stripe.param.checkout.SessionCreateParams;

import java.util.Collections;
import java.util.HashMap;
import java.util.Map;

/**
 * Dreamcobots Stripe Integration — Java
 *
 * Configure via environment variables (see ../../.env.example):
 *   STRIPE_SECRET_KEY      — sk_live_... or sk_test_...
 *   STRIPE_PUBLISHABLE_KEY — pk_live_... or pk_test_...
 *
 * Build: mvn package
 * Run:   java -cp target/stripe-integration-1.0.0.jar com.dreamcobots.stripe.StripeClient
 */
public class StripeClient {

    static {
        String key = System.getenv("STRIPE_SECRET_KEY");
        if (key != null && !key.isEmpty()) {
            Stripe.apiKey = key;
        }
    }

    /**
     * Create a Stripe Checkout session for a one-time payment.
     */
    public static Session createCheckoutSession(
            long amountCents,
            String currency,
            String customerEmail,
            String successUrl,
            String cancelUrl
    ) throws StripeException {
        SessionCreateParams params = SessionCreateParams.builder()
                .addPaymentMethodType(SessionCreateParams.PaymentMethodType.CARD)
                .addLineItem(
                        SessionCreateParams.LineItem.builder()
                                .setPriceData(
                                        SessionCreateParams.LineItem.PriceData.builder()
                                                .setCurrency(currency.toLowerCase())
                                                .setProductData(
                                                        SessionCreateParams.LineItem.PriceData.ProductData.builder()
                                                                .setName("Dreamcobots Service")
                                                                .build()
                                                )
                                                .setUnitAmount(amountCents)
                                                .build()
                                )
                                .setQuantity(1L)
                                .build()
                )
                .setMode(SessionCreateParams.Mode.PAYMENT)
                .setCustomerEmail(customerEmail)
                .setSuccessUrl(successUrl)
                .setCancelUrl(cancelUrl)
                .build();
        return Session.create(params);
    }

    /**
     * Create a shareable Stripe Payment Link.
     */
    public static PaymentLink createPaymentLink(
            long amountCents,
            String currency,
            String productName
    ) throws StripeException {
        PriceCreateParams priceParams = PriceCreateParams.builder()
                .setUnitAmount(amountCents)
                .setCurrency(currency.toLowerCase())
                .setProductData(
                        PriceCreateParams.ProductData.builder()
                                .setName(productName)
                                .build()
                )
                .build();
        Price price = Price.create(priceParams);

        PaymentLinkCreateParams linkParams = PaymentLinkCreateParams.builder()
                .addLineItem(
                        PaymentLinkCreateParams.LineItem.builder()
                                .setPrice(price.getId())
                                .setQuantity(1L)
                                .build()
                )
                .build();
        return PaymentLink.create(linkParams);
    }

    public static void main(String[] args) {
        String mode = (System.getenv("STRIPE_SECRET_KEY") != null &&
                       !System.getenv("STRIPE_SECRET_KEY").isEmpty()) ? "live" : "simulation";
        System.out.println("Dreamcobots Stripe Java client initialised in " + mode + " mode.");
    }
}
