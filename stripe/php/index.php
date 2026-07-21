<?php
/**
 * DreamCobots — Stripe PHP Integration
 *
 * Provides Payment Intent creation, Checkout sessions, and webhook handling.
 *
 * Setup:
 *   composer require stripe/stripe-php
 *   export STRIPE_SECRET_KEY=sk_...
 *   php -S localhost:8000 index.php
 */

require_once __DIR__ . '/vendor/autoload.php';

use Stripe\Stripe;
use Stripe\PaymentIntent;
use Stripe\Checkout\Session;
use Stripe\Webhook;

Stripe::setApiKey(getenv('STRIPE_SECRET_KEY') ?: '');

$webhookSecret = getenv('STRIPE_WEBHOOK_SECRET') ?: '';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/**
 * Create a Payment Intent for a one-time charge.
 *
 * @param int    $amountInCents  Amount in smallest currency unit.
 * @param string $currency       ISO 4217 code (e.g. "usd").
 * @return \Stripe\PaymentIntent
 */
function createPaymentIntent(int $amountInCents, string $currency = 'usd'): \Stripe\PaymentIntent
{
    return PaymentIntent::create([
        'amount'                    => $amountInCents,
        'currency'                  => $currency,
        'automatic_payment_methods' => ['enabled' => true],
    ]);
}

/**
 * Create a Stripe Checkout Session.
 *
 * @param string $priceId     Stripe Price ID.
 * @param string $successUrl  Redirect URL on payment success.
 * @param string $cancelUrl   Redirect URL if the customer cancels.
 * @param string $mode        "payment" or "subscription".
 * @return \Stripe\Checkout\Session
 */
function createCheckoutSession(
    string $priceId,
    string $successUrl,
    string $cancelUrl,
    string $mode = 'subscription'
): \Stripe\Checkout\Session {
    return Session::create([
        'payment_method_types' => ['card'],
        'line_items'           => [['price' => $priceId, 'quantity' => 1]],
        'mode'                 => $mode,
        'success_url'          => $successUrl,
        'cancel_url'           => $cancelUrl,
    ]);
}

// ---------------------------------------------------------------------------
// Webhook Handler
// ---------------------------------------------------------------------------

$requestMethod = $_SERVER['REQUEST_METHOD'] ?? 'GET';
$requestUri    = $_SERVER['REQUEST_URI']    ?? '/';

if ($requestMethod === 'POST' && rtrim($requestUri, '/') === '/webhook') {
    $payload   = file_get_contents('php://input');
    $sigHeader = $_SERVER['HTTP_STRIPE_SIGNATURE'] ?? '';

    if ($webhookSecret !== '') {
        try {
            $event = Webhook::constructEvent($payload, $sigHeader, $webhookSecret);
        } catch (\Stripe\Exception\SignatureVerificationException $e) {
            http_response_code(400);
            echo json_encode(['error' => $e->getMessage()]);
            exit;
        }
    } else {
        $event = json_decode($payload);
    }

    $eventType = $event->type ?? '';
    error_log("Webhook event received: {$eventType}");

    switch ($eventType) {
        case 'payment_intent.succeeded':
            error_log("Payment succeeded: " . ($event->data->object->id ?? ''));
            break;
        case 'checkout.session.completed':
            error_log("Checkout completed: " . ($event->data->object->id ?? ''));
            break;
        case 'customer.subscription.created':
            error_log("Subscription created: " . ($event->data->object->id ?? ''));
            break;
        case 'customer.subscription.deleted':
            error_log("Subscription canceled: " . ($event->data->object->id ?? ''));
            break;
        default:
            error_log("Unhandled event type: {$eventType}");
    }

    http_response_code(200);
    header('Content-Type: application/json');
    echo json_encode(['received' => true]);
    exit;
}

// ---------------------------------------------------------------------------
// Quick smoke-test (GET /)
// ---------------------------------------------------------------------------

if ($requestMethod === 'GET') {
    echo '<h1>DreamCobots Stripe PHP Integration</h1>';
    echo '<p>Webhook endpoint: POST /webhook</p>';
}
