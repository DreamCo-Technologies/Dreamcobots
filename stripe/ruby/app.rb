# frozen_string_literal: true

# DreamCobots — Stripe Ruby Integration
#
# Provides Checkout Session creation and webhook handling.
#
# Setup:
#   bundle install
#   export STRIPE_SECRET_KEY=sk_...
#   ruby app.rb

require 'stripe'
require 'sinatra'
require 'sinatra/json'
require 'json'

Stripe.api_key = ENV.fetch('STRIPE_SECRET_KEY', '')
STRIPE_WEBHOOK_SECRET = ENV.fetch('STRIPE_WEBHOOK_SECRET', '').freeze

# ---------------------------------------------------------------------------
# Checkout Session
# ---------------------------------------------------------------------------

# Create a Stripe Checkout Session.
#
# @param price_id [String]      Stripe Price ID.
# @param success_url [String]   Redirect URL on success.
# @param cancel_url [String]    Redirect URL on cancel.
# @param mode [String]          'payment' or 'subscription'.
# @return [Stripe::Checkout::Session]
def create_checkout_session(price_id:, success_url:, cancel_url:, mode: 'subscription')
  Stripe::Checkout::Session.create(
    payment_method_types: ['card'],
    line_items: [{ price: price_id, quantity: 1 }],
    mode: mode,
    success_url: success_url,
    cancel_url: cancel_url
  )
end

# ---------------------------------------------------------------------------
# Subscription helpers
# ---------------------------------------------------------------------------

def create_subscription(email, price_id)
  customer = Stripe::Customer.create(email: email)
  Stripe::Subscription.create(
    customer: customer.id,
    items: [{ price: price_id }],
    payment_behavior: 'default_incomplete',
    expand: ['latest_invoice.payment_intent']
  )
end

def cancel_subscription(subscription_id)
  Stripe::Subscription.cancel(subscription_id)
end

# ---------------------------------------------------------------------------
# Webhook Handler
# ---------------------------------------------------------------------------

post '/webhook' do
  payload = request.body.read
  sig_header = request.env['HTTP_STRIPE_SIGNATURE']

  event =
    if STRIPE_WEBHOOK_SECRET != ''
      begin
        Stripe::Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
      rescue Stripe::SignatureVerificationError => e
        halt 400, json(error: e.message)
      end
    else
      JSON.parse(payload, symbolize_names: true)
    end

  puts "Webhook event received: #{event[:type]}"

  case event[:type]
  when 'payment_intent.succeeded'
    puts "Payment succeeded: #{event.dig(:data, :object, :id)}"
  when 'checkout.session.completed'
    puts "Checkout completed: #{event.dig(:data, :object, :id)}"
  when 'customer.subscription.created'
    puts "Subscription created: #{event.dig(:data, :object, :id)}"
  when 'customer.subscription.deleted'
    puts "Subscription canceled: #{event.dig(:data, :object, :id)}"
  else
    puts "Unhandled event type: #{event[:type]}"
  end

  json received: true
end

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

port = ENV.fetch('PORT', 4567).to_i
set :port, port
puts "DreamCobots Stripe webhook listener running on port #{port}"
puts "Test locally: stripe listen --forward-to localhost:#{port}/webhook"
