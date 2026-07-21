// Dreamcobots Stripe Integration — .NET (C#)
//
// Install: dotnet restore
// Configure .env (see ../../.env.example)
// Run:     dotnet run

using DotNetEnv;
using Stripe;
using Stripe.Checkout;

Env.Load("../../.env");

StripeConfiguration.ApiKey = Environment.GetEnvironmentVariable("STRIPE_SECRET_KEY") ?? string.Empty;

string mode = string.IsNullOrEmpty(StripeConfiguration.ApiKey) ? "simulation" : "live";
Console.WriteLine($"Dreamcobots Stripe .NET client initialised in {mode} mode.");

/// <summary>Creates a Stripe Checkout session for a one-time payment.</summary>
static async Task<Session> CreateCheckoutSessionAsync(
    long amountCents,
    string currency,
    string customerEmail,
    string successUrl,
    string cancelUrl)
{
    var options = new SessionCreateOptions
    {
        PaymentMethodTypes = new List<string> { "card" },
        LineItems = new List<SessionLineItemOptions>
        {
            new SessionLineItemOptions
            {
                PriceData = new SessionLineItemPriceDataOptions
                {
                    Currency = currency.ToLower(),
                    ProductData = new SessionLineItemPriceDataProductDataOptions
                    {
                        Name = "Dreamcobots Service"
                    },
                    UnitAmount = amountCents
                },
                Quantity = 1
            }
        },
        Mode = "payment",
        CustomerEmail = customerEmail,
        SuccessUrl = successUrl,
        CancelUrl = cancelUrl
    };
    var service = new SessionService();
    return await service.CreateAsync(options);
}

/// <summary>Creates a shareable Stripe Payment Link.</summary>
static async Task<PaymentLink> CreatePaymentLinkAsync(
    long amountCents,
    string currency,
    string productName)
{
    var priceOptions = new PriceCreateOptions
    {
        UnitAmount = amountCents,
        Currency = currency.ToLower(),
        ProductData = new PriceProductDataOptions { Name = productName }
    };
    var priceService = new PriceService();
    var price = await priceService.CreateAsync(priceOptions);

    var linkOptions = new PaymentLinkCreateOptions
    {
        LineItems = new List<PaymentLinkLineItemOptions>
        {
            new PaymentLinkLineItemOptions { Price = price.Id, Quantity = 1 }
        }
    };
    var linkService = new PaymentLinkService();
    return await linkService.CreateAsync(linkOptions);
}
