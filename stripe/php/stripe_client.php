<?php
/**
 * Dreamcobots Stripe Integration — PHP
 *
 * Install: composer install
 * Configure .env (see ../../.env.example)
 */

require_once __DIR__ . '/vendor/autoload.php';

$dotenv = Dotenv\Dotenv::createImmutable(__DIR__);
$dotenv->safeLoad();

\Stripe\Stripe::setApiKey($_ENV['STRIPE_SECRET_KEY'] ?? '');

class DreamcobotsStripe
{
    /**
     * Create a Stripe Checkout session.
     */
    public static function createCheckoutSession(
        int $amountCents,
        string $currency,
        string $customerEmail,
        string $successUrl,
        string $cancelUrl,
        string $mode = 'payment'
    ): array {
        $session = \Stripe\Checkout\Session::create([
            'payment_method_types' => ['card'],
            'line_items' => [[
                'price_data' => [
                    'currency'     => strtolower($currency),
                    'product_data' => ['name' => 'Dreamcobots Service'],
                    'unit_amount'  => $amountCents,
                ],
                'quantity' => 1,
            ]],
            'mode'           => $mode,
            'customer_email' => $customerEmail,
            'success_url'    => $successUrl,
            'cancel_url'     => $cancelUrl,
        ]);

        return ['session_id' => $session->id, 'checkout_url' => $session->url];
    }

    /**
     * Create a shareable Payment Link.
     */
    public static function createPaymentLink(
        int $amountCents,
        string $currency,
        string $productName
    ): array {
        $price = \Stripe\Price::create([
            'unit_amount'  => $amountCents,
            'currency'     => strtolower($currency),
            'product_data' => ['name' => $productName],
        ]);
        $link = \Stripe\PaymentLink::create([
            'line_items' => [['price' => $price->id, 'quantity' => 1]],
        ]);
        return ['id' => $link->id, 'url' => $link->url];
    }
}

if (basename(__FILE__) === basename($_SERVER['PHP_SELF'] ?? '')) {
    $mode = !empty($_ENV['STRIPE_SECRET_KEY']) ? 'live' : 'simulation';
    echo "Dreamcobots Stripe PHP client initialised in {$mode} mode.\n";
}
