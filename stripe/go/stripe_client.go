// Dreamcobots Stripe Integration — Go
//
// Install: go mod tidy
// Configure env vars (see ../../.env.example)
//
// Usage:
//   export STRIPE_SECRET_KEY=sk_live_...
//   go run stripe_client.go

package main

import (
	"fmt"
	"os"

	"github.com/stripe/stripe-go/v76"
	"github.com/stripe/stripe-go/v76/checkout/session"
	"github.com/stripe/stripe-go/v76/paymentlink"
	"github.com/stripe/stripe-go/v76/price"
)

func init() {
	stripe.Key = os.Getenv("STRIPE_SECRET_KEY")
}

// CreateCheckoutSession creates a hosted Stripe checkout session.
func CreateCheckoutSession(amountCents int64, currency, customerEmail, successURL, cancelURL string) (*stripe.CheckoutSession, error) {
	params := &stripe.CheckoutSessionParams{
		PaymentMethodTypes: stripe.StringSlice([]string{"card"}),
		LineItems: []*stripe.CheckoutSessionLineItemParams{
			{
				PriceData: &stripe.CheckoutSessionLineItemPriceDataParams{
					Currency: stripe.String(currency),
					ProductData: &stripe.CheckoutSessionLineItemPriceDataProductDataParams{
						Name: stripe.String("Dreamcobots Service"),
					},
					UnitAmount: stripe.Int64(amountCents),
				},
				Quantity: stripe.Int64(1),
			},
		},
		Mode:          stripe.String(string(stripe.CheckoutSessionModePayment)),
		CustomerEmail: stripe.String(customerEmail),
		SuccessURL:    stripe.String(successURL),
		CancelURL:     stripe.String(cancelURL),
	}
	return session.New(params)
}

// CreatePaymentLink creates a shareable Stripe Payment Link.
func CreatePaymentLink(amountCents int64, currency, productName string) (*stripe.PaymentLink, error) {
	priceParams := &stripe.PriceParams{
		UnitAmount: stripe.Int64(amountCents),
		Currency:   stripe.String(currency),
		ProductData: &stripe.PriceProductDataParams{
			Name: stripe.String(productName),
		},
	}
	p, err := price.New(priceParams)
	if err != nil {
		return nil, err
	}
	linkParams := &stripe.PaymentLinkParams{
		LineItems: []*stripe.PaymentLinkLineItemParams{
			{Price: stripe.String(p.ID), Quantity: stripe.Int64(1)},
		},
	}
	return paymentlink.New(linkParams)
}

func main() {
	mode := "simulation"
	if os.Getenv("STRIPE_SECRET_KEY") != "" {
		mode = "live"
	}
	fmt.Printf("Dreamcobots Stripe Go client initialised in %s mode.\n", mode)
}
