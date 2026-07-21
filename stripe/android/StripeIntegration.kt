// DreamCobots — Stripe Android (Kotlin) Integration
//
// Provides PaymentSheet integration for Android apps.
//
// Setup:
//   1. Add `implementation("com.stripe:stripe-android:20.+")` to app/build.gradle
//   2. Implement a backend endpoint that creates a PaymentIntent and
//      returns { clientSecret: "...", publishableKey: "..." }
//   3. Initialize PaymentSheet in your Activity or Fragment as shown below.

package com.dreamcobots.stripe

import android.os.Bundle
import android.util.Log
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.lifecycleScope
import com.stripe.android.PaymentConfiguration
import com.stripe.android.paymentsheet.PaymentSheet
import com.stripe.android.paymentsheet.PaymentSheetResult
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.net.URL

private const val TAG = "DreamCobotsStripe"
private const val BACKEND_URL = "https://your-backend.example.com"

// ---------------------------------------------------------------------------
// Main Activity
// ---------------------------------------------------------------------------

class MainActivity : ComponentActivity() {

    private lateinit var paymentSheet: PaymentSheet
    private var clientSecret: String? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        paymentSheet = PaymentSheet(this, ::onPaymentSheetResult)

        setContent {
            MaterialTheme {
                PaymentScreen(
                    onPrepare = { preparePayment(amountInCents = 2500, currency = "usd") },
                    onPay = { clientSecret?.let { presentPaymentSheet(it) } }
                )
            }
        }
    }

    // -----------------------------------------------------------------------
    // Fetch PaymentIntent from backend
    // -----------------------------------------------------------------------

    private fun preparePayment(amountInCents: Int, currency: String) {
        lifecycleScope.launch {
            val result = withContext(Dispatchers.IO) {
                runCatching {
                    val url = URL("$BACKEND_URL/create-payment-intent")
                    val connection = url.openConnection() as java.net.HttpURLConnection
                    connection.requestMethod = "POST"
                    connection.setRequestProperty("Content-Type", "application/json")
                    connection.doOutput = true

                    val body = """{"amount":$amountInCents,"currency":"$currency"}"""
                    connection.outputStream.use { it.write(body.toByteArray()) }

                    val response = connection.inputStream.bufferedReader().readText()
                    JSONObject(response)
                }
            }

            result.onSuccess { json ->
                val publishableKey = json.getString("publishableKey")
                clientSecret = json.getString("clientSecret")
                PaymentConfiguration.init(applicationContext, publishableKey)
                Log.d(TAG, "PaymentIntent prepared, client secret received")
            }.onFailure { error ->
                Log.e(TAG, "Failed to prepare payment: ${error.message}")
            }
        }
    }

    // -----------------------------------------------------------------------
    // Present PaymentSheet
    // -----------------------------------------------------------------------

    private fun presentPaymentSheet(secret: String) {
        val configuration = PaymentSheet.Configuration(
            merchantDisplayName = "DreamCobots",
            allowsDelayedPaymentMethods = true
        )
        paymentSheet.presentWithPaymentIntent(secret, configuration)
    }

    // -----------------------------------------------------------------------
    // Handle result
    // -----------------------------------------------------------------------

    private fun onPaymentSheetResult(result: PaymentSheetResult) {
        when (result) {
            is PaymentSheetResult.Completed -> Log.i(TAG, "Payment succeeded!")
            is PaymentSheetResult.Canceled -> Log.i(TAG, "Payment canceled by user")
            is PaymentSheetResult.Failed -> Log.e(TAG, "Payment failed: ${result.error.message}")
        }
    }
}

// ---------------------------------------------------------------------------
// Compose UI
// ---------------------------------------------------------------------------

@Composable
fun PaymentScreen(onPrepare: () -> Unit, onPay: () -> Unit) {
    var prepared by remember { mutableStateOf(false) }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text("DreamCobots Payment", style = MaterialTheme.typography.headlineSmall)
        Spacer(Modifier.height(24.dp))

        if (!prepared) {
            Button(onClick = {
                onPrepare()
                prepared = true
            }) {
                Text("Prepare Payment")
            }
        } else {
            Button(onClick = onPay) {
                Text("Pay Now")
            }
        }
    }
}
