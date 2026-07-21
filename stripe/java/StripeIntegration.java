// DreamCobots — Stripe Java Integration
//
// Provides Payment Intent creation, subscription management, and webhook handling.
//
// Setup:
//   Add stripe-java to pom.xml (see pom.xml in this directory)
//   export STRIPE_SECRET_KEY=sk_...
//   mvn spring-boot:run
package com.dreamcobots.stripe;

import com.stripe.Stripe;
import com.stripe.exception.SignatureVerificationException;
import com.stripe.exception.StripeException;
import com.stripe.model.*;
import com.stripe.model.checkout.Session;
import com.stripe.net.Webhook;
import com.stripe.param.*;
import com.stripe.param.checkout.SessionCreateParams;

import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;

/**
 * DreamCobots Stripe helper — wraps common Stripe operations used by all bots.
 */
public class StripeIntegration {

    static {
        Stripe.apiKey = System.getenv("STRIPE_SECRET_KEY");
    }

    private static final String WEBHOOK_SECRET =
            System.getenv().getOrDefault("STRIPE_WEBHOOK_SECRET", "");

    // -----------------------------------------------------------------------
    // Payment Intent
    // -----------------------------------------------------------------------

    /**
     * Create a Stripe PaymentIntent for a one-time charge.
     *
     * @param amountInCents Amount in the smallest currency unit (e.g. cents).
     * @param currency      ISO 4217 currency code (e.g. {@code "usd"}).
     * @return Stripe {@link PaymentIntent}.
     * @throws StripeException on API error.
     */
    public PaymentIntent createPaymentIntent(long amountInCents, String currency)
            throws StripeException {
        PaymentIntentCreateParams params = PaymentIntentCreateParams.builder()
                .setAmount(amountInCents)
                .setCurrency(currency)
                .setAutomaticPaymentMethods(
                        PaymentIntentCreateParams.AutomaticPaymentMethods.builder()
                                .setEnabled(true)
                                .build())
                .build();
        return PaymentIntent.create(params);
    }

    // -----------------------------------------------------------------------
    // Subscriptions
    // -----------------------------------------------------------------------

    /**
     * Create a customer and subscribe them to a price.
     *
     * @param email   Customer e-mail address.
     * @param priceId Stripe Price ID.
     * @return Stripe {@link Subscription}.
     * @throws StripeException on API error.
     */
    public Subscription createSubscription(String email, String priceId)
            throws StripeException {
        CustomerCreateParams customerParams = CustomerCreateParams.builder()
                .setEmail(email)
                .build();
        Customer customer = Customer.create(customerParams);

        SubscriptionCreateParams subParams = SubscriptionCreateParams.builder()
                .setCustomer(customer.getId())
                .addItem(SubscriptionCreateParams.Item.builder()
                        .setPrice(priceId)
                        .build())
                .setPaymentBehavior(SubscriptionCreateParams.PaymentBehavior.DEFAULT_INCOMPLETE)
                .addAllExpand(Arrays.asList("latest_invoice.payment_intent"))
                .build();
        return Subscription.create(subParams);
    }

    /**
     * Cancel an existing subscription immediately.
     *
     * @param subscriptionId Stripe Subscription ID.
     * @return Cancelled {@link Subscription}.
     * @throws StripeException on API error.
     */
    public Subscription cancelSubscription(String subscriptionId) throws StripeException {
        Subscription subscription = Subscription.retrieve(subscriptionId);
        return subscription.cancel();
    }

    // -----------------------------------------------------------------------
    // Checkout Session
    // -----------------------------------------------------------------------

    /**
     * Create a Stripe Checkout Session.
     *
     * @param priceId    Stripe Price ID.
     * @param successUrl Redirect URL on success.
     * @param cancelUrl  Redirect URL on cancel.
     * @param mode       {@code "payment"} or {@code "subscription"}.
     * @return Stripe Checkout {@link Session}.
     * @throws StripeException on API error.
     */
    public Session createCheckoutSession(
            String priceId, String successUrl, String cancelUrl, String mode)
            throws StripeException {
        SessionCreateParams.Mode sessionMode = "subscription"
                .equalsIgnoreCase(mode)
                ? SessionCreateParams.Mode.SUBSCRIPTION
                : SessionCreateParams.Mode.PAYMENT;

        SessionCreateParams params = SessionCreateParams.builder()
                .addPaymentMethodType(SessionCreateParams.PaymentMethodType.CARD)
                .addLineItem(SessionCreateParams.LineItem.builder()
                        .setPrice(priceId)
                        .setQuantity(1L)
                        .build())
                .setMode(sessionMode)
                .setSuccessUrl(successUrl)
                .setCancelUrl(cancelUrl)
                .build();
        return Session.create(params);
    }

    // -----------------------------------------------------------------------
    // Webhook Handler (to be wired into your HTTP framework)
    // -----------------------------------------------------------------------

    /**
     * Parse and handle an incoming Stripe webhook event.
     *
     * @param payload   Raw request body bytes.
     * @param sigHeader Value of the {@code Stripe-Signature} header.
     */
    public void handleWebhookEvent(String payload, String sigHeader) {
        Event event;
        if (!WEBHOOK_SECRET.isEmpty()) {
            try {
                event = Webhook.constructEvent(payload, sigHeader, WEBHOOK_SECRET);
            } catch (SignatureVerificationException e) {
                System.err.println("Webhook signature verification failed: " + e.getMessage());
                return;
            }
        } else {
            // Fallback for local testing without a signing secret
            event = Event.GSON.fromJson(payload, Event.class);
        }

        System.out.println("Webhook event received: " + event.getType());
        switch (event.getType()) {
            case "payment_intent.succeeded":
                System.out.println("Payment succeeded: " +
                        event.getDataObjectDeserializer().getObject()
                                .map(o -> ((PaymentIntent) o).getId()).orElse("unknown"));
                break;
            case "checkout.session.completed":
                System.out.println("Checkout completed");
                break;
            case "customer.subscription.created":
                System.out.println("Subscription created");
                break;
            case "customer.subscription.deleted":
                System.out.println("Subscription canceled");
                break;
            default:
                System.out.println("Unhandled event type: " + event.getType());
        }
    }

    // -----------------------------------------------------------------------
    // Main (quick smoke-test)
    // -----------------------------------------------------------------------

    public static void main(String[] args) throws StripeException {
        StripeIntegration integration = new StripeIntegration();
        PaymentIntent pi = integration.createPaymentIntent(2500L, "usd");
        System.out.println("PaymentIntent created: " + pi.getId());
    }
}
