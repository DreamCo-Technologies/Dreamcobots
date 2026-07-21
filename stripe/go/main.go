// DreamCobots — Stripe Go Integration
//
// Provides Payment Intent creation and webhook handling.
//
// Setup:
//   go get github.com/stripe/stripe-go/v76
//   export STRIPE_SECRET_KEY=sk_...
//   go run main.go
package main

import (
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"

	"github.com/stripe/stripe-go/v76"
	"github.com/stripe/stripe-go/v76/checkout/session"
	"github.com/stripe/stripe-go/v76/paymentintent"
	"github.com/stripe/stripe-go/v76/webhook"
)

func init() {
	stripe.Key = os.Getenv("STRIPE_SECRET_KEY")
}

// ---------------------------------------------------------------------------
// Payment Intent
// ---------------------------------------------------------------------------

// CreatePaymentIntent creates a Stripe PaymentIntent.
func CreatePaymentIntent(amountInCents int64, currency string) (*stripe.PaymentIntent, error) {
	params := &stripe.PaymentIntentParams{
		Amount:   stripe.Int64(amountInCents),
		Currency: stripe.String(currency),
	}
	params.AddExpand("payment_method")
	return paymentintent.New(params)
}

// ---------------------------------------------------------------------------
// Checkout Session
// ---------------------------------------------------------------------------

// CreateCheckoutSession creates a Stripe Checkout Session.
func CreateCheckoutSession(priceID, successURL, cancelURL, mode string) (*stripe.CheckoutSession, error) {
	params := &stripe.CheckoutSessionParams{
		PaymentMethodTypes: stripe.StringSlice([]string{"card"}),
		LineItems: []*stripe.CheckoutSessionLineItemParams{
			{Price: stripe.String(priceID), Quantity: stripe.Int64(1)},
		},
		Mode:       stripe.String(mode),
		SuccessURL: stripe.String(successURL),
		CancelURL:  stripe.String(cancelURL),
	}
	return session.New(params)
}

// ---------------------------------------------------------------------------
// Webhook Handler
// ---------------------------------------------------------------------------

func handleWebhook(w http.ResponseWriter, r *http.Request) {
	body, err := io.ReadAll(r.Body)
	if err != nil {
		http.Error(w, "Error reading body", http.StatusBadRequest)
		return
	}

	webhookSecret := os.Getenv("STRIPE_WEBHOOK_SECRET")
	var event stripe.Event

	if webhookSecret != "" {
		event, err = webhook.ConstructEvent(body, r.Header.Get("Stripe-Signature"), webhookSecret)
		if err != nil {
			log.Printf("Webhook signature verification failed: %v", err)
			http.Error(w, fmt.Sprintf("Webhook Error: %v", err), http.StatusBadRequest)
			return
		}
	} else {
		if err := json.Unmarshal(body, &event); err != nil {
			http.Error(w, "Error parsing body", http.StatusBadRequest)
			return
		}
	}

	log.Printf("Webhook event received: %s", event.Type)

	switch event.Type {
	case "payment_intent.succeeded":
		var pi stripe.PaymentIntent
		if err := json.Unmarshal(event.Data.Raw, &pi); err == nil {
			log.Printf("Payment succeeded: %s", pi.ID)
		}
	case "checkout.session.completed":
		var cs stripe.CheckoutSession
		if err := json.Unmarshal(event.Data.Raw, &cs); err == nil {
			log.Printf("Checkout completed: %s", cs.ID)
		}
	case "customer.subscription.created":
		log.Printf("Subscription created")
	case "customer.subscription.deleted":
		log.Printf("Subscription canceled")
	default:
		log.Printf("Unhandled event type: %s", event.Type)
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(map[string]bool{"received": true}) //nolint:errcheck
}

// ---------------------------------------------------------------------------
// Entry point
// ---------------------------------------------------------------------------

func main() {
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	http.HandleFunc("/webhook", handleWebhook)

	log.Printf("DreamCobots Stripe webhook listener running on port %s", port)
	log.Printf("Test locally: stripe listen --forward-to localhost:%s/webhook", port)
	log.Fatal(http.ListenAndServe(":"+port, nil))
}
