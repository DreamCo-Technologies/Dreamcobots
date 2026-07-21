// DreamCobots — Stripe .NET Integration
//
// Provides Payment Intent creation, Checkout sessions, and webhook handling.
//
// Setup:
//   dotnet add package Stripe.net
//   export STRIPE_SECRET_KEY=sk_...
//   dotnet run
using System;
using System.IO;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.DependencyInjection;
using Stripe;
using Stripe.Checkout;

namespace DreamCobots.StripeIntegration
{
    /// <summary>
    /// DreamCobots Stripe helper — wraps common Stripe operations used by all bots.
    /// </summary>
    public class StripeService
    {
        private static readonly string WebhookSecret =
            Environment.GetEnvironmentVariable("STRIPE_WEBHOOK_SECRET") ?? string.Empty;

        static StripeService()
        {
            StripeConfiguration.ApiKey = Environment.GetEnvironmentVariable("STRIPE_SECRET_KEY") ?? string.Empty;
        }

        // -------------------------------------------------------------------
        // Payment Intent
        // -------------------------------------------------------------------

        /// <summary>Create a Stripe PaymentIntent for a one-time charge.</summary>
        public async Task<PaymentIntent> CreatePaymentIntentAsync(long amountInCents, string currency = "usd")
        {
            var options = new PaymentIntentCreateOptions
            {
                Amount = amountInCents,
                Currency = currency,
                AutomaticPaymentMethods = new PaymentIntentAutomaticPaymentMethodsOptions
                {
                    Enabled = true,
                },
            };
            var service = new PaymentIntentService();
            return await service.CreateAsync(options);
        }

        // -------------------------------------------------------------------
        // Subscription
        // -------------------------------------------------------------------

        /// <summary>Create a customer and subscribe them to a price.</summary>
        public async Task<Subscription> CreateSubscriptionAsync(string email, string priceId)
        {
            var customerOptions = new CustomerCreateOptions { Email = email };
            var customerService = new CustomerService();
            var customer = await customerService.CreateAsync(customerOptions);

            var subOptions = new SubscriptionCreateOptions
            {
                Customer = customer.Id,
                Items = new System.Collections.Generic.List<SubscriptionItemOptions>
                {
                    new SubscriptionItemOptions { Price = priceId },
                },
                PaymentBehavior = "default_incomplete",
            };
            subOptions.AddExpand("latest_invoice.payment_intent");

            var subService = new SubscriptionService();
            return await subService.CreateAsync(subOptions);
        }

        /// <summary>Cancel a subscription immediately.</summary>
        public async Task<Subscription> CancelSubscriptionAsync(string subscriptionId)
        {
            var service = new SubscriptionService();
            return await service.CancelAsync(subscriptionId);
        }

        // -------------------------------------------------------------------
        // Checkout Session
        // -------------------------------------------------------------------

        /// <summary>Create a Stripe Checkout Session.</summary>
        public async Task<Session> CreateCheckoutSessionAsync(
            string priceId, string successUrl, string cancelUrl, string mode = "subscription")
        {
            var options = new SessionCreateOptions
            {
                PaymentMethodTypes = new System.Collections.Generic.List<string> { "card" },
                LineItems = new System.Collections.Generic.List<SessionLineItemOptions>
                {
                    new SessionLineItemOptions { Price = priceId, Quantity = 1 },
                },
                Mode = mode,
                SuccessUrl = successUrl,
                CancelUrl = cancelUrl,
            };
            var service = new SessionService();
            return await service.CreateAsync(options);
        }

        // -------------------------------------------------------------------
        // Webhook Handler
        // -------------------------------------------------------------------

        /// <summary>Parse and handle an incoming Stripe webhook event.</summary>
        public static async Task HandleWebhookAsync(HttpContext context)
        {
            var json = await new StreamReader(context.Request.Body).ReadToEndAsync();
            var sigHeader = context.Request.Headers["Stripe-Signature"].ToString();

            Event stripeEvent;
            if (!string.IsNullOrEmpty(WebhookSecret))
            {
                try
                {
                    stripeEvent = EventUtility.ConstructEvent(json, sigHeader, WebhookSecret);
                }
                catch (StripeException ex)
                {
                    Console.WriteLine($"Webhook signature verification failed: {ex.Message}");
                    context.Response.StatusCode = 400;
                    return;
                }
            }
            else
            {
                stripeEvent = EventUtility.ParseEvent(json);
            }

            Console.WriteLine($"Webhook event received: {stripeEvent.Type}");

            switch (stripeEvent.Type)
            {
                case Events.PaymentIntentSucceeded:
                    var pi = stripeEvent.Data.Object as PaymentIntent;
                    Console.WriteLine($"Payment succeeded: {pi?.Id}");
                    break;
                case Events.CheckoutSessionCompleted:
                    var session = stripeEvent.Data.Object as Session;
                    Console.WriteLine($"Checkout completed: {session?.Id}");
                    break;
                case Events.CustomerSubscriptionCreated:
                    Console.WriteLine("Subscription created");
                    break;
                case Events.CustomerSubscriptionDeleted:
                    Console.WriteLine("Subscription canceled");
                    break;
                default:
                    Console.WriteLine($"Unhandled event type: {stripeEvent.Type}");
                    break;
            }

            context.Response.StatusCode = 200;
            await context.Response.WriteAsync("{\"received\": true}");
        }
    }

    // -----------------------------------------------------------------------
    // Minimal ASP.NET Core host
    // -----------------------------------------------------------------------

    public class Program
    {
        public static async Task Main(string[] args)
        {
            var builder = WebApplication.CreateBuilder(args);
            builder.Services.AddSingleton<StripeService>();

            var app = builder.Build();

            app.MapPost("/webhook", StripeService.HandleWebhookAsync);

            var port = Environment.GetEnvironmentVariable("PORT") ?? "5000";
            Console.WriteLine($"DreamCobots Stripe webhook listener running on port {port}");
            Console.WriteLine($"Test locally: stripe listen --forward-to localhost:{port}/webhook");

            await app.RunAsync($"http://0.0.0.0:{port}");
        }
    }
}
