# frozen_string_literal: true
# Dreamcobots Stripe Integration — Ruby
#
# Install: bundle install
# Configure .env (see ../../.env.example)

require "dotenv/load"
require "stripe"

Stripe.api_key = ENV.fetch("STRIPE_SECRET_KEY", "")

module DreamcobotsStripe
  # Create a checkout session for a one-time payment
  def self.create_checkout_session(amount_cents:, currency: "usd", customer_email:,
                                   success_url:, cancel_url:, mode: "payment")
    session = Stripe::Checkout::Session.create(
      payment_method_types: ["card"],
      line_items: [{
        price_data: {
          currency: currency.downcase,
          product_data: { name: "Dreamcobots Service" },
          unit_amount: amount_cents
        },
        quantity: 1
      }],
      mode: mode,
      customer_email: customer_email,
      success_url: success_url,
      cancel_url: cancel_url
    )
    { session_id: session.id, checkout_url: session.url }
  end

  # Create a shareable Payment Link
  def self.create_payment_link(amount_cents:, currency: "usd", product_name:)
    price = Stripe::Price.create(
      unit_amount: amount_cents,
      currency: currency.downcase,
      product_data: { name: product_name }
    )
    link = Stripe::PaymentLink.create(
      line_items: [{ price: price.id, quantity: 1 }]
    )
    { id: link.id, url: link.url }
  end

  # Create a subscription
  def self.create_subscription(customer_id:, price_id:)
    sub = Stripe::Subscription.create(
      customer: customer_id,
      items: [{ price: price_id }]
    )
    { id: sub.id, status: sub.status }
  end
end

if __FILE__ == $PROGRAM_NAME
  mode = ENV["STRIPE_SECRET_KEY"] ? "live" : "simulation"
  puts "Dreamcobots Stripe Ruby client initialised in #{mode} mode."
end
